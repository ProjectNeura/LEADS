import numpy as _numpy

mean: type[_numpy.mean] = _numpy.mean
array: type[_numpy.array] = _numpy.array
norm: type[_numpy.linalg.norm] = _numpy.linalg.norm

import pandas as _pandas

read_csv: type[_pandas.read_csv] = _pandas.read_csv
DataFrame: type[_pandas.DataFrame] = _pandas.DataFrame
TextFileReader: type[_pandas.io.parsers.TextFileReader] = _pandas.io.parsers.TextFileReader
