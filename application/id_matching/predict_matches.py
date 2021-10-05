'''
Module for predicting match likelihood and evaluating algorithm performance.
'''

from copy import deepcopy
from time import time
import pandas as pd
import numpy as np
import recordlinkage
import seaborn as sns
import matplotlib.pyplot as plt
import pickle
import recordlinkage

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.metrics import confusion_matrix


def load_classifier(cl_name):
    """Load previously saved classifier for ID matching."""
    with open(cl_name, 'rb') as file:
        lr = pickle.load(file)
    return lr


def get_predictions(mc_df, cl):
    """Get predictions between 0 and 1 for each record by multiplying the classifier ('cl')
    coefficients with DataFrame ('df') features, adding the cl intercept, and applying a
    logistic transformation."""
    mc2 = deepcopy(mc_df)
    try:
        mc2['p'] = cl.intercept
    except:
        mc2['p'] = cl.intercept[0]
    for i in range(0, len(cl.coefficients)):
        mc2['p'] += mc2.iloc[:, i].apply(lambda x: x * cl.coefficients[i])
    mc2['p'] = mc2['p'].apply(lambda x: np.e ** x / (1 + np.e ** x))
    mc2.sort_values('p', ascending=False)
    return mc2


def get_top_matches(dfp, df, cutoff=0.9, max=10):
    """Get top matches with prediction scores greater than cutoff."""
    dfp2 = dfp[dfp.p > cutoff]

    if len(dfp2) > 0:
        dfp2 = pd.merge(
            df.reset_index(),
            dfp2.reset_index(),
            how='right',
            left_on='id',
            right_on='id_2',
            # right_on='level_1',
            suffixes=('', '_match')).sort_values('p', ascending=False)
        dfp2['Match_Prob'] = dfp2['p']
        dfp2['Match_Prob'] = pd.Series(
            [round(val, 4) for val in dfp2['Match_Prob']],
            index=dfp2.index)
        dfp2['Match_Prob'] = pd.Series(
            ["{0:.2f}%".format(val * 100) for val in dfp2['Match_Prob']],
            index=dfp2.index)
        dfp2 = dfp2[['Match_Prob', 'form_number', 'form', 'Original Name', 'Original Name_cleaned_match',
                     'o_name_phonetic_code_match', 'Phone', 'Phone_match', 'social_media_match', 'id_1','id_2']]
        dfp2.columns = ['Match_Prob', 'Form Number', 'Form', 'Name', 'Name Match',
                     'Phonetic Name Match', 'Phone', 'Phone Match', 'Social Media Match','id1','id2']
        dfp2 = dfp2.head(max)
        dfp2.index = np.arange(1, len(dfp2)+1)
        return dfp2
    #else:
        #print("No Matches with > {:.0%} probability".format(cutoff))


def get_coef_df(df, cl):
    """Get a DataFrame of coefficient weights next to their names for a given classifier."""
    coef_values = pd.Series(cl.coefficients)
    coef_names = pd.Series(df.columns).head(len(coef_values))
    coef = pd.DataFrame(pd.concat([coef_names, coef_values], axis=1))
    coef.columns = ['Field_Name', 'Value']
    return coef


def add_col_from_df(mc_df, df, col):
    """Add a given column from the original DataFrame to the Match Candidates Data Frame."""
    new_mc_df = pd.merge(mc_df.reset_index(),
                         df.reset_index()[['id', col]],
                         how='left',
                         left_on='id_1',
                         right_on='id')
    new_mc_df.drop(columns='id', inplace=True)
    new_mc_df.set_index(['id_1','id_2'], inplace=True)
    return new_mc_df


def print_country_match_table(mc_df, df):
    """Print a table that lists true matches ('sum') and match candidates ('count') by country."""
    country_matches = deepcopy(mc_df)
    while not country_matches.country.all():
        col = 'country'
        country_matches = add_col_from_df(mc_df, df, col)
    print(
        pd.pivot_table(
            country_matches[['Match', 'country']],
            index='country',
            aggfunc=['sum', 'count'])
          )


