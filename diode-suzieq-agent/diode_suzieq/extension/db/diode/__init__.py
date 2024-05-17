#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Dummy Diode DB"""

import logging
from suzieq.db.diode.diodedb import SqDiodeDB

def get_sqdb(cfg: dict, logger: logging.Logger) -> SqDiodeDB:
    """Return the diode db engine for the appropriate table

    :param cfg: dict, Suzieq configuration dictionary
    :param logger: logging.Logger, logger to hook into for logging, can be None
    :returns: a logging database engine to use for read/wr, other DB ops
    :rtype: SqDiodeDB

    """
    return SqDiodeDB(cfg, logger)

__all__ = ['get_sqdb']