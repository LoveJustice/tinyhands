from libraries.neo4j_lib import execute_neo4j_query
import pandas as pd
import datetime
import uuid

from redflags.Gradient_Boosting_Regressor_Training_and_Evaluation import file_path

datetime.datetime.now()


def generate_unique_filename(prefix="adverts_sample", extension="csv"):
    # Get current timestamp in ISO 8601 format
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")

    # Generate a short random string
    random_string = uuid.uuid4().hex[:6]

    # Combine components
    filename = f"{prefix}_{timestamp}_{random_string}.{extension}"

    return filename


query = """MATCH (g:Group)-[:HAS_POSTING]-(n:Posting) WHERE (g.country_id) = 1 AND (n.text IS NOT NULL) AND NOT (n.text = "") RETURN ID(n) AS IDn, n.post_id AS post_id, n.text AS advert"""
parameters = {}
adverts = pd.DataFrame(execute_neo4j_query(query, parameters))
file_path0 = "data/adverts_round_1.csv"
file_path1 = "results/advert_comparison_cleaned.csv"
file_path2 = "results/advert_100_comparison_with_regressor_predictions.csv"
adverts_20 = pd.read_csv(file_path0)
adverts_20 = pd.read_csv(file_path1)
advert_100 = pd.read_csv(file_path2)
file_path = "results/advert_flags.csv"
advert_existing = pd.read_csv(file_path).rename(columns={"post_id": "IDn"})
unique_filename = generate_unique_filename(prefix="adverts_sample", extension="csv")
adverts[~adverts["IDn"].isin(list(set(list(advert_existing["IDn"]))))].sample(
    100
).to_csv(f"results/{unique_filename}", index=False)
