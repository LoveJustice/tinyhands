"""
Module for training algorithm on existing match data and evaluating results.
"""

import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import datetime
from time import time
import seaborn as sns
import matplotlib.pyplot as plt
import pickle
import re
import recordlinkage

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.metrics import confusion_matrix

import sl_id_match.link_records as lnk
import sl_id_match.predict_matches as pm
import sl_id_match.pre_proc as pp




db_cred = 'database.ini'

slp = pp.get_and_pre_process_all(db_cred)

tm = pd.read_csv("master_ids.csv")
nm = pd.read_csv("confirmed_non_matches.csv")
match_can = lnk.get_confirmed_match_can(slp, tm, nm)


## Optionally remove matches between people with the same base IRF number:
# match_can = lnk.subset_diff_case_matches(match_can, slp)

match_can_df = lnk.eval_match_can(match_can, slp)
match_can_df = lnk.adjust_scores(match_can_df, 'Phone', 0.6)

lnk.get_true_match_vals(match_can_df, slp, tm)

test_size = 0.3
random_state = 456

train, test = train_test_split(
    match_can_df,
    stratify=match_can_df.Match,
    test_size=test_size,
    random_state=random_state)

train_matches_index = train[train.Match == 1]
test_matches_index = test[test.Match == 1]
train.drop(columns='Match', inplace=True)
test.drop(columns='Match', inplace=True)

lr_all = recordlinkage.LogisticRegressionClassifier()

lr_all.fit_predict(train, train_matches_index.index)

test = pm.get_predictions(test, lr)

lnk.get_true_match_vals(test, slp, tm)

pm.get_cf_mat(test)

test = pm.add_col_from_df(test, slp, 'country')

pm.get_country_roc_curves(test)
