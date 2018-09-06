import numpy as np
import pandas as pd
from .column_division import *


# Really many functions in 1 file, probably should be divided by normalization type or refactored with more general
# functions
def percentille_normalization(df, q=0.75):
    """
    Normalize intensities in dataframe by some of their order statistic, 75 by default
    Data is assumed to be log-transformed
    samples and meta constants should be predefined
    :param df: df - dataframe with all data
    :param q: float - percentile which will be denominator
    :return: df - normalized by percentile df
    """
    df = df.copy()

    # Because of addition of metadata to rows there is a problem - data in column is heterogeneous (intensities and categories)
    # Thus we have to convert it to float before operations
    numeric_part = df.loc[df.index[:-meta], samples].apply(lambda x: pd.to_numeric(x, errors='ignore'))

    # Normalize by selected percentile
    numeric_part = numeric_part.subtract(numeric_part.quantile(q, axis=1), axis=0)
    df.loc[df.index[:-meta], samples] = numeric_part.astype('O')
    return df


def normalize(df, function, *args, **kwargs):
    """
    Apply normalization function to subset of df, which is determined by samples and meta constants which should be
    defined earlier
    Modify input df
    :param df: df - dataframe with all data
    :param function: function - function which takes df and return df
    :param args: sequence - list, tuple, set or str with parameters in the right order to function
    :param kwargs: dict - dict with name: value of parameters to function
    :return:
    """
    df.loc[df.index[:-meta], samples] = function(df.loc[df.index[:-meta], samples].astype(dtype='float'), *args, **kwargs)


def find_diff(df):
    """
    Find number of rows for metainformation in df. This rows should located at the bottom of df
    Assumes that only peak names contains numbers
    Used for finding constant meta
    :param df: df - dataframe with metadata
    :return: int - number of rows which are taken by metadata
    """
    meta = df.shape[0] - df.filter(regex=r'\d+', axis=0).index.shape[0]
    return meta

# mz of diverse standard adducts - H and Ac-H
standard_mzs = {'pg': [709.55189, 769.57302],
                'pe': [740.54648, 800.56761],
                'ceramide': [529.53310, 589.55423]}


def standard_normalization(df, standard_mzs, precision=5):
    """
    Normalize df by standard intensities. Throw an error if no standards were found. It should be refined I think.
    Make loop with try block to reduce precision up to some value, after this perhaps we should return original df.
    :param df: df - dataframe with all data, with no nonnumericals in columns with intensities
    :param standard_mzs: dict - standard names and lists of their mzs
    :param precision: int - number of digits to round mzs before comparison
    :return: df - df with normalized intensities by standard intensities
    """
    # Find standards
    standards = find_standards(df, standard_mzs, precision)
    # Select suitable standard
    standard = select_standard(standards)
    # Normalize by standard itensities
    df = std_normalization(df, standard)
    return df


def std_normalization(df, standard):
    """
    Divide intensities in df by standard intensities
    :param df: df - dataframe with all data, with no nonnumericals in columns with intensities
    :param standard: series - series with standard intensities
    :return: df - normalized by standard intensities df
    """
    df = df.copy()

    # Extract np array with values from standard series
    standard = standard[samples].values.reshape(-1)
    # Subtract standard intensities from values
    df[samples] = df[samples].subtract(standard, axis=1)
    return df


def select_standard(standards):
    """
    Function to select some standard intensities between all. Now it is just maximal intensities from all standards
    :param standards: df - dataframe with standards intensities
    :return: series - series with selected intensities
    """
    # Select maximal intensities from all standards
    return standards.max()


def find_standards(df, standard_mzs, precision=5):
    """
    Find standard's peaks in df given dictionary with their mzs
    :param df: df - dataframe with data
    :param standard_mzs: dict - standard names and lists of their mzs
    :param precision: int - number of digits to round mzs before comparison
    :return: df - dataframe with rows from original corresponding to standards
    """
    # Create empty df for standards
    stands = pd.DataFrame()

    # Compare mzs of all standards with peak's and write ones with equal to standard mzs to df
    for standard, mzs in standard_mzs.items():
        for mz in mzs:
            p = df['mz'].round(precision) == np.round(mz, precision)
            stands = stands.append(df[p])

    # Check whether some standards are present
    assert not stands.empty, 'No standards was found in df!\nTry less strict precision'
    return stands


def normalize_by_mass(df, mass_row_name='mass'):
    """
    Apply mass normalization function to subset of df, which is determined by samples, samples_with_mass and meta
    constants which should be defined earlier. Samples should be an Index object.
    Perhaps we should remake these functions to take all that independent constants
    Modify input df
    :param df: df - dataframe with all data
    :param mass_row_name: str - name of row with mass data
    :return:
    """
    # Select intensities of samples
    samples_intensities = prepare_intensities(df)
    # Pick masses of samples
    masses = prepare_mass(df, mass_row_name)
    # Normalize
    df.loc[df.index[:-meta], samples[samples_with_mass]] = mass_norm(samples_intensities, masses)


def mass_norm(samples_intensities, masses):
    """
    Perform normalization by mass
    :param samples_intensities: df - dataframe with intensities of samples with known mass in float format
    :param masses: series - series with mass data, which is converted to float
    :return: df - dataframe with intensities normalized by mass
    """
    # Log transform mass because it is not scaled but data is
    return samples_intensities - masses.apply(np.log)


def prepare_mass(df, mass_row_name='mass'):
    """
    Get mass data from df
    :param df: df - dataframe with merged metadata
    :param mass_row_name: str - name of row with mass data
    :return: series - series with mass data, which is converted to float
    """
    # samples_with_mass should be defined
    # Pick masses of samples and convert them to float
    masses = df.loc[mass_row_name, samples_with_mass[samples_with_mass].index]
    masses = masses.astype('float')
    return masses


def prepare_intensities(df):
    """
    Get data with intensities of samples with known mass from df
    :param df: df - dataframe with merged metadata
    :return: df - subset of passed into df with intensities, which are converted to floats
    """
    # Select intensities of samples with mass and convert them to float
    samples_intensities = df.loc[df.index[:-meta], samples].loc[:, samples_with_mass]
    samples_intensities = samples_intensities.astype('float')
    return samples_intensities
