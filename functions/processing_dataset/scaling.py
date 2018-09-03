import numpy as np
import pandas as pd
from .column_division import *


def log_scaling(df):
    """
    Log scaling of (intensities + 1) in df. Addition of 1 to avoid Inf in case of zeros.
    :param df: df - dataframe
    :return: df - scaled dataframe
    """
    dff = df.copy()

    # Take log(dff + 1) from intensities
    dff[samples] = np.log1p(dff[samples])
    return dff
