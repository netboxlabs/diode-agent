import logging
from suzieq.db.logging.loggingdb import SqLoggingDB

def get_sqdb(cfg: dict, logger: logging.Logger) -> SqLoggingDB:
    """Return the logging db engine for the appropriate table

    :param cfg: dict, Suzieq configuration dictionary
    :param logger: logging.Logger, logger to hook into for logging, can be None
    :returns: a logging database engine to use for read/wr, other DB ops
    :rtype: SqLoggingDB

    """
    return SqLoggingDB(cfg, logger)

__all__ = ['get_sqdb']