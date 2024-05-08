import logging

import pandas as pd
import pyarrow as pa
from typing import List
from suzieq.db.base_db import SqDB

class SqLoggingDB(SqDB):
    '''Class supporting logging backend as DB'''

    def __init__(self, cfg: dict, logger: logging.Logger) -> None:
        self.cfg = cfg
        self.logger = logger or logging.getLogger()
    
    def get_tables(self):
        return

    def read(self, table_name: str, data_format: str,
             **kwargs) -> pd.DataFrame:
        fields = kwargs.pop("columns")
        final_df = pd.DataFrame()
        cols = set(final_df.columns.tolist() + final_df.index.names)
        for fld in [x for x in fields if x not in cols]:
            final_df[fld] = None
        return final_df.reset_index()[fields]

    def write(self, table_name: str, data_format: str,
              data, coalesced: bool, schema: pa.lib.Schema, **kwargs) -> int:
        return 0


    def coalesce(self, tables: List[str] = None, period: str = '',
                 ign_sqpoller: bool = False) -> None:
        return