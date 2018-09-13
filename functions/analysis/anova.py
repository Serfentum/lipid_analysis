import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests


def anova_for_all_peaks_with_adjustment(df, variables, interaction='double'):
    """
    Conduct anova for each peak in df vs columns listed in variables
    :param df: dataframe - df with samples - rows and peaks and features - columns (normal form)
    :param variables: list - list with column names which will be used in anova
    :param interaction: str - one of 'no', 'double' and 'multiple' denoting type of interaction
    :return: masked dataframe with shape len(variables) + their interactions X len(df.columns) - len(varibles) with
    adjusted p-value for each analysis
    """
    # Get p-values for each analysis
    pvs = anova_for_all_peaks_vs_some_variables(df, variables, interaction)
    # Flatten p-value df into 1-dimensional array
    p_values = pvs.values.ravel()

    # Adjust p-values with Benjamini/Hochberg procedure
    p_values_corrected = multipletests(p_values, method='fdr_tsbh')
    bool_p = p_values_corrected[0].reshape(pvs.shape)
    cor_p = p_values_corrected[1].reshape(pvs.shape)
    # Create df with adjusted p-values and mask that which are higher than 0.05
    p_values_corrected = pd.DataFrame(cor_p, columns=pvs.columns, index=pvs.index)
    p_value_appropriate = p_values_corrected[pd.DataFrame(bool_p, columns=pvs.columns, index=pvs.index)]
    return p_value_appropriate


def anova_for_all_peaks_vs_some_variables(df, variables, interaction='double'):
    """
    Conduct anova for each column on columns in variables - each column in df except those which are in variables will
    be analysed vs those in variables
    Assumes that there are 2 non numeric columns which are the last at df. Should be fixed (probably with re)
    :param df: df - dataframe, which contains all aforementioned columns
    :param variables: list - list with column names which will be used in anova
    :param interaction: str - one of 'no', 'double' and 'multiple' denoting type of interaction
    :return: df - dataframe with shape len(variables) + their interactions X len(df.columns) - len(varibles) with
    p-value for each analysis
    """
    # Create df for p-values of all interactions in anova
    pvs = pd.DataFrame()

    # Conduct anova for each peak by age and tissue with interaction and add information to dataframe
    for peak in df.columns[:-2]:
        analysis = anova(df, peak, variables, interaction)
        pvs[peak] = analysis
    return pvs


def anova(df, feature, variables, interaction='double'):
    """
    Perform anova for 1 feature ~ variables and their interactions
    :param df: df - dataframe, which contains all aforementioned columns
    :param feature: str - name of column which will be explained
    :param variables: list - list with column names which will be used in anova
    :param interaction: str - one of 'no', 'double' and 'multiple' denoting type of interaction
    :return: df column - column with p-values from sm.stats.anova_lm without residuals
    """
    formula = construct_formula(feature, variables, interaction)
    model = smf.ols(formula, df).fit()

    # Take column with p-value for each of group
    analysis = sm.stats.anova_lm(model)['PR(>F)'].drop('Residual')
    return analysis


def construct_formula(y, xs, interaction='double'):
    """
    Create formula string for patsy in statsmodels
    :param y: str - name of dependent column
    :param xs: iterable - list with names of dependent columns
    :param interaction: str - one of 'no', 'double' and 'multiple' - whether formula will contain interaction terms
    :return: str - formula for statsmodels
    """
    # Convert numeric terms to appropriate form
    y = numeric_term(y)
    xs = list(map(numeric_term, xs))

    # Construct formula
    formula = interactions(y, xs, interaction)
    return formula


def interactions(y, xs, interaction):
    """
    Construct the formula depending on interaction type
    :param y: str - name of dependent column
    :param xs: iterable - list with names of dependent columns
    :param interaction: str - one of 'no', 'double' and 'multiple' - whether formula will contain interaction terms
    :return: str - formula for statsmodels
    """
    # Define formaulae for different interaction types and return appropriate
    interaction_types = {'multiple': f'{y} ~ ({" + ".join(xs)}) ** {len(xs)}',
                         'double': f'{y} ~ ({" + ".join(xs)}) ** 2',
                         'no': f'{y} ~ {" + ".join(xs)}'}
    return interaction_types[interaction]


def numeric_term(x):
    """
    Convert numeric term in formula to appropriate form for patsy
    If term is non-numeric it will be returned
    :param x: str - name of column
    :return: str - term in appropriate form
    """
    # For int numeric terms
    if isinstance(x, int):
        return f'Q({x})'
    # For str numeric terms
    elif x.isdigit():
        return f'Q("{x}")'
    return x
