import os
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
import matplotlib.pyplot as plt


def draw_dimensionality_reduction(name, transformed, y, classes, colors=None, title='PCA', locus='best'):
    """
    Plot results of dimensionality collapsing
    :param name: str - name of saved figure
    :param transformed: array - 2d array with transformed data
    :param y: sequence - collection of observation labels e.g. old/young for age, bones/blood for tiessue etc.
    :param classes: sequence - container with unique labels of observations
    :param colors: sequence - container with colors in #HHHHHH format where H is a hex digit
    :param title: str - title of figure
    :param locus: str - position of legend
    :return:
    """
    # Specify plot size
    plt.figure(figsize=(12, 8))

    # Use specified colors if provided
    if colors:
        for sp, color in zip(classes, colors):
            plt.scatter(transformed[sp == y, 0],
                        transformed[sp == y, 1],
                        alpha=0.8, color=color, label=sp)
    else:
        for sp in classes:
            plt.scatter(transformed[sp == y, 0],
                        transformed[sp == y, 1],
                        alpha=0.8, label=sp)

    # Metadata
    xlab = 'PC1'
    ylab = 'PC2'
    plt.legend(loc=locus, shadow=False)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)

    # Create dir for images and save svg image
    os.makedirs('img', exist_ok=True)
    plt.savefig(f'img/{name}', format='svg', bbox_inches='tight')


def construct_title(analysis, species, included_variants, separation_feature):
    """
    Construct title for plot by inferring key features of samples in dataset
    :param analysis: str - name of analysis, e.g. pca or MDS
    :param species: str - name of species, e.g. H. sapiens or rats
    :param included_variants: dict - dictionary with selected feature: variant for analysis
    :param separation_feature: str - name of feature which will be separated on plot by color, e.g. tissue or age
    :return: str - title
    """
    # Initialize variable for singleton features which contains only one variant
    features = []

    # Collect features which have only 1 variant into features
    for feature, variable in included_variants.items():
        if isinstance(variable, str):
            features.append(variable)
        elif len(variable) == 1:
            features.append(variable[0])

    # Construct title
    title = f'{analysis.upper()} of {", ".join(features)} {species.capitalize()} separated by {separation_feature.lower()}'
    return title


def extract_data_for_plot(df, sample_feature):
    """
    Take label series of data and all unique possible variants of this label type
    :param df: df - part of samples from dataframe merged with metadata
    :param sample_feature: str - index of row containing variants by which samples will be divided on the plot
    :return: df - subset of input df
    """
    # Take series
    y = df.loc[sample_feature]
    # Take unique variants
    classes = df.loc[sample_feature].unique()
    return y, classes


def pca_transform(df, n_components=2):
    """
    Transform data for PCA, meta constant should be predefined
    :param df: df - subset of dataframe merged with metadata
    :param n_components: int - number of components
    :return: array - np array with number of samples x n_components shape
    """
    # Initialize transformer
    pca = PCA(n_components=n_components)
    # Take numeric subset of data and
    # Transpose df, because as we love in ml ROWS are observations and COLUMNS are features and
    # all normal functions follow this convention. Thus we finally transpose df to normal form
    return pca.fit_transform(df.iloc[:-meta].T)


def mds_transform(df, n_components=2):
    """
    Transform data for MDS, meta constant should be predefined
    :param df: df - subset of dataframe merged with metadata
    :param n_components: int - number of components
    :return: array - np array with number of samples x n_components shape
    """
    # Initialize transformer
    mds = MDS(n_components=n_components, n_jobs=-1)
    # Take numeric subset of data and
    # Transpose df, because as we love in ml ROWS are observations and COLUMNS are features and
    # all normal functions follow this convention. Thus we finally transpose df to normal form
    transformed = mds.fit_transform(df.iloc[:-meta].T)
    return transformed


def subset(df, include, exclude={}, with_mass=True):
    """
    Take appropriate slice of data, use samples_with_mass constant which should be predefined.
    At least one of include and exclude should be provided, could be both
    :param df: df - dataframe merged with metadata
    :param include: dict - dictionary with feature: variant to include variant of feature from output df
                           other appropriate format is feature: [variants] to include all listed variants
    :param exclude: dict - dictionary with feature: variant to exclude variant of feature from output df
                           other appropriate format is feature: [variants] to exclude all listed variants
    :param with_mass: boolean - whether to exclude samples without known mass,
                                idk why I have included this option - it always should be True
    :return: (series, array) - tuple with row of given feature from input array and array with unique values in this
                               series
    """
    # Create a copy of original df
    df = df.copy()
    # Initialize condition with neutral element
    cond = True

    # For features in include add to condition appropriate columns
    for feature, variant in include.items():
        # Add single variant
        if type(variant) is str:
            cond &= (df.loc[feature] == variant)
        # Add several variants
        else:
            cond &= df.loc[feature].isin(variant)

    # For features in include add to condition appropriate columns
    for feature, variant in exclude.items():
        # Remove single variant
        if type(variant) is str:
            cond &= (df.loc[feature] != variant)
        # Remove several variants
        else:
            cond &= ~df.loc[feature].isin(variant)

    # Imho this condition is always true, hence with_mass parameter should be removed
    # Take only columns with present mass
    if with_mass:
        return df.loc[:, cond & samples_with_mass]
    # Take all selected columns
    return df.loc[:, cond]
