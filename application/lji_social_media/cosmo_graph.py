import pandas as pd


from libraries.neo4j_lib import execute_neo4j_query
from cosmograph import cosmo


points_query = """MATCH path = (startProfile:Profile)-[*]-(valid_name:ValidName)
WHERE
  ANY(node IN nodes(path) WHERE node:Person) AND
  ANY(node IN nodes(path) WHERE node:IRF) AND
  NONE(node IN nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
  AND id(startProfile) IN [466423,466098,626]
UNWIND nodes(path) AS node
WITH DISTINCT node
RETURN ID(node) AS id, node.name AS value, labels(node) AS label LIMIT 10;
"""

points = pd.DataFrame(execute_neo4j_query(points_query))

links_query = """MATCH path = (startProfile:Profile)-[*]-(valid_name:ValidName)
WHERE
  ANY(node IN nodes(path) WHERE node:Person) AND
  ANY(node IN nodes(path) WHERE node:IRF) AND
  NONE(node IN nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
  AND ID(startProfile) IN [466423,466098,626]
UNWIND relationships(path) AS rel
WITH DISTINCT rel
RETURN ID(startNode(rel)) AS source, ID(endNode(rel)) AS target LIMIT 10;"""

links = pd.DataFrame(execute_neo4j_query(links_query))

widget = cosmo(
    points=points,
    links=links,
    point_id_by="id",
    point_label_by="label",
    link_source_by="source",
    link_target_by="target",
    point_color_by="label",
    point_include_columns=["value"],
)
widget
