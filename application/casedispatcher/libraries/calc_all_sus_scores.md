
---

# Custom Function Docstrings

## 0. `calc_vics_willing_scores`

```python
"""
Calculate and assign victim willingness multipliers to suspects.

This function computes a multiplier based on the number of victims willing to testify for each suspect case.
The multiplier reflects the strength or reliability of the case, enhancing the suspect's profile accordingly.
It merges the `suspects` DataFrame with the `vics_willing` DataFrame on the `case_id`, applies the
multiplier based on predefined rules, and adds a new column `v_mult` to the suspects DataFrame.

Parameters:
    suspects (pd.DataFrame):
        DataFrame containing suspect information. Must include a `case_id` column to identify each case.

    vics_willing (pd.DataFrame):
        DataFrame containing victim willingness data. Must include:
            - `case_id`: Identifier to merge with the suspects DataFrame.
            - `count`: Integer representing the number of victims willing to testify.

Returns:
    pd.DataFrame:
        The updated suspects DataFrame with an additional `v_mult` column representing the victim willingness multiplier.
        If `vics_willing` is empty, `v_mult` is set to 0.0 for all suspects.

Multiplier Calculation:
    The multiplier (`v_mult`) is determined based on the number of willing victims (`count`) as follows:
        count | v_mult
        ------|-------
          0   | 0.0
          1   | 0.5
          2   | 0.75
          3   | 0.875
          4   | 0.9375
          5   | 0.96875
          6   | 0.984375
          7+  | 1.0

Notes:
    - The function uses a predefined incremental approach to calculate multipliers for counts between 2 and 6.
    - Columns `willing_to_testify` and `count` are removed from the final suspects DataFrame after processing.
    - Ensure that the input DataFrames have the required columns to avoid merge issues.
"""
```

---

## 1. `calc_arrest_scores`

```python
"""
Calculate scores based on the number of other suspects arrested in each case,
and create fields for 'bio_known' and for police willingness to arrest.

This function performs the following operations:
    1. Sets the 'bio_known' flag based on the 'case_status' of each suspect.
    2. Calculates the total number of arrests in each case and merges this data into the suspects DataFrame.
    3. Determines police willingness to arrest based on their 'case_status' and merges this information into the suspects DataFrame.

Parameters:
    suspects (pd.DataFrame):
        DataFrame containing suspect information. Must include:
            - `case_id`: Identifier for each case.
            - `case_status`: Status of the case.

    states_of_charge (pd.DataFrame):
        DataFrame containing state of charge information. Must include:
            - `sf_number_group`: Group identifier (used in `get_total_arrests`).
            - `arrested`: Indicator if arrested.
            - `case_id`: Identifier to merge with suspects.

    police (pd.DataFrame):
        DataFrame containing police information. Must include:
            - `case_id`: Identifier to merge with suspects.
            - `case_status`: Status indicating willingness to arrest.

Returns:
    pd.DataFrame:
        The updated suspects DataFrame with additional columns:
            - `bio_known`: Binary indicator (1 if bio is known, else 0).
            - `others_arrested`: Total number of other arrests in the case.
            - `willing_to_arrest`: Binary indicator (1 if police are willing to arrest, else 0).

Raises:
    RuntimeError:
        If any step in the calculation process fails due to missing columns or other issues.
"""
```

---

## 2. `calc_recency_scores`

```python
"""
Assign a recency score to each suspect based on the number of days since their interview.

The recency score is higher for more recent interviews and decreases as the number of days since the interview increases.
The score is calculated using the formula:
    recency_score = max(1 - discount_coef * (days_old ** discount_exp), 0)

This function performs the following operations:
    1. Calculates the number of days since each suspect's interview.
    2. Merges this information into the suspects DataFrame.
    3. Computes the recency score using provided weights.
    4. Removes duplicate suspect entries based on 'suspect_id'.

Parameters:
    suspects (pd.DataFrame):
        DataFrame containing suspect information. Must include:
            - `case_id`: Identifier for each case.
            - `suspect_id`: Unique identifier for each suspect.

    states_of_charge (pd.DataFrame):
        DataFrame containing state of charge information. Must include:
            - `sf_number`: Group identifier used to derive `case_id`.
            - `interview_date`: Date of the suspect's interview.

    weights (pd.DataFrame):
        DataFrame containing weight parameters for score calculation. Must include:
            - `discount_coef`: Coefficient used in the recency score formula.
            - `discount_exp`: Exponent used in the recency score formula.

Returns:
    pd.DataFrame:
        The updated suspects DataFrame with an additional `recency_score` column.

Raises:
    RuntimeError:
        If any step in the calculation process fails due to missing columns or other issues.
"""
```

---

## 3. `weight_pv_believes`

