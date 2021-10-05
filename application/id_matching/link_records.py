'''
Module for getting and interacting with entity pairs using the recordlinkage package.
'''

from copy import deepcopy
from time import time
import pandas as pd
import numpy as np
import recordlinkage


def get_match_candidates(a, **kwargs):
    """Returns a multi-index of match candidates based on one or two DataFrames and selected index type."""
    b = kwargs.get('b', None)
    type = kwargs.get('type', 'full')
    on_col = kwargs.get('on', None)
    dupe_indexer = recordlinkage.Index()
    if type == 'full':
        dupe_indexer.full()
    elif type == 'block':
        dupe_indexer.block(on_col)
    elif type == 'neighborhood':
        dupe_indexer.sortedneighbourhood(on_col)
    match_can = dupe_indexer.index(a, b)
    return match_can


def get_true_match_can(df, tm):
    """Get multi-index of match candidates only for confirmed matches."""
    df2 = deepcopy(df)
    df2.reset_index(inplace=True)
    df2 = pd.merge(df2,
                   tm[['id', 'new_mid']],
                   how='left',
                   on='id')
    df2.set_index('id', inplace=True)
    tm_can = get_match_candidates(df2, type='block', on='new_mid')
    return tm_can


def get_confirmed_match_can(df, tm, nm):
    """Get multi-index of match candidates for confirmed matches and non-matches."""
    tm_can = get_true_match_can(df, tm)
    nm_can = pd.MultiIndex.from_frame(nm[['id_a', 'id_b']])
    nm_can = nm_can[~nm_can.isin(tm_can)]
    match_can = tm_can.append(nm_can)
    return match_can


def get_true_match_vals(match_can_df, df, tm):
    """Adds a column with 1 (confirmed match) and 0 (confirmed non-match) to Match Candidate DataFrame."""
    tm_can = get_true_match_can(df, tm)
    match_can_df['Match'] = 0
    match_can_df.Match[match_can_df.index.isin(tm_can)] = 1

#WIP Gets matches for given person id
def get_match_can_for_single(can_id, df):
    """Get multi-index of match candidates for a given person"""
    
    candidate = df.filter(regex='^'+str(can_id)+'$', axis=0)
    match_can = get_match_candidates(a=candidate,
                                     b=df[~df.index.isin(candidate.index)])
    return match_can

def get_random_one_match_can(df, country=None, print_id=True):
    """Get multi-index of match candidates for one randomly selected person (and optionally select country)."""
    print("Getting Rand One")
    if country is None:
        rand_one = df.sample(n=1)
    else:
        rand_one = df[df.country == country].sample(n=1)
    print(rand_one)
    print("showing index")
    print(rand_one.shape)
    print(df.filter(regex='^'+'16428'+'$', axis=0))
    '''
    print("Getting match_can")
    match_can = get_match_candidates(a=rand_one,
                                     b=df[~df.index.isin(rand_one.index)])
    print(match_can)
    if print_id:
        print(df.loc[match_can[1][0]])
    return match_can
'''

def subset_diff_case_matches(mc, df):
    """Get subset of matches between persons from different cases (according to base IRF number)."""
    mc2 = mc.to_frame(index=False)
    mc2.columns = 'id_1', 'id_2'
    diff_irf_can = pd.merge(mc2, df.reset_index()[['id', 'irf_number']],
                            how='inner',
                            left_on='id_1',
                            right_on='id')
    diff_irf_can = pd.merge(diff_irf_can, df.reset_index()[['id', 'irf_number']],
                            how='inner',
                            left_on='id_2',
                            right_on='id')
    diff_irf_can = diff_irf_can[diff_irf_can.irf_number_x != diff_irf_can.irf_number_y]
    diff_irf_can.drop(columns=['id_x', 'id_y', 'irf_number_x', 'irf_number_y'], inplace=True)
    sub_mc = pd.MultiIndex.from_frame(diff_irf_can[['id_1', 'id_2']])
    return sub_mc


def eval_match_can(mc, df):
    """Evaluate match candidates and calculate a 0-1 score for each feature."""
    compare_dupes = recordlinkage.Compare()
    compare_dupes.string('Original Name_cleaned',
                         'Original Name_cleaned',
                         label='Original Name_cleaned')
    compare_dupes.string('o_name_phonetic_code',
                         'o_name_phonetic_code',
                         label='o_name_phonetic_code')
    #compare_dupes.geo('add2_lat',
    #                  'add2_long',
    #                  'add2_lat',
    #                  'add2_long',
    #                  method='exp',
    #                  offset=0,
    #                  scale=15,
    #                  label='a2_lat-long')
    compare_dupes.exact('Gender',
                        'Gender',
                        label='Gender')
    compare_dupes.numeric('Age',
                          'Age',
                          method='exp',
                          scale=3,
                          label='Age')
    compare_dupes.string('Phone',
                         'Phone',
                         label='Phone',
                         method='levenshtein')
    compare_dupes.exact('birthdate',
                        'birthdate',
                        label='birthdate')
    compare_dupes.string('nationality',
                         'nationality',
                         label='nationality')
    compare_dupes.exact('social_media',
                        'social_media',
                        label='social_media')
    match_can_p = compare_dupes.compute(mc, df)
    return match_can_p


def adjust_scores(mc_df, col, cutoff):
    """Adjust feature scores in Match Candidate DataFrame by changing scores below the
    specified cutoff to zero."""
    mc_df[col] = np.where(mc_df[col] > cutoff,
                          mc_df[col],
                          0)
    return mc_df
