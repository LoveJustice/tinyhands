# entity_model.py
# author: christo strydom
import os
import logging
from datetime import datetime
import pandas as pd
from copy import deepcopy
import gspread_dataframe as gd
from .case_dispatcher_logging import setup_logger
import gspread


import pandas as pd
from copy import deepcopy

# from .case_dispatcher_logging import setup_logger


logger = setup_logger("entity_model_logging", "entity_logging")


class DataFrameValidator:
    @staticmethod
    def standardize_columns(df, base_columns=None):
        """
        Standardize DataFrame columns by removing duplicates and ensuring consistency
        """
        # Get unique column names while preserving order
        seen = set()
        unique_cols = []
        for col in df.columns:
            if col not in seen:
                seen.add(col)
                unique_cols.append(col)
            else:
                # If duplicate, append a unique suffix
                counter = 1
                while f"{col}_{counter}" in seen:
                    counter += 1
                unique_cols.append(f"{col}_{counter}")
                seen.add(f"{col}_{counter}")

        # Create new DataFrame with unique column names
        df_unique = df.copy()
        df_unique.columns = unique_cols

        # If base_columns provided, ensure all required columns exist
        if base_columns is not None:
            for col in base_columns:
                if col not in df_unique.columns:
                    df_unique[col] = pd.NA

        return df_unique

    @staticmethod
    def validate_required_columns(df, required_columns):
        """
        Validate that DataFrame has all required columns
        """
        missing_columns = [col for col in required_columns if col not in df.columns]
        return len(missing_columns) == 0, missing_columns

    @staticmethod
    def safe_concat(dfs, common_columns=None):
        """
        Safely concatenate DataFrames ensuring column consistency
        """
        if not dfs:
            return pd.DataFrame()

        # If common_columns not provided, use intersection of all DataFrame columns
        if common_columns is None:
            common_columns = set.intersection(*[set(df.columns) for df in dfs])

        # Standardize each DataFrame
        standardized_dfs = []
        for df in dfs:
            std_df = DataFrameValidator.standardize_columns(df[common_columns])
            standardized_dfs.append(std_df)

        # Concatenate standardized DataFrames
        return pd.concat(standardized_dfs, ignore_index=True)


class GetAttr:
    """
    This is a class which allows objects in its subclasses to be indexed.

    When an object in a subclass of GetAttr is indexed, this class will return the attribute of the object with the same name as the index.
    """

    def __getitem__(cls, x):
        """
        This method is called when the object is indexed.

        Args:
            x (str): The name of the attribute to retrieve.

        Returns:
            object: The attribute of the object with the same name as the index.
        """
        # Return the attribute of the object with the same name as the index
        return getattr(cls, x)


"""## The EntityGroup"""


