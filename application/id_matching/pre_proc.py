'''
Module for pre-processing data extracted from Searchlight for ID matching.
'''

import pandas as pd
import numpy as np
import re

from recordlinkage.preprocessing import clean
from recordlinkage.preprocessing import phonetic

from . import db_conn as dc


def get_irf_person_ids(irfs, intees):
    """Get a DataFrame of every Person ID that's on an IRF along with the IRF number."""
    irf_id = pd.merge(intees[['person_id', 'interception_record_id']],
                      irfs[['id', 'irf_number']],
                      how='left',
                      left_on='interception_record_id',
                      right_on='id')
    irf_id = irf_id[['person_id', 'irf_number']]
    irf_id['form_number'] = irf_id['irf_number']
    irf_id['form'] = 'IRF'
    return irf_id


def get_cif_person_ids(cifs, pbs):
    """Get a DataFrame of every Person ID that's on a CIF along with the base IRF number and CIF number."""
    # TODO add other PVs here
    cif_pbs = pd.merge(pbs[['cif_id', 'person_id']],
                       cifs[['id', 'cif_number']],
                       how='left',
                       left_on='cif_id',
                       right_on='id')
    cif_pbs = cif_pbs[['person_id', 'cif_number']]
    cifs = cifs[['main_pv_id', 'cif_number']]
    cifs.columns = cif_pbs.columns
    cif_id = pd.concat([cifs, cif_pbs],
                       axis=0,
                       ignore_index=True,
                       sort=False)
    cif_id.columns = 'person_id', 'form_number'
    cif_id['irf_number'] = cif_id['form_number'].str.replace('.', '')
    cif_id['irf_number'] = cif_id['irf_number'].str[:-1]
    cif_id = cif_id[['person_id', 'irf_number', 'form_number']]
    cif_id['form'] = 'CIF'
    return cif_id


def get_vdf_person_ids(vdfs):
    """Get a DataFrame of every Person ID that's on a VDF along with the base IRF number and VDF number."""
    vdf_id = vdfs[['id', 'vdf_number']]
    vdf_id.columns = 'person_id', 'form_number'
    vdf_id['irf_number'] = vdf_id['form_number'].str[:-1]
    vdf_id = vdf_id[['person_id', 'irf_number', 'form_number']]
    vdf_id['form'] = 'VDF'
    return vdf_id


def get_country_codes(bs, c):
    """Get a DataFrame of station codes and country names from border station and country SL tables."""
    country_codes = pd.merge(bs,
                             c,
                             how='left',
                             left_on='operating_country_id',
                             right_on='id')
    country_codes = country_codes[['station_code', 'name']]
    country_codes.rename(columns={'name': 'country'}, inplace=True)
    return country_codes


def get_person_forms(dp, irf_id, cif_id, vdf_id):
    """Combine all person records with the corresponding forms they're associated with."""
    forms = pd.concat([irf_id, cif_id, vdf_id],
                      axis=0,
                      sort=False)
    person_forms = pd.merge(dp,
                            forms,
                            how='left',
                            left_on='id',
                            right_on='person_id')
    del person_forms['person_id']
    person_forms.drop_duplicates('id', inplace=True)
    return person_forms


def add_countries(df, country_codes):
    """Add country names to DataFrame by joining on station code of IRF number."""
    df['station_code'] = df.irf_number.str[:3]
    df = pd.merge(df,
                  country_codes,
                  how='left',
                  on='station_code')
    del df['station_code']
    return df


def get_features(df):
    """Clean and engineer new features for match comparison."""

    # remove non-alpha characters from names and generate phonetic codes:
    df['Original Name_cleaned'] = clean(df['Original Name'])
    df['o_name_phonetic_code'] = phonetic(df['Original Name_cleaned'], method="soundex")

    df['Age'] = df['Age'].astype('float')

    #df['add2_lat'] = df['add2_lat'].astype('float')
    #df['add2_long'] = df['add2_long'].astype('float')

    # remove non-numeric characters from phone numbers and save as strings for levenshtein comparison:
    df['Phone'] = df['Phone'].str.replace(r'[^0-9]+', '')
    df['Phone'] = df['Phone'].astype(str)

    # remove all characters that aren't part of a URL:
    df['social_media'] = df['social_media'].apply(
        lambda x: re.findall(
            'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            str(x))).sort_values().str[0]
    df['social_media'] = df['social_media'].fillna(np.nan)

    return df


def get_and_pre_process_all(db_cred):

    dp, intees, irfs, cifs, vdfs, pbs, c, bs = dc.get_sl_data(db_cred)

    irf_id = get_irf_person_ids(irfs, intees)
    cif_id = get_cif_person_ids(cifs, pbs)
    vdf_id = get_vdf_person_ids(vdfs)

    country_codes = get_country_codes(bs, c)

    slp = get_person_forms(dp, irf_id, cif_id, vdf_id)
    slp = add_countries(slp, country_codes)

    slp.set_index('id', inplace=True)

    keep_cols = ['Original Name',
                 'Age',
                 'Gender',
                 'Phone',
                 'birthdate',
                 'nationality',
                 'social_media',
                 'country',
                 'irf_number',
                 'form_number',
                 'form' ]
    slp = slp[['full_name', 'age', 'gender', 'phone_contact', 'birthdate', 'nationality', 'social_media',
               'country', 'irf_number', 'form_number', 'form']]
    slp.columns = keep_cols

    slp = get_features(slp)
    return slp

def get_and_pre_process_all2(db_cred):

    slp = dc.get_sl_data2(db_cred)
    slp.set_index('id', inplace=True)

    keep_cols = ['Original Name',
                 'Age',
                 'Gender',
                 'Phone',
                 'birthdate',
                 'nationality',
                 'social_media',
                 'country',
                 'irf_number',
                 'form_number',
                 'form' ]

    slp.columns = keep_cols

    slp = get_features(slp)
    return slp
