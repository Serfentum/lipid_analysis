import numpy as np
import pandas as pd
from .column_division import *


def purge_control(df, fold=3, exterminate=False):
    """
    Turn values in peaks whose intensity is lower than corresponding in control samples to NA
    :param df: df - dataframe to clean
    :param fold: float - number of times which intensity of peak should be larger in sample than in peak
    :param exterminate: boolean - whether to turn all values in a peak to NA if it is present in a blank (strict variant)
    :return: df - cleaned from control dataframe
    """
    df = df.copy()
    # Find maxima for each peak in all blank controls
    maxima = df[blanks].max(axis=1)

    # In case of extermination turn to NA all peaks which contains intensity > 0 in any of blanks
    if exterminate:
        df.loc[maxima[maxima != 0].index, samples_wo_controls_qc] = np.nan

    # Otherwise turn to NA values whose intensities less than fold * blank_intensity
    else:
        # Find samples where peaks' concentration less than in blank times fold multiplier
        less_than_blank = df[samples_wo_controls_qc].apply(lambda x: x < maxima * fold)
        # Purge observations with abundance less than blank one
        df[less_than_blank] = np.nan
        # Should I subtract blank value from samples?
        # df[samples_wo_controls_qc] = df[samples_wo_controls_qc].sub(maxima, axis=0)
    return df


# Load data
name = '../../vitaminD/cleaned_isotopes_cleaned_contaminants_xs_annotated_rats_neg.csv'
df = pd.read_csv(name, index_col=0)

# Purge
df = purge_control(df)
# Write to a file
df.to_csv(f'cleaned_control_{name}')