class EntityGroup:
    sheets = []

    def __init__(self, uid, new_cases, active_gsheet, closed_gsheet, gsdfs):
        try:
            logger.info(f"Initializing EntityGroup with uid: {uid}")
            logger.debug(f"New cases columns: {new_cases.columns.tolist()}")
            logger.debug(
                f"Active gsheet columns: {gsdfs[active_gsheet].columns.tolist()}"
            )
            logger.debug(
                f"Closed gsheet columns: {gsdfs[closed_gsheet].columns.tolist()}"
            )

            EntityGroup.sheets.append(self)
            self.uid = uid
            self.new = new_cases
            self.gsheet = gsdfs[active_gsheet]
            self.closed = gsdfs[closed_gsheet]
            self.active_name = active_gsheet
            self.closed_name = closed_gsheet

            logger.info(f"Successfully initialized EntityGroup with uid: {uid}")
        except Exception as e:
            logger.error(f"Error initializing EntityGroup: {str(e)}", exc_info=True)
            raise

    @classmethod
    def merge_addresses(cls, addr):
        """Adds relevant address data to new entity groups."""
        addr = addr
        for sheet in cls.sheets:
            # sheet.new.infer_objects
            if "address1_id" in sheet.new:
                sheet.new["address1_id"] = (
                    sheet.new["address1_id"].fillna(0).astype(int)
                )
                sheet.new["address2_id"] = (
                    sheet.new["address2_id"].fillna(0).astype(int)
                )
                sheet.new = pd.merge(sheet.new, addr, how="left", on="address2_id")
                sheet.new["Address"] = (
                    sheet.new["address_2"].map(str) + ", " + sheet.new["address_1"]
                )

    @classmethod
    def subset_ocuntry(cls, scc_key, country):
        """Subset dataframe for a specific country."""
        for sheet in cls.sheets:
            sheet.new["station_code"] = sheet.new[sheet.uid].str[:3]
            sheet.new = pd.merge(sheet.new, scc_key, how="left", on="station_code")
            sheet.new = sheet.new[sheet.new.country_name == country]
            sheet.new = sheet.new.iloc[:, 0 : len(sheet.new.columns) - 2]
            sheet.new.drop_duplicates(subset=sheet.uid, inplace=True)

    @classmethod
    def set_case_id(cls):
        """Creates a Case ID from the form ID stored in the database."""
        for sheet in cls.sheets:
            sheet.new.loc[:, "case_id"] = sheet.new["case_id"].str.replace(".", "")
            sheet.new["case_id"] = sheet.new["case_id"].str[:-1]

    @classmethod
    def combine_sheets(cls):
        """
        Combines data from `sheet.new` and `sheet.gsheet` for each sheet in `cls.sheets`.

        This method performs the following steps for each sheet:
        1. Creates a deep copy of `sheet.new`.
        2. Reindexes the columns of the copied dataframe to include columns from both `sheet.new` and `sheet.gsheet`.
        3. Drops the first 7 columns of the copied dataframe.
        4. Concatenates the data from `sheet.gsheet` and the modified copy row-wise.
        5. Drops duplicate rows based on the `sheet.uid` column.
        6. Logs the columns of `sheet.new`, `sheet.gsheet`, and the modified copy.

        Parameters:
        - cls: Class instance containing the sheets to be processed.

        Returns:
        None
        Adds new cases to data already in the corresponding Google Sheet."""

        for sheet in cls.sheets:

            sheet.newcopy = deepcopy(sheet.new)

            sheet.newcopy = sheet.newcopy.reindex(
                columns=sheet.new.columns.tolist() + list(sheet.gsheet.columns)
            )

            sheet.newcopy = sheet.newcopy.iloc[:, 7 : len(sheet.newcopy.columns)]

            sheet.active = pd.concat([sheet.gsheet, sheet.newcopy], sort=False)
            sheet.active.drop_duplicates(subset=sheet.uid, inplace=True)

    @classmethod
    def move_closed(cls, soc_df):
        validator = DataFrameValidator()

        for sheet in cls.sheets:
            logger.info(f"Processing sheet: {sheet.active_name}")

            try:
                # Validate required columns
                required_columns = [sheet.uid, "case_status", "case_id"]
                for df_name, df in [
                    ("sheet.newcopy", sheet.newcopy),
                    ("soc_df", soc_df),
                    ("sheet.closed", sheet.closed),
                ]:
                    valid, missing = validator.validate_required_columns(
                        df, required_columns
                    )
                    if not valid:
                        logger.error(f"Missing columns in {df_name}: {missing}")
                        continue

                # Standardize all DataFrames before operations
                sheet.newcopy = validator.standardize_columns(sheet.newcopy)
                sheet.closed = validator.standardize_columns(sheet.closed)

                # Rest of your existing logic, but using safe_concat for concatenation
                prev_closed = sheet.newcopy[
                    sheet.newcopy[sheet.uid].isin(
                        soc_df[soc_df.arrested == 1][sheet.uid]
                    )
                ].copy()

                newly_closed = sheet.gsheet[
                    sheet.gsheet["case_status"].str.contains("Closed", na=False)
                ]

                # Safely concatenate all closed cases
                sheet.closed = validator.safe_concat(
                    [sheet.closed, prev_closed, newly_closed],
                    common_columns=sheet.closed.columns,
                )

                # Remove duplicates
                sheet.closed = sheet.closed.drop_duplicates(subset=sheet.uid)

                # Update active sheet
                sheet.active = sheet.active[
                    ~sheet.active[sheet.uid].isin(sheet.closed[sheet.uid])
                ]

                logger.info(f"Successfully processed sheet: {sheet.active_name}")

            except Exception as e:
                logger.error(f"Error processing sheet {sheet.active_name}: {str(e)}")
                raise

    @classmethod
    def move_closed_depr(cls, soc_df):
        """Moves closed cases to closed sheet for each Entity Group instance."""

        for sheet in cls.sheets:

            prev_closed = sheet.newcopy[
                sheet.newcopy[sheet.uid].isin(soc_df[soc_df.arrested == 1].suspect_id)
            ]
            prev_closed["Case_Status"] = "Closed: Already in Legal Cases Sheet"
            newly_closed = sheet.gsheet[sheet.gsheet["Date_Closed"].str.len() > 1]
            prev_closed = prev_closed[
                ~prev_closed[sheet.uid].isin(sheet.closed[sheet.uid])
            ]
            original_cols = list(prev_closed.columns)
            new_cols = [original_cols[i] + str(i) for i in range(len(original_cols))]
            sheet.closed.columns = new_cols
            prev_closed.columns = new_cols
            newly_closed.columns = new_cols
            sheet.closed = pd.concat([sheet.closed, prev_closed, newly_closed])
            sheet.closed.columns = original_cols
            sheet.closed.drop_duplicates(subset=sheet.uid, inplace=True)
            sheet.active = sheet.active[
                ~sheet.active[sheet.uid].isin(sheet.closed[sheet.uid])
            ]

    @classmethod
    def move_other_closed(cls, suspects, police, victims):
        """Moves cases closed in other Entity Groups to closed sheets."""
        closed_suspects = suspects.active[
            (suspects.active["suspect_id"].isin(police.closed["suspect_id"]))
            | (~suspects.active["case_id"].isin(victims.active["case_id"]))
        ]
        closed_police = police.active[
            (police.active["suspect_id"].isin(suspects.closed["suspect_id"]))
            | (~police.active["case_id"].isin(victims.active["case_id"]))
        ]
        closed_victims = victims.active[
            (~victims.active["case_id"].isin(police.active["case_id"]))
            | (~victims.active["case_id"].isin(suspects.active["case_id"]))
        ]
        orig_scols = list(suspects.closed.columns)
        new_scols = [orig_scols[i] + str(i) for i in range(len(orig_scols))]
        suspects.closed.columns = new_scols
        closed_suspects.columns = new_scols
        suspects.closed = pd.concat([suspects.closed, closed_suspects])
        suspects.closed.columns = orig_scols
        suspects.closed.drop_duplicates(subset="suspect_id")
        orig_pcols = list(police.closed.columns)
        new_pcols = [orig_pcols[i] + str(i) for i in range(len(orig_pcols))]
        police.closed.columns = new_pcols
        closed_police.columns = new_pcols
        police.closed = pd.concat([police.closed, closed_police])
        police.closed.columns = orig_pcols
        police.closed.drop_duplicates(subset="suspect_id")
        orig_vcols = list(victims.closed.columns)
        new_vcols = [orig_vcols[i] + str(i) for i in range(len(orig_vcols))]
        victims.closed.columns = new_vcols
        closed_victims.columns = new_vcols
        victims.closed = pd.concat([victims.closed, closed_victims])
        victims.closed.columns = orig_vcols
        victims.closed.drop_duplicates(subset="victim_id", inplace=True)

        for sheet in cls.sheets:
            sheet.active = sheet.active[
                ~sheet.active[sheet.uid].isin(sheet.closed[sheet.uid])
            ]
            sheet.closed = sheet.closed[sheet.closed["case_id"] != ""]
            sheet.closed = sheet.closed.loc[:, :"date_closed"]

    @classmethod
    def update_gsheets(cls, credentials, gs_name, active_cases):
        """Update Google Sheets with new data."""
        client = gspread.authorize(credentials)

        for sheet in cls.sheets:

            target_sheet = client.open(gs_name).worksheet(sheet.active_name)
            up_sheet = sheet.active.iloc[:, : len(sheet.active.columns) - 1]

            gd.set_with_dataframe(target_sheet, up_sheet)
            target_sheet = client.open(gs_name).worksheet(sheet.closed_name)
            gd.set_with_dataframe(target_sheet, sheet.closed)
        target_sheet = client.open(gs_name).worksheet("cases")
        up_sheet = active_cases.iloc[:, : len(active_cases.columns)]
        gd.set_with_dataframe(target_sheet, up_sheet)

    @classmethod
    def add_irf_notes(cls, irf_notes):
        """Update Google Sheets with new data."""
        for sheet in cls.sheets:

            sheet.active = pd.merge(
                sheet.active,
                irf_notes,
                how="left",
                left_on="case_id",
                right_on="irf_number",
            )
            sheet.active["irf_case_notes"] = sheet.active["case_notes"]
            sheet.active = sheet.active.loc[:, :"date_closed"]

    @classmethod
    def add_case_name_formula(cls):
        for sheet in cls.sheets:
            sheet.active.reset_index(inplace=True)
            sheet.active = sheet.active.drop(columns="index")
            for index, row in sheet.active.iterrows():
                sheet.active.at[index, "case_name"] = (
                    "=iferror(index(Cases!B:B,match(A{},Cases!A:A,0)),)".format(
                        index + 2
                    )
                )

    new_gsheets = []
