import os
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
import matplotlib.pyplot as plt


def reduce_dimensions(df, analysis, species, separation_feature, functions, included_variants, excluded_variants={}, with_mass=True):
    """
    Top function to perform dimensionality reduction, plot graph and save figure
    :param df: df - dataframe merged with metadata
    :param analysis: str - lowercase name of analysis, e.g. pca or mds
    :param species: str - name of species
    :param separation_feature: str - name of feature which will be separated on plot by color, e.g. tissue or age
    :param functions: dict - dictionary with name: transformation_function
    :param included_variants: dict - dictionary with selected feature: variant for analysis
    :param excluded_variants: dict - dictionary with excluded feature: variant from analysis
    :param with_mass: bool - whether to take samples without mass in the analysis
    :return:
    """
    # Create title
    title = construct_title(analysis, species, included_variants, separation_feature, with_mass)

    # Take appropriate subset of data
    ss = subset(df, included_variants, excluded_variants, with_mass=with_mass)

    # Exit function if subset is empty
    if ss.empty or ss.loc[separation_feature].isna().all():
        return

    # Extract y and classes for plot
    y, classes = extract_data_for_plot(ss, separation_feature)

    # Transform selected samples with PCA or MDS or something else
    transforming(analysis, functions, ss, title, y, classes)


def draw_variants(df, feature, analysis, species, separation_feature, functions, excluded_variants={}, with_mass=True):
    """
    Draw and save plots for analysis of everything feature variant separately
    Plots for subsets of data where variants for separation_feature are absent (NA) won't be drawed
    :param df: df - dataframe merged with metadata
    :param feature: str - index of df row which contains variants which should be plotted separately
    :param analysis: str - lowercase name of analysis, e.g. pca or mds
    :param species: str - name of species
    :param separation_feature: str - name of feature which will be separated on plot by color, e.g. tissue or age
    :param functions: dict - dictionary with name: transformation_function
    :param excluded_variants: dict - dictionary with excluded feature: variant from analysis
    :param with_mass: bool - whether to take samples without mass in the analysis
    :return:
    """
    # Select non NA variants
    variants = df.loc[feature].unique()
    nas = pd.isna(variants)

    # Draw and save plot for each subset of data with particular value of feature
    for variant in variants[~nas]:
        included_variants = {feature: variant}
        reduce_dimensions(df, analysis, species, separation_feature, functions, included_variants, excluded_variants,
                          with_mass)


def plot_variants_with_opposite_separations(df, species, functions, analyses=('pca', 'mds'), separations=('tissue', 'age'), excluded={}):
    """
    Plot figure for each specified analysis with and without mass for each of 2 features in separations divided by the
    remaining one
    :param df: df - dataframe
    :param species: str - name of species in analysis
    :param functions: dict - dictionary with name: transformation function
    :param analyses: iterable - collection with names of analyses, which are in functions container
    :param separations: iterable - collection with 2 names of features used in separation of data in plots
    :param excluded: dict - dictionary with feature: variants to exclude
    :return:
    """
    for analysis in analyses:
        for with_mass in [True, False]:
            # 1 feature separated by other and vice versa
            draw_variants(df, separations[0], analysis, species, separations[1], functions, excluded, with_mass=with_mass)
            draw_variants(df, separations[1], analysis, species, separations[0], functions, excluded, with_mass=with_mass)


def transforming(analysis, functions, ss, title, y, classes):
    """
    Perform appropriate transformation and plotting, save figure
    :param analysis: str - name of analysis, e.g. pca or mds
    :param functions: dict - dictionary with name: transformation_function
    :param ss: df - chosen subset of data
    :param title: str - title of plot and name of file
    :param y: sequence - collection of observation labels e.g. old/young for age, bones/blood for tiessue etc.
    :param classes: sequence - container with unique labels of observations
    :return:
    """
    # Depending on analysis extract additional data
    if analysis == 'pca':
        transformed, (var1, var2) = functions[analysis](ss)
        # Draw and save plot
        draw_dimensionality_reduction(title, transformed, y, classes, title=title, var1=var1, var2=var2)
    else:
        transformed = functions[analysis](ss)
        # Draw and save plot
        draw_dimensionality_reduction(title, transformed, y, classes, title=title)


def draw_dimensionality_reduction(name, transformed, y, classes, colors=None, title='PCA', var1=0, var2=0, locus='best'):
    """
    Plot results of dimensionality collapsing
    :param name: str - name of saved figure
    :param transformed: array - 2d array with transformed data
    :param y: sequence - collection of observation labels e.g. old/young for age, bones/blood for tiessue etc.
    :param classes: sequence - container with unique labels of observations
    :param colors: sequence - container with colors in #HHHHHH format where H is a hex digit
    :param title: str - title of figure
    :param var1: float - portion of explained variance by PC1
    :param var2: float - portion of explained variance by PC1
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
    # For pca plot add axis labels with explained variance portion
    if 'PCA' in title:
        xlab = f'PC1, {var1}'
        ylab = f'PC2, {var2}'
        plt.xlabel(xlab)
        plt.ylabel(ylab)

    plt.legend(loc=locus, shadow=False)
    plt.title(title)

    # Create dir for images and save svg image
    os.makedirs('img', exist_ok=True)
    plt.savefig(f'img/{name}.svg', format='svg', bbox_inches='tight')


def construct_title(analysis, species, included_variants, separation_feature, with_mass):
    """
    Construct title for plot by inferring key features of samples in dataset
    :param analysis: str - name of analysis, e.g. pca or MDS
    :param species: str - name of species, e.g. H. sapiens or rats
    :param included_variants: dict - dictionary with selected feature: variant for analysis
    :param separation_feature: str - name of feature which will be separated on plot by color, e.g. tissue or age
    :param with_mass: boolean - whether samples without mass are included in analysis
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

    # Create mass part
    if with_mass:
        wm = 'only with mass'
    else:
        wm = 'with and without mass'

    # Construct title
    title = f'{analysis.upper()} of {", ".join(features)} {species.capitalize()} {wm} separated by {separation_feature.lower()}'
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
    Transform data for PCA
    meta constant should be predefined
    :param df: df - subset of dataframe merged with metadata
    :param n_components: int - number of components
    :return: array - np array with number of samples x n_components shape
    """
    # Initialize transformer
    pca = PCA(n_components=n_components)
    # Take numeric subset of data and
    # Transpose df, because as we love in ml ROWS are observations and COLUMNS are features and
    # all normal functions follow this convention. Thus we finally transpose df to normal form
    transformed = pca.fit_transform(df.iloc[:-meta].T)

    # Get info about variance percentages
    variance = pca.explained_variance_ratio_
    return transformed, tuple(map(lambda x: np.round(x, 2), variance))


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


def subset(df, include, exclude={}, with_mass=with_mass):
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
