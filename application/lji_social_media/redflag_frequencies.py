import pandas as pd
from collections import Counter
import libraries.neo4j_lib as nl


# Modify the output format for easy copying to Google Docs
def print_google_doc_format(df):
    # Create header line
    header = "Rank\tType\tCount\tPercentage\tCumulative %"
    print(header)

    # Create rows
    for idx, row in df.iterrows():
        formatted_row = (
            f"{idx}\t"
            f"{row['type']}\t"
            f"{row['count']}\t"
            f"{row['percentage']}%\t"
            f"{row['cumulative_percentage']}%"
        )
        print(formatted_row)


# Define the red flags
RED_FLAGS = [
    "assure_prompt",
    "bypass_prompt",
    "callback_request_prompt",
    "drop_off_at_secure_location_prompt",
    "false_organization_prompt",
    "gender_specific_prompt",
    "illegal_activities_prompt",
    "immediate_hiring_prompt",
    "language_switch_prompt",
    "multiple_provinces_prompt",
    "no_education_skilled_prompt",
    "no_location_prompt",
    "overseas_prompt",
    "quick_money_prompt",
    "recruit_students_prompt",
    "requires_references",
    "suspicious_email_prompt",
    "target_specific_group_prompt",
    "unprofessional_writing_prompt",
    "unrealistic_hiring_number_prompt",
    "unusual_hours_prompt",
    "vague_description_prompt",
]

# Modify your query to return the relationship type
query = """
MATCH (r:RecruitmentAdvert)-[ha:HAS_ANALYSIS]-(analysis:Analysis {result:'yes'})
WHERE r.monitor_score IS NOT NULL
RETURN ha.type as type
"""

# Execute query and get results
results = nl.execute_neo4j_query(query, {})  # Assuming you have this function

# Create a counter for all types
type_counts = Counter([record["type"] for record in results])

# Create a DataFrame with all red flags (including those with zero count)
df = pd.DataFrame(
    [{"type": flag, "count": type_counts.get(flag, 0)} for flag in RED_FLAGS]
)

# Sort by count in descending order
df = df.sort_values("count", ascending=False)

# Calculate percentage
total = df["count"].sum()
df["percentage"] = (df["count"] / total * 100).round(2)

# Add cumulative percentage
df["cumulative_percentage"] = df["percentage"].cumsum().round(2)

# Format the table
df_formatted = df.reset_index(drop=True)
df_formatted.index += 1  # Start index at 1 instead of 0

print("Red Flag Type Frequency Analysis")
print("-" * 80)
print(df_formatted.to_string())
print("-" * 80)
print(f"Total occurrences: {total}")

print_google_doc_format(df_formatted)

df_formatted.to_csv("results/red_flag_frequencies.csv", index=False)
# Create Excel file
df_formatted.to_excel(
    "red_flags_analysis.xlsx",
    index=True,
    index_label="Rank",
    columns=["type", "count", "percentage", "cumulative_percentage"],
)
