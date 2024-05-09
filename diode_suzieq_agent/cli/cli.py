#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc

import argparse
import asyncio
import sys
import traceback
import yaml
import tempfile
from types import SimpleNamespace
from pathlib import Path


from suzieq.version import SUZIEQ_VERSION
from diode_suzieq_agent.version import version_semver
from diode_suzieq_agent.extension import install_sq_diode
import netboxlabs.diode.sdk.version as SdkVersion

from suzieq.poller.controller.controller import Controller
from suzieq.shared.exceptions import InventorySourceError, PollingError, SqPollerConfError
# from netboxlabs.diode.sdk import DiodeClient

from suzieq.shared.utils import (
    poller_log_params, init_logger, log_suzieq_info, validate_sq_config)

APP_NAME = "diode-suzieq-agent"
APP_VERSION = version_semver()
SUZIEQ_CONFIG_FILE = "suzieq-cfg.yml"


def parse_config_file(cfile: Path):
    try:
        with open(cfile, "r") as f:
            cfg = yaml.safe_load(f.read())
    except Exception as e:
        sys.exit(f"ERROR: Unable to open config file {cfile}: {e.args[1]}")

    cfg or sys.exit(f"ERROR: Empty config file {cfile}")

    isinstance(cfg, dict) or sys.exit(
        f"ERROR: Invalid config file format {cfile}")

    return cfg


async def start_agent(config: dict):
    try:
        # diode_client = DiodeClient(
        #     target="", app_name=APP_NAME, app_version=APP_VERSION)

        logfile, loglevel, logsize, log_stdout = poller_log_params({}, is_controller=True
                                                                   )
        logger = init_logger('suzieq.poller.controller', logfile,
                             loglevel, logsize, log_stdout)
        log_suzieq_info('Poller Controller', logger, show_more=True)
        # Parameters to be stored in SUZIEQ_CONFIG_FILE
        cfg = {"data-directory": tempfile.gettempdir(), "poller": {
            "logging-level": "WARNING", "period": 30, "connect-timeout": 20, "log-stdout": True}}
        validate_sq_config(cfg)
        config_path = f"{tempfile.gettempdir()}/{SUZIEQ_CONFIG_FILE}"
        with open(config_path, "w") as file:
            yaml.dump(cfg, file, allow_unicode=True)

        # This arguments is what is passed
        args = SimpleNamespace(run_once="update", input_dir=False, debug=False, no_coalescer=True,
                               update_period=3600, workers=2, service_only=False, exclude_services=False,
                               inventory="/workspaces/diode-agent/test.yaml", outputs="diode", config=config_path, output_dir=None, ssh_config_file=None)
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
    parser = argparse.ArgumentParser(description="Diode Agent for SuzieQ")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"Diode Agent version: {version_semver()}, SuzieQ version: {SUZIEQ_VERSION}, Diode SDK version: {SdkVersion.version_semver()}",
        help='Display Diode Agent, SuzieQ and Diode SDK versions'
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="config.yaml",
        help='Agent yaml configuration file',
        type=str, required=True
    )
    args = parser.parse_args()

    cfile = Path(args.config)
    cfile.is_file() or sys.exit(f"ERROR: \"{cfile}\" is not a file")
    str(cfile).lower().endswith(".yaml") or sys.exit(
        f"ERROR: \"{cfile}\" is not a yaml file")

    config = parse_config_file(cfile)

    install_sq_diode()
    try:
        asyncio.run(start_agent(config))
    except (KeyboardInterrupt, RuntimeError):
        pass


if __name__ == '__main__':
    agent_main()