```python
"""
Weight beliefs about suspects' involvement in trafficking.

This function calculates a "pv_believes" score for each suspect based on various indicators
of their involvement in trafficking. The score is determined by evaluating multiple belief
indicators and applying corresponding weights.

The function performs the following operations:
    1. Extracts relevant columns from the `states_of_charge` DataFrame.
    2. Computes the "pv_believes" score using the provided weights.
    3. Processes and derives the `case_id` from `sf_number`.
    4. Cleans and finalizes the data by selecting necessary columns and removing duplicates.
    5. Merges the computed "pv_believes" score into the `suspects` DataFrame.

Parameters:
    suspects (pd.DataFrame):
        DataFrame containing suspect information. Must include:
            - `case_id`: Identifier for each case.
            - `suspect_id`: Unique identifier for each suspect.

    states_of_charge (pd.DataFrame):
        DataFrame containing state of charge information. Must include:
            - `sf_number`: Group identifier used to derive `case_id`.
            - `pv_believes_definitely_trafficked_many`: Indicator of definite trafficking beliefs.
            - `pv_believes_trafficked_some`: Indicator of some trafficking beliefs.
            - `pv_believes_suspect_trafficker`: Indicator of suspect being a trafficker.

    pv_believes (pd.DataFrame):
        DataFrame containing weight values for each belief indicator. Must include:
            - `pv_believes_definitely_trafficked_many`: Weight for definite trafficking beliefs.
            - `pv_believes_trafficked_some`: Weight for some trafficking beliefs.
            - `pv_believes_suspect_trafficker`: Weight for suspect being a trafficker.

Returns:
    pd.DataFrame:
        The updated suspects DataFrame with an additional `pv_believes` column.

Raises:
    RuntimeError:
        If any step in the calculation process fails due to missing columns or other issues.
"""
```

---

## 4. `get_exp_score`

```python
"""
Calculate exploitation score based on parameters and reported exploitation.

This function computes an "exp" (exploitation) score for each suspect based on various exploitation indicators.
The score is calculated by applying weights to different exploitation factors, reflecting the level of exploitation
associated with each suspect.

The function performs the following operations:
    1. Extracts relevant exploitation-related columns from the `states_of_charges` DataFrame.
    2. Computes the "exp" score using provided weights for each exploitation indicator.
    3. Processes and derives the `case_id` from `sf_number`.
    4. Cleans and finalizes the data by selecting necessary columns and removing duplicates.
    5. Merges the computed "exp" score into the `suspects` DataFrame.

Parameters:
    suspects (pd.DataFrame):
        DataFrame containing suspect information. Must include:
            - `case_id`: Identifier for each case.
            - `suspect_id`: Unique identifier for each suspect.

    states_of_charges (pd.DataFrame):
        DataFrame containing state of charge information. Must include:
            - `sf_number`: Group identifier used to derive `case_id`.
            - Various exploitation indicator columns containing boolean values (e.g.,
              `pv_believes_definitely_trafficked_many`, `pv_believes_trafficked_some`, etc.).

    exploitation_type (Dict[str, float]):
        Dictionary containing weight values for each exploitation indicator. The keys should correspond
        to the exploitation indicator column names in `states_of_charges`, and the values are the weights
        to be applied.

Returns:
    pd.DataFrame:
        The updated suspects DataFrame with an additional `exp` column representing the exploitation score.

Raises:
    RuntimeError:
        If any step in the calculation process fails due to missing columns or other issues.
"""
```

---

## 5. `get_new_soc_score`

```python
"""
Merge newly calculated Strength of Case (SOC) scores into the suspects DataFrame.

This function performs the following operations:
    1. Validates the presence of required columns in the input DataFrames.
    2. Selects the necessary columns from the `states_of_charges` DataFrame.
    3. Merges the SOC scores into the `suspects` DataFrame based on `suspect_id`.
    4. Rounds the SOC scores to six decimal places.

Parameters:
    suspects (pd.DataFrame):
        DataFrame containing suspect information. Must include:
            - `suspect_id`: Unique identifier for each suspect.

    states_of_charges (pd.DataFrame):
        DataFrame containing state of charge information. Must include:
            - `suspect_id`: Unique identifier for each suspect.
            - `soc`: Strength of Case score.

Returns:
    pd.DataFrame:
        The updated suspects DataFrame with an additional `strength_of_case` column.

Raises:
    RuntimeError:
        If any step in the merging process fails due to missing columns or other issues.
"""
```

---

## 6. `get_eminence_score`

