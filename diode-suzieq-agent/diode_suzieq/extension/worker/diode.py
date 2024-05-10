"""
This module contains the logic of the writer for the 'diode' mode
"""
import logging

from suzieq.poller.worker.writers.output_worker import OutputWorker
#from diode_suzieq.client import Client ModuleNotFoundError

logger = logging.getLogger(__name__)

class DiodeOutputWorker(OutputWorker):
    """DiodeOutputWorker is used to write poller output to diode server
    """
    def __init__(self, **kwargs):
        self.data_directory = kwargs.get('data_dir')
        #self.client = Client()

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
      #  self.client.ingest(ret_val)
        
        