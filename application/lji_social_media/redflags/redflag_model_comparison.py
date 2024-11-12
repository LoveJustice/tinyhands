import pandas as pd
import libraries.model_tools as mt
from libraries.claude_prompts import RED_FLAGS as DATA_COLUMNS
import libraries.neo4j_lib as nl


# ============================================================================================
flag_query = """MATCH p=(group:Group)-[]-(posting:Posting)-[r:HAS_ANALYSIS]->(analysis:Analysis)
RETURN posting.text AS advert, ID(group) AS group_id, ID(posting) AS IDn,  r.type as flag, analysis.result as result """

# flags = execute_neo4j_query(flag_query, parameters={})

df = pd.DataFrame(nl.execute_neo4j_query(flag_query, parameters={}))
# df = df[["advert", "group_id", "IDn", "monitor_score", "flag"]+red_flags]
duplicates = df.duplicated(subset=["advert", "group_id", "IDn", "flag"], keep=False)
duplicate_rows = df[duplicates].sort_values(by=["advert", "group_id", "IDn", "flag"])
list(duplicate_rows["flag"].unique())
print("Duplicate rows:")
print(duplicate_rows)
# Perform the pivot operation with multiple index columns
flags = df.pivot(
    index=["advert", "group_id", "IDn"],
    columns="flag",
    values="result",
).reset_index()

flags = df.pivot_table(
    index=["advert", "group_id", "IDn", "monitor_score"],
    columns="flag",
    values="result",
    aggfunc="first",
).reset_index()


file_path = "data/adverts_round_2.csv"
adverts_round_2 = pd.read_csv(file_path)

model_path = "redflag_model_2024-11-05T09_03_15_91d8c8.pkl"
trained_pipeline = mt.load_model(model_path)

file_path = "results/advert_flags.csv"
advert_flags = pd.read_csv(file_path)
advert_flags.merge(adverts_round_2, on="IDn", how="inner")
prediction_flags = flags[flags.IDn.isin(adverts_round_2.IDn)]

# Make predictions on the entire dataset
prediction_flags.loc[:, "model_predictions"] = trained_pipeline.predict(
    prediction_flags[DATA_COLUMNS].replace({"yes": 1, "no": 0})
)

prediction_flags.to_csv("results/prediction_flags.csv", index=False)

adverts = pd.read_csv("data/adverts_scores_round2.csv")
list(adverts)
columns = [
    "IDn",
    "advert",
    "monitor_score",
    "monitor_rank",
    "model_score",
    "model_rank",
    "col0",
    "col1",
    "col3",
]
adverts.columns = columns

df = prediction_flags[
    ["advert", "group_id", "IDn", "model_predictions"] + DATA_COLUMNS
].merge(adverts[["IDn", "monitor_score"]], on="IDn", how="inner")
df.to_csv("results/prediction_flags.csv", index=False)
list(
    prediction_flags[["advert", "group_id", "IDn", "model_predictions"] + DATA_COLUMNS]
)
df[["monitor_score", "model_predictions"]]
df.model_predictions.nunique()
df["monitor_score"].nunique()
