
import argparse
import asyncio
import sys
import traceback
from types import SimpleNamespace

from netboxlabs.diode.sdk import DiodeClient
from suzieq.poller.controller.controller import Controller
from suzieq.poller.worker.writers.output_worker import OutputWorker
from suzieq.shared.exceptions import InventorySourceError, PollingError, SqPollerConfError
from suzieq.shared.utils import (poller_log_params, init_logger, print_version,log_suzieq_info)

async def start_agent():
    print("eita")
    try:
        logfile, loglevel, logsize, log_stdout = poller_log_params({},is_controller=True
        )
        logger = init_logger('suzieq.poller.controller', logfile,
                         loglevel, logsize, log_stdout)
        log_suzieq_info('Poller Controller', logger, show_more=True)
        
        cfg = {"data-directory" : "/tmp", "service-directory":"/tmp", "poller": {"logging-level":"WARNING","period":30,"connect-timeout":20, "log-stdout":True} }
        args = SimpleNamespace(run_once = "update", input_dir = False, debug=False, no_coalescer=True, update_period=3600, workers = 2, service_only=False,exclude_services=False)
        controller = Controller(args, cfg)
        controller.init()
        await controller.run()
    except (SqPollerConfError, InventorySourceError, PollingError) as error:
        if not log_stdout:
            print(f"ERROR: {error}")
        logger.error(error)
        sys.exit(1)
    except Exception as error:
        if not log_stdout:
            traceback.print_exc()
        logger.critical(f'{error}\n{traceback.format_exc()}')
        sys.exit(1)
    
    

def agent_main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '-V',
        '--version',
        action='store_true',
        help='Print suzieq version'
    )
    
    OutputWorker.get_plugins()
    
    args = parser.parse_args()
    if args.version:
        print_version()
        sys.exit(0)
    try:
        asyncio.run(start_agent())
    except (KeyboardInterrupt, RuntimeError):
        pass
    


if __name__ == '__main__':
    agent_main()
    
    
    
    # 	sOptions := []string{
	# 	"-I",
	# 	s.inventoryPath,
	# 	"-o",
	# 	"logging",
	# 	"--no-coalescer",
	# 	"--run-once",
	# 	"update",
	# }