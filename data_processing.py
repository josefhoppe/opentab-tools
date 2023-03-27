"""
Utility functions to process data
"""

import pandas as pd

def map_column_names(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """
    Maps a DataFrames columns to make them more usable in a program.
    col_map: dictionary of 'new_col_name' -> "old complicated column name"
    """
    reg_data = {}
    for new_col, old_col in col_map.items():
        reg_data[new_col] = df[old_col]

    return pd.DataFrame(reg_data)