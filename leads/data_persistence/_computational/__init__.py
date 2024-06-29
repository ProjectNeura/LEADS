try:
    import cupy as _np
except ImportError:
    import numpy as _np
import pandas as _pandas

mean: type[_np.mean] = _np.mean
array: type[_np.array] = _np.array
ndarray: type[_np.array] = _np.ndarray
norm: type[_np.linalg.norm] = _np.linalg.norm
sqrt: type[_np.sqrt] = _np.sqrt
minimum: type[_np.min] = _np.min
maximum: type[_np.max] = _np.max

read_csv: type[_pandas.read_csv] = _pandas.read_csv
DataFrame: type[_pandas.DataFrame] = _pandas.DataFrame
TextFileReader: type[_pandas.io.parsers.TextFileReader] = _pandas.io.parsers.TextFileReader
