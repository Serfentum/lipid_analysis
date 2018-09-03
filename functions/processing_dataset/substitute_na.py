import numpy as np
import pandas as pd
from .column_division import *


# TODO: Other method for filling NAs - 0.5 * min(sample) looks flimsy
def remove_na_peaks(df, fraction=1):
    """
    Remove peaks which have no values in samples and qc. Need predefined constant samples_wo_controls_qc
    :param df: df - dataframe to clean
    :param fraction: float - threshold of tolerable NA portion for peak
    :return: df - cleaned from empty peaks dataframe
    """
    # Find peaks which contain NA more than provided fraction in samples and qc
    too_many_na = df[samples_wo_controls_qc].isna().sum(axis=1) / df[samples_wo_controls_qc].shape[1] > fraction
    na_peaks = too_many_na[too_many_na].index

    # Get rid of these peaks
    df = df.drop(na_peaks)
    return df

def substitute_na(df):
    """
    Substitute NA with values. Need predefined constant samples_wo_controls_qc
    :param df: df - dataframe to clean
    :return: df - dataframe with values in sample area
    """
    df = df.copy()

    # Fill NA with 0.5 * min(sample) in columns with intensities
    df[samples_wo_controls_qc] = df[samples_wo_controls_qc].apply(lambda xs: xs.fillna(xs.min() / 2), axis=1)
    return df
