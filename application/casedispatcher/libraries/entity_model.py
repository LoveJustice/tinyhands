import pandas as pd
from copy import deepcopy
import gspread_dataframe as gd
from .case_dispatcher_logging import setup_logger
import gspread
import pickle
from typing import Dict, List

logger = setup_logger("entity_model_logging", "entity_logging")

# logger = setup_logger("entity_model_logging", "entity_logging", level=logging.DEBUG)


def safe_concat(dataframes: List[pd.DataFrame], key: str) -> pd.DataFrame:
    """
    Safely concatenate a list of DataFrames after renaming columns to avoid collisions,
    and then restore the original column names. Duplicate rows based on a unique key are dropped.

    Parameters:
        dataframes (List[pd.DataFrame]): List of DataFrames to concatenate.
        key (str): The column name used as the unique identifier for deduplication.

    Returns:
        pd.DataFrame: A concatenated DataFrame with duplicates dropped.
    """
    if not dataframes:
        return pd.DataFrame()

    original_cols = list(dataframes[0].columns)
    temp_cols = [f"{col}_tmp" for col in original_cols]
    new_dfs = []
    for df in dataframes:
        df_copy = df.copy()
        df_copy.columns = temp_cols
        new_dfs.append(df_copy)
    concatenated = pd.concat(new_dfs, ignore_index=True)
    concatenated.columns = original_cols
    concatenated.drop_duplicates(subset=key, inplace=True)
    return concatenated


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


def for_each_sheet(func):
    """
    Decorator for class methods of EntityGroup that are meant to iterate over all
    registered sheets. The decorated function must have a signature like:

        def method(cls, sheet, *args, **kwargs):

    When the decorated method is called (without a sheet argument), the decorator
    will iterate over cls.sheets and call the function with (sheet, *args, **kwargs)
    for each sheet.

    Raises:
        Propagates any exception that occurs for a particular sheet.
    """

    def wrapper(cls, *args, **kwargs):
        for sheet in cls.sheets:
            try:
                # Call the original function passing the current sheet and any additional arguments.
                func(cls, sheet, *args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in sheet '{sheet.active_name}': {e}", exc_info=True
                )
                raise

    return wrapper


