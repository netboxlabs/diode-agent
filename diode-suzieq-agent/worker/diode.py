"""
This module contains the logic of the writer for the 'logging' mode
"""
import logging, json

from suzieq.poller.worker.writers.output_worker import OutputWorker

logger = logging.getLogger(__name__)
LOGGING_THRESHOLD=16384

class LoggingOutputWorker(OutputWorker):
    """LoggingOutputWorker is used to write poller output as logs
    """
    def __init__(self, **kwargs):
        self.data_directory = kwargs.get('data_dir')

    def split_logging(self, data, topic):
        json_str = json.dumps(data)
        if len(json_str) <= LOGGING_THRESHOLD:
            logger.warning(json_str)
            return
        half = len(data[topic]) // 2
        if not half:
            logger.error("Not able to logging out. Huge output data for topic '%s'", topic)
            return
        data_left = {topic:data[topic][:half]}
        data_right = {topic:data[topic][half:]}
        self.split_logging(data_left, topic)
        self.split_logging(data_right, topic)

    def write_data(self, data):
        """Write the output of the commands into stdout

        Args:
            data (Dict): dictionary containing the data to store.
        """
        if not data["records"]:
            return

        ret_val = {data["topic"]:[]}
        for record in data["records"]:
            ret_val[data["topic"]].append(record)
        self.split_logging(ret_val, data["topic"])