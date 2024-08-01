import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import Point
import geopandas as gpd
from libraries.google_lib import DB_Conn
import streamlit as st
from shapely.geometry import MultiPoint

curl = st.secrets["face_matcher"]["curl"]


query = """SELECT irfcommon.date_of_interception AS date_of_interception \
        ,irfcommon.irf_number AS irf_number \
        ,person.social_media AS social_media \
        ,person.role AS role \
        ,person.full_name AS full_name \
        ,person.nationality AS nationality \
        ,person.phone_contact AS phone_contact \
        ,person.address_notes AS adress_notes \
        ,person.guardian_name AS guardian_name \
        ,person.guardian_phone AS guardian_phone \
        ,person.address AS address \
        ,irfatt.description AS attachment_description \
        ,irfatt."option" AS attachment_option \
        ,irfatt.attachment AS attachment \
        ,country.name AS country \
        ,country.id AS operating_country_id \
        FROM public.dataentry_irfcommon irfcommon \
        INNER JOIN public.dataentry_intercepteecommon intercepteecommon ON intercepteecommon.interception_record_id = irfcommon.id \
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = irfcommon.station_id \
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id \
        INNER JOIN public.dataentry_person person ON person.id = intercepteecommon.person_id \
        INNER JOIN public.dataentry_irfattachmentcommon irfatt ON irfatt.interception_record_id = irfcommon.id \
        """

with DB_Conn() as db:
    person_details = db.ex_query(query)
person_details.sort_values("date_of_interception", inplace=True, ascending=False)
person_details = person_details[~person_details.isna()]
person_details["address"][0]


# Function to safely extract coordinates from the address column
def extract_coords(address_entry):
    if isinstance(address_entry, dict):
        location = address_entry.get("location", {})
        y = location.get("y")
        x = location.get("x")
        if y is not None and x is not None:
            try:
                return (float(y), float(x))
            except (ValueError, TypeError):
                pass
    return None


# Extract coordinates
person_details["coords"] = person_details["address"].apply(extract_coords)

# Remove rows with None coordinates
person_details = person_details.dropna(subset=["coords"])

# Create a GeoDataFrame, filtering out any invalid geometries
valid_geometries = []
valid_indices = []
f = person_details.country == "Uganda"
for idx, coords in person_details[f]["coords"].items():
    if coords is not None:
        try:
            valid_geometries.append(Point(coords))
            valid_indices.append(idx)
        except:
            pass
person_details.country.unique()
gdf = gpd.GeoDataFrame(
    person_details[f].loc[valid_indices], geometry=valid_geometries, crs="EPSG:4326"
)
coords_rad = np.radians(gdf["coords"].tolist())

# Perform DBSCAN clustering
epsilon = 1 / 6371.0  # 1 km radius, converted to radians
min_samples = 2  # Minimum number of points to form a cluster
dbscan = DBSCAN(eps=epsilon, min_samples=min_samples, metric="haversine", n_jobs=-1)
gdf["cluster"] = dbscan.fit_predict(coords_rad)


# Function to compute centroid of a cluster
def get_centroid(cluster_points):
    if len(cluster_points) == 1:
        return cluster_points[0]
    else:
        return MultiPoint(cluster_points).centroid


# Compute centroids for each cluster
cluster_centroids = gdf.groupby("cluster").apply(
    lambda x: get_centroid(x.geometry.tolist())
)

# Remove the centroid for noise points (cluster == -1) if it exists
if -1 in cluster_centroids.index:
    cluster_centroids = cluster_centroids.drop(-1)

# Print results
print("Cluster centroids:")
print(cluster_centroids)

print("\nNumber of clusters found:", len(cluster_centroids))
print("Number of noise points:", (gdf["cluster"] == -1).sum())


# If you want to get the addresses in each cluster
def safe_get_address(address_entry):
    if isinstance(address_entry, dict):
        return address_entry.get("address", "Unknown")
    else:
        return "Unknown"


addresses_by_cluster = (
    gdf[gdf["cluster"] != -1]
    .groupby("cluster")
    .apply(lambda x: x["address"].apply(safe_get_address).tolist())
)

print("\nAddresses by cluster:")
print(addresses_by_cluster)


# Define a function to compute the distance matrix
def compute_distance_matrix(points):
    return np.array(
        [[great_circle(p1, p2).kilometers for p2 in points] for p1 in points]
    )


# Compute the distance matrix
distances = compute_distance_matrix(gdf["coords"].tolist())

# Perform DBSCAN clustering
epsilon = 1  # 1 km radius
min_samples = 2  # Minimum number of points to form a cluster
dbscan = DBSCAN(eps=epsilon, min_samples=min_samples, metric="precomputed")
gdf["cluster"] = dbscan.fit_predict(distances)

# Now 'gdf' contains a new 'cluster' column with cluster labels
# -1 indicates noise points (not part of any cluster)

# You can now group by cluster if needed
clustered_data = gdf.groupby("cluster")

# Example: Get the centroid of each cluster
cluster_centroids = clustered_data.geometry.centroid

# Example: Get the addresses in each cluster
addresses_by_cluster = clustered_data["address"].agg(list)

# Print results
print(addresses_by_cluster)
print(cluster_centroids)