class EntityGroup:
    """
    A class for handling entity groups (such as victims, suspects, and police) with their corresponding sheets.

    Attributes:
        sheets (List[EntityGroup]): A class-level list containing all instances of EntityGroup.
        uid (str): The unique identifier column used by the entity group.
        new (pd.DataFrame): DataFrame containing new case data.
        gsheet (pd.DataFrame): DataFrame representing the active Google Sheet data.
        closed (pd.DataFrame): DataFrame representing the closed cases data.
        active_name (str): Name of the active cases sheet.
        closed_name (str): Name of the closed cases sheet.
    """

    sheets: List["EntityGroup"] = []

    def __init__(
        self,
        uid: str,
        new_cases: pd.DataFrame,
        active_gsheet: str,
        closed_gsheet: str,
        gsdfs: Dict,
    ):
        """
        Initialize an EntityGroup instance.

        Parameters:
            uid (str): The unique identifier for the entity group.
            new_cases (pd.DataFrame): DataFrame containing new case data.
            active_gsheet (str): Key for the active cases sheet in gsdfs.
            closed_gsheet (str): Key for the closed cases sheet in gsdfs.
            gsdfs (Dict): A dictionary mapping sheet names to DataFrame objects.

        Raises:
            Exception: If initialization fails.
        """
        logger.info(f"Initializing EntityGroup with uid: {uid}")
        try:
            self.uid = uid
            self.new = new_cases
            self.gsheet = gsdfs[active_gsheet]
            self.closed = gsdfs[closed_gsheet]
            self.active_name = active_gsheet
            self.closed_name = closed_gsheet
            EntityGroup.sheets.append(self)
            logger.info(f"Successfully initialized EntityGroup with uid: {uid}")
        except Exception as e:
            logger.error(f"Error while initializing EntityGroup: {e}", exc_info=True)
            raise

    @classmethod
    @for_each_sheet
    def merge_addresses(cls, sheet, addr: pd.DataFrame):
        """
        Merge address-related columns into the new cases DataFrame for a given sheet.

        This method:
            - Fills missing values in 'address1_id' and 'address2_id'
            - Merges the DataFrame with the provided address DataFrame on 'address2_id'
            - Creates a new "Address" column from the merged address components

        Parameters:
            sheet (EntityGroup): The current sheet (EntityGroup instance) to process.
            addr (pd.DataFrame): DataFrame containing address data.
        """
        if "address1_id" in sheet.new:
            sheet.new["address1_id"] = sheet.new["address1_id"].fillna(0).astype(int)
            sheet.new["address2_id"] = sheet.new["address2_id"].fillna(0).astype(int)
            sheet.new = pd.merge(sheet.new, addr, how="left", on="address2_id")
            sheet.new["Address"] = (
                sheet.new["address_2"].astype(str) + ", " + sheet.new["address_1"]
            )
            logger.debug(f"Merged addresses for sheet '{sheet.active_name}'.")

    @classmethod
    @for_each_sheet
    def subset_country(cls, sheet, scc_key: pd.DataFrame, country: str):
        """
        Filter the new cases DataFrame for a specific country.

        This method:
            - Derives a station code from the unique identifier.
            - Merges with the provided scc_key DataFrame to obtain country information.
            - Filters the DataFrame to only include rows matching the specified country.
            - Drops duplicate cases based on the unique identifier.

        Parameters:
            sheet (EntityGroup): The current sheet (EntityGroup instance) to process.
            scc_key (pd.DataFrame): DataFrame containing station code to country mappings.
            country (str): The target country for filtering.
        """
        sheet.new["station_code"] = sheet.new[sheet.uid].str[:3]
        sheet.new = pd.merge(sheet.new, scc_key, how="left", on="station_code")
        sheet.new = sheet.new[sheet.new.country_name == country]
        # Remove temporary columns if needed
        sheet.new = sheet.new.iloc[:, :-2]
        sheet.new.drop_duplicates(subset=sheet.uid, inplace=True)
        logger.debug(f"Subsetted country for sheet '{sheet.active_name}'.")

    @classmethod
    @for_each_sheet
    def set_case_id(cls, sheet):
        """
        Standardize the case_id format in the new cases DataFrame for a given sheet.
        This method removes periods from the 'case_id' values and truncates the last character.
        """
        sheet.new["case_id"] = sheet.new["case_id"].str.replace(".", "").str[:-1]
        logger.debug(f"Set case_id for sheet '{sheet.active_name}'.")

    @classmethod
    def combine_sheets(cls):
        """
        Combine the active Google Sheet data with the new cases data for all registered sheets.

        This method:
            - Creates a deep copy of each sheet's new cases DataFrame.
            - Reindexes the copy to include columns from both the new cases and active sheet.
            - Drops the first 7 columns of the reindexed copy.
            - Concatenates the active sheet data with this modified copy.
            - Drops duplicate rows based on the unique identifier.
        """
        for sheet in cls.sheets:
            sheet.newcopy = deepcopy(sheet.new)
            # Reindex columns to cover both new and gsheet data
            sheet.newcopy = sheet.newcopy.reindex(
                columns=sheet.new.columns.tolist() + list(sheet.gsheet.columns)
            )
            sheet.newcopy = sheet.newcopy.iloc[:, 7:]
            sheet.active = pd.concat([sheet.gsheet, sheet.newcopy], sort=False)
            sheet.active.drop_duplicates(subset=sheet.uid, inplace=True)
            logger.debug(f"Combined sheets for '{sheet.active_name}'.")

    @classmethod
    def move_closed(cls, soc_df: pd.DataFrame):
        """
        Update closed cases in each sheet based on data from a source DataFrame (soc_df).

        For each sheet:
            - Identify previously closed cases based on soc_df.
            - Update their 'case_status' to "Closed: Already in Legal Cases Sheet".
            - Identify newly closed cases from the active sheet data.
            - Normalize the date fields for newly closed cases.
            - Concatenate the new closed cases with existing closed cases (safely, to avoid column collisions).
            - Update the active cases by removing any cases now marked as closed.

        Parameters:
            soc_df (pd.DataFrame): DataFrame containing case data (including an 'arrested' flag
                                   and 'sf_number' used as the unique identifier).
        """
        for sheet in cls.sheets:
            logger.info(f"Processing sheet: {sheet.active_name} for closed cases")
            # Filter previously closed cases based on soc_df
            soc_closed_ids = soc_df.loc[soc_df.arrested == 1, "sf_number"]
            prev_closed = sheet.newcopy[
                sheet.newcopy[sheet.uid].isin(soc_closed_ids)
            ].copy()
            prev_closed["case_status"] = "Closed: Already in Legal Cases Sheet"
            logger.debug(f"Identified {len(prev_closed)} previously closed cases.")
            # Identify newly closed cases from the active gsheet
            newly_closed = sheet.gsheet[
                sheet.gsheet["case_status"].str.contains("Closed", na=False)
            ].copy()
            today = pd.Timestamp.today().normalize()
            newly_closed["date"] = today
            newly_closed["supervisor_review"] = today
            # Exclude duplicates from closed
            prev_closed = prev_closed[
                ~prev_closed[sheet.uid].isin(sheet.closed[sheet.uid])
            ]
            # Use helper to safely concatenate
            sheet.closed = safe_concat(
                [sheet.closed, prev_closed, newly_closed], key=sheet.uid
            )
            # Update active cases
            sheet.active = sheet.active[
                ~sheet.active[sheet.uid].isin(sheet.closed[sheet.uid])
            ]
            logger.info(f"Finished processing closed cases for '{sheet.active_name}'.")

    @classmethod
    def move_other_closed(
        cls, suspects: "EntityGroup", police: "EntityGroup", victims: "EntityGroup"
    ):
        """
        Cross-update closed cases among different entity groups (suspects, police, victims).

        This method:
            - Defines suspect, police, and victim cases to be closed based on cross-entity conditions.
            - Uses safe concatenation to update the corresponding closed cases DataFrame for each entity.
            - Updates the active cases by removing any cases which now appear in the closed cases.

        Parameters:
            suspects (EntityGroup): The suspects entity group.
            police (EntityGroup): The police entity group.
            victims (EntityGroup): The victims entity group.
        """
        # Define closures for suspects
        closed_suspects = suspects.active[
            (suspects.active["sf_number"].isin(police.closed["sf_number"]))
            | (~suspects.active["case_id"].isin(victims.active["case_id"]))
        ]
        closed_police = police.active[
            (police.active["sf_number"].isin(suspects.closed["sf_number"]))
            | (~police.active["case_id"].isin(victims.active["case_id"]))
        ]
        closed_victims = victims.active[
            (~victims.active["case_id"].isin(police.active["case_id"]))
            | (~victims.active["case_id"].isin(suspects.active["case_id"]))
        ]
        # Safe concatenation for each entity
        suspects.closed = safe_concat(
            [suspects.closed, closed_suspects], key="sf_number"
        )
        police.closed = safe_concat([police.closed, closed_police], key="sf_number")
        victims.closed = safe_concat([victims.closed, closed_victims], key="victim_id")

        # Update active cases for all sheets
        for sheet in cls.sheets:
            sheet.active = sheet.active[
                ~sheet.active[sheet.uid].isin(sheet.closed[sheet.uid])
            ]
            sheet.closed = sheet.closed[sheet.closed["case_id"] != ""]
            # Optionally limit columns, e.g., up to date_closed
            if "date_closed" in sheet.closed.columns:
                sheet.closed = sheet.closed.loc[:, :"date_closed"]

    @classmethod
    def update_gsheets(cls, credentials, gs_name: str, active_cases: pd.DataFrame):
        """
        Update Google Sheets with the current active and closed cases data.

        For each sheet in the EntityGroup:
            - Update the active cases worksheet.
            - Update the closed cases worksheet.
        Also updates a main cases sheet and saves the column names used in each sheet to a pickle file.

        Parameters:
            credentials: The credentials object to authorize with Google Sheets.
            gs_name (str): The name of the Google Sheets document.
            active_cases (pd.DataFrame): The main DataFrame to update the 'cases' worksheet.
        """
        import gspread
        from gspread_dataframe import set_with_dataframe  # assumed gd alias before

        client = gspread.authorize(credentials)
        sheet_columns_dict = {}

        for sheet in cls.sheets:
            # Update active cases
            target_sheet = client.open(gs_name).worksheet(sheet.active_name)
            up_sheet = sheet.active.iloc[:, :-1]
            sheet_columns_dict[sheet.active_name] = up_sheet.columns.tolist()
            set_with_dataframe(target_sheet, up_sheet)

            # Update closed sheet
            target_sheet = client.open(gs_name).worksheet(sheet.closed_name)
            sheet_columns_dict[sheet.closed_name] = sheet.closed.columns.tolist()
            set_with_dataframe(target_sheet, sheet.closed)

        # Update main cases sheet
        target_sheet = client.open(gs_name).worksheet("cases")
        up_sheet = active_cases.copy()
        sheet_columns_dict["cases"] = up_sheet.columns.tolist()
        set_with_dataframe(target_sheet, up_sheet)

        # Save the sheet columns dictionary
        import pickle

        with open("sheet_columns.pkl", "wb") as file:
            pickle.dump(sheet_columns_dict, file)
        logger.info("Sheet columns dictionary saved to sheet_columns.pkl")

    @classmethod
    @for_each_sheet
    def add_irf_notes(cls, sheet, irf_notes: pd.DataFrame):
        """
        Merge IRF notes into the active cases DataFrame for a given sheet.

        The merge is performed on 'case_id' from the active cases DataFrame and 'irf_number'
        from the provided IRF notes DataFrame. It then creates an 'irf_case_notes' column based
        on the merged 'case_notes'.

        Parameters:
            sheet (EntityGroup): The current sheet (EntityGroup instance) to process.
            irf_notes (pd.DataFrame): DataFrame containing IRF notes.
        """
        sheet.active = pd.merge(
            sheet.active,
            irf_notes,
            how="left",
            left_on="case_id",
            right_on="irf_number",
        )
        sheet.active["irf_case_notes"] = sheet.active["case_notes"]
        # Optionally trim columns
        if "date_closed" in sheet.active.columns:
            sheet.active = sheet.active.loc[:, :"date_closed"]
        logger.debug(f"Added IRF notes for sheet '{sheet.active_name}'.")

    @classmethod
    @for_each_sheet
    def add_case_name_formula(cls, sheet):
        """
        Add a formula column 'case_name' to the active cases DataFrame in a given sheet.

        For each row in the active cases DataFrame, a formula is inserted that references
        the 'Cases' sheet to retrieve a matching case name based on the cell in column A.

        Parameters:
            sheet (EntityGroup): The current sheet (EntityGroup instance) to process.
        """
        sheet.active.reset_index(drop=True, inplace=True)
        for index in sheet.active.index:
            sheet.active.at[index, "case_name"] = (
                f"=iferror(index(Cases!B:B,match(A{index + 2},Cases!A:A,0)),)"
            )
        logger.debug(f"Added case name formula to sheet '{sheet.active_name}'.")
