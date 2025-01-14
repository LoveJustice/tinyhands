# Create base soc_df from db_sus after db_sus has gone through these steps:
# - db_sus = db_sus.dropna(subset=["suspect_arrested"])
# - Create 'arrested' column from suspect_arrested
# - Process role column
# - Merge with db_irf
# - Merge with suspect_evaluation_types
# - Drop duplicates
# - Add gender dummies (female, male, unknown_gender)
# - Fill age nulls with -99
#
# soc_df = db_sus.copy()
