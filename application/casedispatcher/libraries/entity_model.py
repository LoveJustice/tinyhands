import pandas as pd
from copy import deepcopy
import gspread_dataframe as gd
from .case_dispatcher_logging import setup_logger
import gspread

logger = setup_logger("entity_model_logging", "entity_logging")


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


class EntityGroup(GetAttr):
    """This is a class for Victims, Suspects, and Police entity groups with
    corresponding sheets."""

    sheets = []

    def __init__(self, uid, new_cases, active_gsheet, closed_gsheet, gsdfs):
        logger.info(f"Initializing EntityGroup with uid: {uid}")
        try:
            EntityGroup.sheets.append(self)
            self.uid = uid
            self.new = new_cases
            self.gsheet = gsdfs[active_gsheet]
            self.closed = gsdfs[closed_gsheet]
            self.active_name = active_gsheet
            self.closed_name = closed_gsheet
            logger.info(f"Successfully initialized EntityGroup with uid: {uid}")
        except Exception as e:
            logger.error(
                f"Error while initializing EntityGroup: {str(e)}", exc_info=True
            )
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
            logger.info(f"1. combine_sheets: New Columns: {sheet.new.columns}")
            logger.info(f"2. combine_sheets: GSheet Columns: {sheet.gsheet.columns}")
            sheet.newcopy = deepcopy(sheet.new)
            logger.info(
                f"3. combine_sheets: NewCopy Columns BEFORE reindexing: {sheet.newcopy.columns}"
            )
            sheet.newcopy = sheet.newcopy.reindex(
                columns=sheet.new.columns.tolist() + list(sheet.gsheet.columns)
            )
            logger.info(
                f"4. combine_sheets: NewCopy Columns AFTER reindexing: {sheet.newcopy.columns}"
            )
            sheet.newcopy = sheet.newcopy.iloc[:, 7 : len(sheet.newcopy.columns)]
            logger.info(
                f"5. combine_sheets: NewCopy Columns AFTER sheet.newcopy = sheet.newcopy.iloc[:, 7 : len(sheet.newcopy.columns)]: {sheet.newcopy.columns}"
            )
            sheet.active = pd.concat([sheet.gsheet, sheet.newcopy], sort=False)
            sheet.active.drop_duplicates(subset=sheet.uid, inplace=True)
            # logger.info(f"New Columns: {sheet.new.columns}")
            # logger.info(f"GSheet Columns: {sheet.gsheet.columns}")
            logger.info(f"6. combine_sheets: NewCopy Columns: {sheet.newcopy.columns}")

    @classmethod
    def move_closed(cls, soc_df):
        """Moves closed cases to closed sheet for each Entity Group instance."""
        for sheet in cls.sheets:
            prev_closed = sheet.newcopy[
                sheet.newcopy[sheet.uid].isin(soc_df[soc_df.arrested == 1].suspect_id)
            ].copy()
            prev_closed.loc[:, "case_status"] = "Closed: Already in Legal Cases Sheet"

            newly_closed = sheet.gsheet[sheet.gsheet["date_closed"].str.len() > 1]
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
    def move_closed_depr(cls, soc_df):
        """Moves closed cases to closed sheet for each Entity Group instance."""

        for sheet in cls.sheets:
            logger.info(f"sheet.newcopy.columns = {sheet.newcopy.columns}")
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
        logger.info(f"active_cases.columns = {active_cases.columns}")
        for sheet in cls.sheets:
            logger.info(f"sheet.active_name = {sheet.active_name}")
            target_sheet = client.open(gs_name).worksheet(sheet.active_name)
            up_sheet = sheet.active.iloc[:, : len(sheet.active.columns) - 1]
            logger.info(f"up_sheet.columns = {up_sheet.columns}")
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
            logger.info(f"sheet.active_name = {sheet.active_name}")
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
                sheet.active.at[
                    index, "case_name"
                ] = "=iferror(index(Cases!B:B,match(A{},Cases!A:A,0)),)".format(
                    index + 2
                )

    new_gsheets = []
