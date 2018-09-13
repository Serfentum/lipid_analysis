from .anova import *


def anova_permutations(df, variables, permutated, n=1000, interaction='double'):
    """
    Perform permutation test with anova tests
    :param df: df - dataframe with samples - rows and peaks and features - columns (normal form)
    :param variables: list - list with column names which will be used in anova
    :param permutated: list - features from variables in which labels should be mixed
    :param n: int - number of permutations
    :param interaction: str - type of interaction in anova, one of 'no', 'double' and 'multiple'
    :return: df - dataframe with size n X len(variables) + their interactions filled with significant peaks and their
    significance for each category after each permutation
    """
    # Perform anova 1 time to obtain right column structure for df with permutations results
    trial = anova_for_all_peaks_vs_some_variables(df, variables, interaction)
    # Create result df
    results_permutation = pd.DataFrame(columns=trial.index)

    # By number of permutations:
    # shuffle specified labels
    # conduct anova n times
    # compute BH corrected p-values
    # store significant peaks in result dataframe
    for i in range(n):
        # Shuffle specified labels
        for feature in permutated:
            np.random.shuffle(df[feature].values)

        # Conduct anova and write significant peaks to df
        p_vals = anova_for_all_peaks_with_adjustment(df, variables, interaction='double')
        results_permutation.loc[i] = tuple(p_vals.loc[c].dropna() for c in p_vals.index)

        # Display 100th rounds to give user information about process
        if i % 100 == 0:
            print(f'{i}th launch is done')

    return results_permutation
