import pandas as pd
import streamlit as st
import libraries.neo4j_lib as neo4j_lib
import libraries.search_patterns as sp


# Cache the data to avoid fetching it every time there's a rerun
@st.cache_data(
    ttl=600
)  # Cache the result for 600 seconds (10 minutes) or adjust as needed
def fetch_group_data():
    neo4j_query = """MATCH (group:Group)
    RETURN group.country_id AS country_id,
    group.group_id AS group_id,
    group.name AS group_name,
    group.url AS group_url
    ORDER BY group_name;"""
    return pd.DataFrame(neo4j_lib.execute_neo4j_query(neo4j_query, {}))


# Load the group data into session state for persistence
if "groups" not in st.session_state:
    st.session_state["groups"] = fetch_group_data()

# Display the dataframe for context
st.dataframe(st.session_state["groups"])

# Dropdown to select a group
st.selectbox(
    "Select a group:", st.session_state["groups"]["group_name"], key="selected_group"
)

# Add a button to trigger the action
if st.button("Proceed with selected group"):
    if st.session_state["selected_group"] is not None:
        st.write(f"You selected the group: {st.session_state['selected_group']}")
        # Fetch the corresponding URL for the selected group
        selected_url = (
            st.session_state["groups"]
            .loc[
                st.session_state["groups"]["group_name"]
                == st.session_state["selected_group"],
                "group_url",
            ]
            .values[0]
        )
        st.session_state["group_adverts"] = pd.DataFrame(
            neo4j_lib.all_group_adverts(selected_url)
        )
        st.write(st.session_state["group_adverts"])
        # Display or execute the action
        st.write(f"Opening URL: {selected_url}")
        st.session_state["driver"].get(selected_url)  # Example action
        st.session_state["group_name"] = sp.find_group_name()
        st.write(f"Group name: {st.session_state['group_name']}")
