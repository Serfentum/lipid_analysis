import numpy as np
import pandas as pd
import re


# MANUAL
# Divide columns into groups
# Load data
name = '../../vitaminD/cleaned_contaminants_xs_annotated_rats_neg.csv'
df = pd.read_csv(name, index_col=0)

# Blank controls
pat = re.compile(r'blank', re.I)
blanks = df.filter(regex=pat).columns

# Quality controls
pat = re.compile(r'qc', re.I)
qc_controls = df.filter(regex=pat).columns

# Washes
pat = re.compile(r'wash', re.I)
washes = df.filter(regex=pat).columns

# Diverse columns without concentration
other_columns = {'mz', 'mzmin', 'mzmax', 'rt', 'rtmin', 'rtmax', 'npeaks',
                 'samples', 'isotopes', 'adduct', 'pcgroup'}

# All samples including controls and without all of them except qc
samples = list(set(df.columns).difference(other_columns))

samples_wo_controls_qc = list(set(samples).difference(blanks)
                                          .difference(washes))