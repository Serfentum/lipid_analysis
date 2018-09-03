import numpy as np
import pandas as pd
from .column_division import *


def compose_metadata(df, metadata):
    """
    Alternative to add_metadata, shouldn't be used
    Prepare metadata to main df compatible structure (aligned by sample names)
    :param df: df - original dataframe
    :param metadata: df - support dataframe with metadata
    :return: df - original df with several added rows from metadata
    """
    # Extract metadata
    meta = extract_meta(metadata)
    # Add id to dataframe and transpose it for merging
    df = add_id(df).T

    # Merge transposed df with meta on new id column and index of meta
    # Transpose df back to arrange it in original manner
    df = df.merge(meta, left_on='id', right_index=True, how='left').T
    meta = df.iloc[-(meta.shape[1] + 1):, :]
    return meta


def add_metadata(df, metadata):
    """
    Add some rows from metadata to df
    :param df: df - original dataframe
    :param metadata: df - support dataframe with metadata
    :return: df - original df with several added rows from metadata
    """
    # Extract metadata
    meta = extract_meta(metadata)
    # Add id to dataframe and transpose it for merging
    df = add_id(df).T

    # Merge transposed df with meta on new id column and index of meta
    # Transpose df back to arrange it in original manner
    df = df.merge(meta, left_on='id', right_index=True, how='left').T
    return df


def extract_meta(metadata):
    """
    Find and extract age, mass and id columns from metadata
    :param metadata: df - dataframe with metainformation to extract
    :return: df - subset from given dataframe with some meta columns
    """
    # Find age
    pat = re.compile(r'age', re.I)
    age = extract_column(metadata, pat)
    # Find weight
    pat = re.compile(r'mass|weight', re.I)
    mass = extract_column(metadata, pat)
    # Find id columns
    pat = re.compile(r'id|ms', re.I)
    ids = extract_column(metadata, pat)

    # Merge series together
    meta = pd.concat([ids, age, mass], axis=1).set_index(ids.name)
    return meta


def extract_column(df, pat):
    """
    Extract columns from df with specified re pattern
    :param df: df - dataframe
    :param pat: re - compiled re
    :return: column or columns from df
    """
    return df.filter(regex=pat).iloc[:, 0]


def add_id(df):
    """
    Add row with id to df
    :param df: df - original df
    :return: df - df with row 'id'
    """
    # Add identifiers
    ids = extract_id(samples)
    df = df.append(ids)
    return df


def extract_id(samples):
    """
    Extract id by which dfs are connected from samples names
    :param samples: iterable - collection with names of samples
    :return: series - series with id of each sample which had it in a form specified by pattern
    """
    # Extract identifier of each mouse
    pat = re.compile(r'ms\d+', re.I)
    res = {}

    # Add identifier in dict if it was found
    for s in samples:
        for i in re.finditer(pat, s):
            res[s] = i.group()
            break

    # Create series and name it
    res = pd.Series(res)
    res.name = 'id'
    return res

