import numpy as np
import pandas as pd
from .column_division import *


def purge_control(df):
    """
    Remove values in peaks whose intensity is lower than corresponding in control samples
    :param df: df - dataframe to clean
    :return: df - cleaned from control dataframe
    """
    dff = df.copy()
    # Find maxima for each peak in all blank controls
    maxima = dff[blanks].max(axis=1)
    # Find samples where peaks' concentration less than their in blank
    less_than_blank = dff[samples_wo_controls_qc].apply(lambda x: x < maxima)

    # Purge observations with abundance less than blank one
    dff[less_than_blank] = np.nan
    return dff

# Load data
name = '../../vitaminD/cleaned_isotopes_cleaned_contaminants_xs_annotated_rats_neg.csv'
df = pd.read_csv(name, index_col=0)

# Purge
df = purge_control(df)
# Write to a file
df.to_csv(f'cleaned_control_{name}')