```python
"""
Assign an eminence score to each suspect based on existing data, defaulting to '1' where necessary.

This function performs the following operations:
    1. Assigns a default eminence score of '1' where the 'eminence' field is missing or empty.
    2. Converts the 'em2' field to a float type.
    3. If a 'net_weight' column exists, adds its value to the 'em2' score, caps the score at '9',
       and fills any resulting missing values with '0'.
    4. Cleans up by removing the 'net_weight' column if it was used.

Parameters:
    suspects (pd.DataFrame):
        DataFrame containing suspect information. Must include:
            - `suspect_id`: Unique identifier for each suspect.
            - `eminence`: Current eminence score (can be missing or empty).

Returns:
    pd.DataFrame:
        The updated suspects DataFrame with an additional `em2` column representing the processed eminence score.

Raises:
    RuntimeError:
        If any step in the processing fails due to missing columns or other issues.
"""
```

---

## 7. `calc_solvability`

```python
"""
Calculate a weighted solvability score for each active suspect.

The solvability score is a composite metric derived from multiple factors related to the strength and
progress of a case. Each factor is weighted according to predefined coefficients to reflect its
importance in determining the overall solvability of the case.

The function performs the following operations:
    1. Validates the presence of required columns in the input DataFrames.
    2. Computes weighted scores for each factor based on the provided weights.
    3. Aggregates the weighted scores to compute the final solvability score.
    4. Handles any missing values and ensures data consistency.

Parameters:
    suspects (pd.DataFrame):
        DataFrame containing suspect information. Must include the following columns:
            - `v_mult`: Multiplier based on victims' willingness to testify.
            - `bio_known`: Indicator if bio and location of suspect are known.
            - `others_arrested`: Number of other suspects arrested in the case.
            - `willing_to_arrest`: Indicator if police are willing to arrest.
            - `recency_score`: Score representing the recency of the case.
            - `pv_believes`: Belief score regarding suspects' involvement.
            - `exp`: Exploitation score based on reported exploitation.
            - `suspect_id`: Unique identifier for each suspect.

    weights (pd.DataFrame):
        DataFrame containing weight parameters for each factor. Must include the following columns:
            - `victim_willing_to_testify`: Weight for `v_mult`.
            - `bio_and_location_of_suspect`: Weight for `bio_known`.
            - `other_suspect(s)_arrested`: Weight for `others_arrested`.
            - `police_willing_to_arrest`: Weight for `willing_to_arrest`.
            - `recency_of_case`: Weight for `recency_score`.
            - `pv_believes`: Weight for `pv_believes`.
            - `exploitation_reported`: Weight for `exp`.

Returns:
    pd.DataFrame:
        The updated suspects DataFrame with an additional `solvability` column representing the weighted solvability score.

Raises:
    RuntimeError:
        If any step in the calculation process fails due to missing columns or other issues.
"""
```

---

## 8. `calc_priority`

```python
"""
Calculate a weighted priority score for each active suspect and update the suspects DataFrame accordingly.

The priority score is a composite metric derived from multiple factors such as solvability, strength of case,
and eminence. Each factor is weighted according to predefined coefficients to reflect its importance in
determining the overall priority of the suspect.

The function performs the following operations:
    1. Validates the presence of required columns in the input DataFrames.
    2. Computes weighted scores for each factor based on the provided weights.
    3. Aggregates the weighted scores to compute the final priority score.
    4. Handles any missing values and ensures data consistency.
    5. Sorts the suspects based on the priority score in descending order.
    6. Aligns the columns of the updated suspects DataFrame with the existing suspects DataFrame.
    7. Removes duplicate entries based on 'suspect_id'.

Parameters:
    new_suspects (pd.DataFrame):
        DataFrame containing updated suspect information. Must include:
            - `suspect_id`: Unique identifier for each suspect.
            - `solvability`: Solvability score of the case.
            - `strength_of_case`: Strength of the case score.
            - `em2`: Eminence score.

    weights (pd.DataFrame):
        DataFrame containing weight parameters for each factor. Must include:
            - `solvability`: Weight for the `solvability` factor.
            - `strength_of_case`: Weight for the `strength_of_case` factor.
            - `eminence`: Weight for the `em2` (eminence) factor.

    existing_suspects (pd.DataFrame):
        DataFrame containing the original suspect information. Used to align columns in the updated suspects DataFrame.

Returns:
    pd.DataFrame:
        The updated suspects DataFrame with an additional `priority` column representing the weighted priority score,
        sorted in descending order of priority.

Raises:
    RuntimeError:
        If any step in the calculation process fails due to missing columns or other issues.
"""
```

---

# Summary

The above Markdown document compiles the docstrings for the following custom functions from the`data_prep.py` script:

1. **`calc_vics_willing_scores`**
2. **`calc_arrest_scores`**
3. **`calc_recency_scores`**
4. **`weight_pv_believes`**
5. **`get_exp_score`**
6. **`get_new_soc_score`**
7. **`get_eminence_score`**
8. **`calc_solvability`**
9. **`calc_priority`**

Each section provides a detailed description of the function's purpose, parameters, return values, and potential exceptions, facilitating better understanding and maintainability of your codebase.
