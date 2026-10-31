from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


def records_to_pandas(records: list[dict[str, Any]]) -> pd.DataFrame:
    """辞書リストをpandasのDataFrameへ変換します。

    pandasが未インストールの環境で呼び出された場合は、追加インストールの
    手順を明記したImportErrorを送出します。
    """
    try:
        pd = importlib.import_module("pandas")
    except ImportError as err:
        raise ImportError(
            "to_pandas()を利用するにはpandasが必要です。"
            "pip install 'irbkpy[pandas]' を実行してインストールしてください。"
        ) from err
    return pd.DataFrame(records)


def records_to_polars(records: list[dict[str, Any]]) -> pl.DataFrame:
    """辞書リストをpolarsのDataFrameへ変換します。

    polarsが未インストールの環境で呼び出された場合は、追加インストールの
    手順を明記したImportErrorを送出します。
    """
    try:
        pl = importlib.import_module("polars")
    except ImportError as err:
        raise ImportError(
            "to_polars()を利用するにはpolarsが必要です。"
            "pip install 'irbkpy[polars]' を実行してインストールしてください。"
        ) from err
    return pl.DataFrame(records)
