'''
This is an example of a good code structure using data from 
Stack Overflow's annual Developer survey
'''

import numpy as np
import pandas as pd
import zipfile
import re
import os

age_bins = [0, 18, 24, 34, 44, 54, 64, 100]

age_labels = ['17 years or younger', '18 - 24 years old', 
    '25 - 34 years old', '35 - 44 years old', '45 - 54 years old', 
    '55 - 64 years old', '65 years or older']

columns_to_keep = ['Respondent', 'Country', 'Employment', 'Ethnicity', 'Gender', 'YearsCode', 
    'EdLevel', 'JobSat', 'LanguageWorkedWith', 'Age']


def process_data():
    '''
    Reads Stack Overflow's data, cleans and reshapes it and writes the final 
    dataset to a csv document.
    '''

    zf = zipfile.ZipFile('stack_overflow_2020.zip') 
    df = pd.read_csv(zf.open('developer_survey_2020/survey_results_public.csv'))
    df = df.filter(items=columns_to_keep)
    df = clean_data(df)
    df = gen_categoricals(df)
    df = add_lang_columns(df)

    df.to_csv(r'stack_overflow.csv', index = False)


def clean_data(dataframe):
    '''
    Takes the dataframe and adds a column for each coding language.
    '''

    df = dataframe.copy()

    df['YearsCode'] = df['YearsCode'].replace('More than 50 years', 50)
    df['YearsCode'] = df['YearsCode'].replace('Less than 1 year', 0)
    df['YearsCode'] = df['YearsCode'].astype('float64')

    df['EdLevel'] = df['EdLevel'].str.replace(r'\(.*\)' , '')

    return df


def gen_categoricals(dataframe):
    '''
    Converts the age column into categoricals
    '''

    df = dataframe.copy()

    df['age_cat'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=True)

    return df


def add_lang_columns(dataframe):
    '''
    Takes the dataframe and adds a column for each coding language.
    '''

    df = dataframe.copy()

    langs = []

    for val in df['LanguageWorkedWith'].dropna().values:
        temp = val.split(';')
        for lang in temp:
            if lang not in langs:
                langs.append(lang.strip())

    df = df[df.LanguageWorkedWith.notnull()]
    df['LanguageWorkedWith'] = ';' + df['LanguageWorkedWith'] + ';'
    
    for lang in langs:
        df[lang] = np.where(df['LanguageWorkedWith'].str.contains('\;'+re.escape(lang)+'\;'), True, False)
    
    return df


if __name__ == '__main__':
    process_data()





