import cupy as _cupy

mean: type[_cupy.mean] = _cupy.mean
array: type[_cupy.array] = _cupy.array
norm: type[_cupy.linalg.norm] = _cupy.linalg.norm

import pandas as _cudf

read_csv: type[_cudf.read_csv] = _cudf.read_csv
DataFrame: type[_cudf.DataFrame] = _cudf.DataFrame
TextFileReader: type[_cudf.io.parsers.TextFileReader] = _cudf.io.parsers.TextFileReader
