import pandas as pd
import libraries.neo4j_lib as neo4j_lib

synthetic_ads_scored = pd.read_csv("results/synthetic_ads_scored.csv")

synthetic_ads_scored.head()

synthetic_ads_scored["IDn"]

for idx, row in synthetic_ads_scored.iterrows():
    print(row["Ad"])
    parameters = {"text": row["Ad"], "monitor_score": row["Scores"]}
    query = """MERGE (group:Group {name: 'SyntheticGroup', country_id: 1, 
    group_id: 'synthetic_group_id', 
    url:'https://www.synthetic.com/groups/synthetic'}) - [:HAS_POSTING] -> 
    (posting:Posting {text: $text, 
    monitor_score: $monitor_score})
    WITH posting
    SET posting:RecruitmentAdvert
    SET posting:SyntheticAdvert"""
    neo4j_lib.execute_neo4j_query(query, parameters)
