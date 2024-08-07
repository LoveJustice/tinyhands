from libraries.neo4j_lib import execute_neo4j_query
import pandas as pd
import datetime
import uuid

datetime.datetime.now()


def generate_unique_filename(prefix="adverts_sample", extension="csv"):
    # Get current timestamp in ISO 8601 format
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Generate a short random string
    random_string = uuid.uuid4().hex[:6]

    # Combine components
    filename = f"{prefix}_{timestamp}_{random_string}.{extension}"

    return filename


query = """MATCH (g:Group)-[:HAS_POSTING]-(n:Posting) WHERE (g.country_id) = 1 AND (n.text IS NOT NULL) AND NOT (n.text = "") RETURN ID(n) AS IDn, n.text AS advert"""
parameters = {}
adverts = pd.DataFrame(execute_neo4j_query(query, parameters))

file_path1 = "results/advert_comparison_cleaned.csv"
file_path2 = "results/advert_100_comparison_with_regressor_predictions.csv"
adverts_20 = pd.read_csv(file_path1)
advert_100 = pd.read_csv(file_path2)

unique_filename = generate_unique_filename(prefix="adverts_sample", extension="csv")
adverts[
    ~adverts["IDn"].isin(list(set(list(adverts_20["IDn"]) + list(advert_100["IDn"]))))
].sample(50).to_csv(f"results/adverts_za_{unique_filename}.csv", index=False)