def get_cf_mat(df, match_col='Match', pred_col='p', cutoff=0.5):
    """Create a confusion matrix from DataFrame with two columns (strings) and a cutoff (float)
    (modified from https://github.com/DTrimarchi10/confusion_matrix/blob/master/cf_matrix.py)
    """
    df['p_cutoff'] = np.where(
        df[pred_col] >= cutoff,
        1,
        0)
    cf = confusion_matrix(df[match_col], df['p_cutoff'])

    accuracy = np.trace(cf) / float(np.sum(cf))
    # Metrics for Binary Confusion Matrices
    precision = cf[1, 1] / sum(cf[:, 1])
    recall = cf[1, 1] / sum(cf[1, :])
    f1_score = 2 * precision * recall / (precision + recall)
    stats_text = "\n\nAccuracy={:0.3f}\nPrecision={:0.3f}\nRecall={:0.3f}\nF1 Score={:0.3f}".format(
        accuracy, precision, recall, f1_score)

    group_names = ['True Neg', 'False Pos', 'False Neg', 'True Pos']
    group_counts = ["{0:0.0f}".format(value) for value in
                    cf.flatten()]
    group_percentages = ["{0:.2%}".format(value) for value in
                         cf.flatten() / np.sum(cf)]
    labels = []
    for i in zip(group_names, group_counts, group_percentages):
        labels.append("%s" % i[0] + "\n%s" % i[1] + "\n%s" % i[2])
    labels = np.asarray(labels).reshape(2, 2)

    plt.figure(figsize=(8, 5))
    sns.heatmap(cf,
                annot=labels,
                fmt='',
                cmap='Blues',
                annot_kws={"size": 14})
    plt.xlabel(stats_text, fontsize=14)
    plt.title("Classifer Cutoff: {:.0%}".format(cutoff), fontsize=20)


def get_country_roc_curves(mc_df):
    """Display ROC Curves for each country that has more than one match along with the number
    of Match Candidates ('MC') and their 'Area Under the Curve' score ('AUC')."""

    result_table = pd.DataFrame(columns=['countries', 'fpr', 'tpr', 'auc', 'match_can'])

    countries = []
    for c in mc_df.country.unique():
        if len(mc_df[mc_df.country == c].Match) - sum(mc_df[mc_df.country == c].Match) > 1:
            countries.append(c)

    for c in countries:
        c_df = mc_df[mc_df.country == c]
        fpr, tpr, _ = roc_curve(c_df.Match, c_df.p, pos_label=1)
        auc = roc_auc_score(c_df.Match, c_df.p)
        match_can = len(c_df.Match)

        result_table = result_table.append({'country': c,
                                            'fpr': fpr,
                                            'tpr': tpr,
                                            'auc': auc,
                                            'match_can': match_can},
                                           ignore_index=True)

    # Set name of the classifiers as index labels
    result_table.set_index('country', inplace=True)

    fig = plt.figure(figsize=(9, 7))

    for i in result_table.index:
        plt.plot(result_table.loc[i]['fpr'],
                 result_table.loc[i]['tpr'],
                 label="{}, MC={}, AUC={:.3f}".format(i,
                                                      result_table.loc[i]['match_can'],
                                                      result_table.loc[i]['auc']))

    plt.plot([0, 1], [0, 1], color='orange', linestyle='--')

    plt.xticks(np.arange(0.0, 1.1, step=0.1))
    plt.xlabel("Flase Positive Rate", fontsize=15)

    plt.yticks(np.arange(0.0, 1.1, step=0.1))
    plt.ylabel("True Positive Rate", fontsize=15)

    plt.title('ROC Curves by Country', fontweight='bold', fontsize=15)
    plt.legend(prop={'size': 13}, loc='lower right')

    plt.show()
