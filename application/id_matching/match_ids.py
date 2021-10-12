"""
Main module for matching IDs.
"""

import pandas as pd
import numpy as np
import pickle
import recordlinkage

import link_records as lnk
import predict_matches as pm
import pre_proc as pp

pd.options.mode.chained_assignment = None

db_cred = '/data/id_matching/database.ini'
#db_cred = 'database.ini'

print('-- Start --')
slp = pp.get_and_pre_process_all(db_cred)
print('-- Pre-processed all --')
#match_can = lnk.get_random_one_match_can(slp, country='Nepal')
#match_can = 30492
match_can = lnk.get_match_can_for_single(36373, slp)

match_can_df = lnk.eval_match_can(match_can, slp)
match_can_df = lnk.adjust_scores(match_can_df, 'Phone', 0.6)

print('-- Evaluated Scores --')

lr = pm.load_classifier('/data/id_matching/lr_all.pkl')
#lr = pm.load_classifier("lr2.pkl")

match_can_p = pm.get_predictions(match_can_df, lr)


print('-- Got Predictions --')

print('-- Top Matches --')
possible_matches = pm.get_top_matches(match_can_p, slp)
print(possible_matches)