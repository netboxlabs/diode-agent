#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""NetBox Labs - extension namespace."""

import os
import shutil
from pathlib import Path

from suzieq.db.base_db import SqDB
from suzieq.poller.worker.writers.output_worker import OutputWorker
from suzieq.shared.utils import get_sq_install_dir

WORKER_FILE = "diode.py"
WORKER_FOLDER = Path("worker")
DB_FOLDER = Path("db")


def install_sq_diode():
    sq_install_dir = '/'.join(get_sq_install_dir().split('/')[:-1])
    extension_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
    # install custom worker to suzieq worker install path
    worker_pkg = '.'.join(OutputWorker.__module__.split('.')[:-1])
    install_path = (f"{sq_install_dir}/{worker_pkg.replace('.', '/')}")
    shutil.copy(f"{extension_dir}/{WORKER_FOLDER}/{WORKER_FILE}",
                f"{install_path}/{WORKER_FILE}")
    # install dummy db to suzieq db install path
    db_pkg = '.'.join(SqDB.__module__.split('.')[:-1])
    install_path = (f"{sq_install_dir}/{db_pkg.replace('.', '/')}")
    print(install_path)
    print(f"{extension_dir}/{DB_FOLDER}")
    shutil.copytree(f"{extension_dir}/{DB_FOLDER}",
                    install_path, dirs_exist_ok=True)
    return
