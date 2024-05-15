try:
    import cupy as _np
except ImportError:
    import numpy as _np

mean: type[_np.mean] = _np.mean
array: type[_np.array] = _np.array
norm: type[_np.linalg.norm] = _np.linalg.norm
sin: type[_np.sin] = _np.sin
arcsin: type[_np.arcsin] = _np.arcsin
cos: type[_np.cos] = _np.cos
arccos: type[_np.arccos] = _np.arccos
tan: type[_np.tan] = _np.tan
arctan: type[_np.arctan] = _np.arctan

import pandas as _pandas

read_csv: type[_pandas.read_csv] = _pandas.read_csv
DataFrame: type[_pandas.DataFrame] = _pandas.DataFrame
TextFileReader: type[_pandas.io.parsers.TextFileReader] = _pandas.io.parsers.TextFileReader
