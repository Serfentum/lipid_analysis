import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from .column_division import *


def z_scale(df):
    """
    Perform z-scaling on df
    samples constant should be predefined
    :param df: df - dataframe
    :return:
    """
    df = df.copy()

    # Initialize scaler and scale numeric data
    ss = StandardScaler()
    # Transposes are to scale data for each peak and turn it to original form
    df[samples] = ss.fit_transform(df[samples].T).T
    return df


def log_transform(df):
    """
    Log scaling of (intensities + minimum) in df. Addition of minimum to avoid Inf in case of zeros.
    Minimum is a half of minimal positive value
    samples constant should be predefined
    :param df: df - dataframe with nonnegative values
    :return: df - log transformed dataframe
    """
    df = df.copy()

    # Adding 1 before log transformation is too much for z-scaled positivised data
    # Thus I have apply this general method:
    # According to this post, one of appropriate adding to 0 before log-transforming is half of nonnegative minimum
    # value
    # https://robjhyndman.com/hyndsight/transformations/
    # Find positive minimum to add to values
    minimum = df[samples][df[samples] != 0].min().min()

    # Take  from intensities
    df[samples] = np.log(df[samples] + minimum)
    return df


def positivize(df):
    """
    Add minimal value in df to df (shift value distribution to start from 0)
    samples constant should be predefined
    :param df: df - dataframe
    :return: df - nonnegative (0 and positives) dataframe
    """
    df = df.copy()

    # Find minimum and subtract it from df
    minimum = df[samples].min().min()
    df[samples] = df[samples] - minimum
    return df
