import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
from tqdm.auto import tqdm
from functools import partial
from typing import List, Tuple, Optional
from libraries.neo4j_lib import execute_neo4j_query


def is_valid_name(name):
    words = name.lower().split()
    return len(words) > 1 and len(set(words)) > 1


def match_names_rapidfuzz(
    name: str, people_names: List[str], threshold: int = 80
) -> Optional[str]:
    match = process.extractOne(
        name, people_names, scorer=fuzz.ratio, score_cutoff=threshold
    )
    return match[0] if match else None


def fetch_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    profiles = pd.DataFrame(
        execute_neo4j_query(
            "MATCH (p:Profile) RETURN p.name AS name, p.url AS url, ID(p) AS id", {}
        )
    )
    valid_names = pd.DataFrame(
        execute_neo4j_query(
            "MATCH (valid_name:ValidName) RETURN ID(valid_name) as id, valid_name.full_name AS full_name, valid_name.name AS name",
            {},
        )
    )
    return profiles, valid_names


def process_data(
    profiles: pd.DataFrame, valid_names: pd.DataFrame, threshold: int
) -> pd.DataFrame:
    # Filter profiles
    profiles = profiles[profiles["name"].apply(is_valid_name)]

    # Convert to numpy array for faster processing 'Nkosi Makuwa Thomas'
    # 'nkosi makuwa thomas'
    # match_names_rapidfuzz(
    #     "Nkosi Makuwa Thomas", valid_names["name"].to_numpy(), threshold=threshold
    # )
    people_names = valid_names["name"].to_numpy()

    # Vectorize the matching function
    vectorized_match = np.vectorize(
        partial(match_names_rapidfuzz, people_names=people_names, threshold=threshold)
    )

    # Apply the matching function with a progress bar
    tqdm.pandas(desc="Matching names")
    profiles["matched_searchlight_name"] = profiles["name"].progress_apply(
        vectorized_match
    )

    return profiles


def main():
    profiles, valid_names = fetch_data()
    result = process_data(profiles, valid_names, threshold=85)
    return result


if __name__ == "__main__":
    result = main()
    print(result.head())
    result[~result["matched_searchlight_name"].isna()]
