import numpy as np
import pandas as pd
from itertools import product
import string


# It is unnecessary if metadata always contains tissue, which can be joined via identificator
brain_regions = ['precuneus', 'amygdala ', 'hippocampus', 'caudate ', 'putamen',
                 'thalamus ', 'hypothalamus', 'cb', 'pfc', 'pmc', 'claustrum', 'striatum',
                 'hippocamp','cb-gm', 'ba40a', 'ba7p', 'ba7a', 'ba29/30', 'ba37-amt', 'ba47', 'ba23a',
                 'pop', 'ba18/19p', 'ba21p', 'ba6p', 'ba6prc', 'ba17p', 'ba4', 'ba41/42',
                 'ba17a', 'ba3/1/2', 'ba37-pmt', 'ba37m', 'ba8', 'ba6m', 'insa', 'ba23p',
                 'ba20p', 'ba22a', 'ba18/19a', 'ba22p', 'ba7m', 'ba6a', 'ba40p', 'ba44',
                 'ba20a', 'ba9', 'ba9m', 'ba8m', 'ba21a', 'ba10', 'ba10fp', 'ba32g', 'ba39',
                 'ba25', 'ba38', 'ba46', 'ba45', 'ba10m', 'ba31', 'ba24', 'ba32', 'ba11',
                 'pirctx', 'amg', 'insp', 'entctx', 'ca3/dg', 'nacc', 'caud', 'put', 'dentn',
                 'supcll', 'pulth', 'rn', 'sn', 'gp', 'ca1', 'sub', 'vath', 'mdth', 'hyp',
                 'vlth', 'ec', 'ic', 'cca', 'ccp', 'cb-wm']
other_tissues = ['brain', 'plasma', 'muscle', 'liver', 'epithelium',
                 'endoneurium', 'perineurium', 'epineurium', 'vascular',
                 'connective', 'lymphoid', 'meristem', 'qc']
some_punct = ['.', '_', '|', '$', '#', '@']

# Create combinations of brain and region separated by something
brain_encodings = list(''.join(x) for x in product(['brain'], some_punct, brain_regions))

# List of tissue names
tissues = brain_encodings + other_tissues + brain_regions


def create_labels_tissue(samples, labs=tissues, name='tissue', punct=string.punctuation):
    """
    Create series with tissue name
    :param samples: iterable - collection of samples names in original dataframe
    :param labs: iterable - collection of new appropriate names of samples which express some category, e.g. tissue
    :param name: str - name of series, tissue by default
    :param punct: iterable - collection of possible separators in original names
    :return: series - series with tissue affiliation of samples
    """
    res = create_labels(samples, labs, punct)
    res.name = name
    return res


def create_labels(samples, labs, punct=string.punctuation):
    """
    Create series with new names of samples
    :param samples: iterable - collection of samples names in original dataframe
    :param labs: iterable - collection of new appropriate names of samples which express some category, e.g. tissue
    :param punct: iterable - collection of possible separators in original names
    :return: series - series with new names of samples
    """
    # Create list to store labels
    res = []

    # Find appropriate name of type for sample
    # Make it '_' separated and add it to list with labels
    # Add NA if no matches with labs were found
    for sample in samples:
        for lab in labs:
            if lab in sample.lower():
                lab = punct_check(lab, punct)
                res.append(lab)
                break
        else:
            res.append(np.nan)

    # Create a series
    res = pd.Series({c: v for c, v in zip(samples, res)})
    return res


def punct_check(label, punct):
    """
    Replace arbitrary separator by '_' in label name
    :param label: str - label name
    :param punct: iterable - collection of possible separators
    :return: str - cleaned label
    """
    # For all separators in punct check its presence in label
    # Replace separator with '_' if it is in label
    for mark in punct:
        if mark in label:
            return label.replace(mark, '_')
    return label