import numpy as np
import pandas as pd
from .column_division import *


def purge_isotopes(df):
    """
    Delete isotopic peaks with lower intensity from dataset - peaks are rows and mz, rt, samples are columns
    :param df: df - dataframe to clean
    :return: df - cleaned from isotopes dataframe
    """
    # Parse isotopes column and extract id of peak and isotope type
    df[['id', 'type']] = df['isotopes'].str.extract(r'\[(?P<id>\d+)\]\[(?P<type>.+)\]', expand=True)

    # Get indices of appropriate peaks
    ind = df.groupby('id').apply(isotop_chose).values

    # Obtain df without redundant isotope peaks which had isotope alternatives
    data_wo_isotopes = df.loc[ind]
    # Obtain df with peaks without isotope alternatives
    data_wo_isotopes_na = df[df['id'].isna()]

    # Unite dfs to one
    cleaned = pd.concat([data_wo_isotopes, data_wo_isotopes_na])

    # Delete obsolete columns
    cleaned.drop(['id', 'type'], axis=1, inplace=True)
    return cleaned


def isotop_chose(group):
    """
    Return index of peak with greatest fraction of maximal concentration from group.
    samples here is a subset of columns (which contains peaks) which should be processed
    :param group: df - group of grouped df
    :return: index - indices of appropriate peaks
    """
    index = (group[samples] == group[samples].max(axis=0)).sum(axis=1).idxmax()
    return index
