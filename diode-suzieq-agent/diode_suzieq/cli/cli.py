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
from diode_suzieq.client import Client
from diode_suzieq.parser import parse_config, ParseException
from diode_suzieq.version import version_semver
from diode_suzieq.extension import install_sq_diode
import netboxlabs.diode.sdk.version as SdkVersion

from suzieq.poller.controller.controller import Controller
from suzieq.shared.exceptions import InventorySourceError, PollingError, SqPollerConfError

from suzieq.shared.utils import (
    poller_log_params, init_logger, log_suzieq_info, validate_sq_config)

SUZIEQ_CONFIG_FILE = "suzieq-cfg.yml"
TMP_DIR = tempfile.gettempdir()


def get_inventory_path(policy_name: str):
    return f"{TMP_DIR}/inventory_{policy_name}.yaml"


def parse_config_file(cfile: Path):
    try:
        with open(cfile, "r") as f:
            cfg = parse_config(f.read())
    except ParseException as e:
        sys.exit(e.args[1])
    except Exception as e:
        sys.exit(f"ERROR: Unable to open config file {cfile}: {e.args[1]}")

    diode = cfg.diode

    if len(diode.policies) > 1:
        sys.exit(f"ERROR: agent currently supports single policy only")

    # dump inventory to file
    for policy_name in diode.policies:
        inventory_file = get_inventory_path(policy_name)
        try:
            with open(inventory_file, "w") as f:
                yaml.dump(
                    diode.policies[policy_name].data.inventory, f, allow_unicode=True)
            SINGLE_INVENTORY_PATH = inventory_file
        except Exception as e:
            sys.exit(f"ERROR: Unable to save {inventory_file}: {e.args[1]}")
    return diode


def dump_sq_config_file():
    # Parameters to be stored in SUZIEQ_CONFIG_FILE
    cfg = {"data-directory": TMP_DIR, "poller": {
        "logging-level": "WARNING", "period": 30, "connect-timeout": 20, "log-stdout": True}}
    validate_sq_config(cfg)
    config_path = f"{TMP_DIR}/{SUZIEQ_CONFIG_FILE}"
    with open(config_path, "w") as file:
        yaml.dump(cfg, file, allow_unicode=True)

    return cfg, config_path


async def start_agent(cfg):
    try:
        logfile, loglevel, logsize, log_stdout = poller_log_params({}, is_controller=True
                                                                   )
        logger = init_logger('suzieq.poller.controller', logfile,
                             loglevel, logsize, log_stdout)
        log_suzieq_info('Poller Controller', logger, show_more=True)

        # start diode client
        client = Client()
        client.init_client(target=cfg.config.target,
                           api_key=cfg.config.api_key,
                           tls_verify=cfg.config.tls_verify)

        sq_config, sq_config_path = dump_sq_config_file()

        for policy_name in cfg.policies:
            inventory_path = get_inventory_path(policy_name)

        # This arguments is what is passed
        args = SimpleNamespace(run_once="update", input_dir=False, debug=False, no_coalescer=True,
                               update_period=3600, workers=2, service_only=False, exclude_services=False,
                               inventory=inventory_path, outputs="diode", config=sq_config_path,
                               output_dir=None, ssh_config_file=None)

        controller = Controller(args, sq_config)
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

    config = parse_config_file(Path(args.config))
    install_sq_diode()

    try:
        asyncio.run(start_agent(config))
    except (KeyboardInterrupt, RuntimeError):
        pass


if __name__ == '__main__':
    agent_main()
