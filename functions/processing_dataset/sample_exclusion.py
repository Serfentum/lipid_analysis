def exclude(df, excluded_samples):
    """
    Remove some sample columns
    :param df: df - dataframe
    :param excluded_samples: list - list with samples to exclude
    :return: df - dataframe without excluded columns
    """
    df = df.copy()
    # Exclusion
    included = ~df.loc['id'].isin(excluded_samples)
    df = df.loc[:, included]
    return df