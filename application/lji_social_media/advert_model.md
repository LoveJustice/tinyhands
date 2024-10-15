## The advert model
### workflow:

Adverts were originally scraped from Facebook Groups and ingested as Posting nodes in Neo4J.

The text content of each advert was analyzed by prompting an LLM with 22 queries.  This analysis produced the presence of 'redflags' in the advert.

The result is downloaded a table in csv format.  Each redflag is a column, and each row is an advert.  This csv sent scored to the monitors for scoring and each monitor_score is uploaded to the corresponding Posting node in Neo4J.
The table with flags and monitor scores are now used to train a model.  The model is trained on the flags to predict the monitor_score.

New adverts are scraped and ingested and analyzed to create corresponding flags.  Using the model of the previous iteration, new scores are predicted.  The new adverts are also sent to the monitors for a monitor_score.  The quality of the model is now assessed by comparing the monitor_score to the predicted_score.  The process is now ready to be repeated.

What is expected is that that a chosen metric will show continuous improvement with more iterations.

Predicted scores never get uploaded to the neo4j db.

The model gets save in a pkl file.
