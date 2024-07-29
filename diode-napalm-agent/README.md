# Diode NAPALM Agent

The Diode NAPALM Agent is a lightweight network device discovery tool that uses [NAPALM](https://github.com/napalm-automation/napalm) to streamline data entry into NetBox through the [Diode](https://github.com/netboxlabs/diode) ingestion service.

# Get started

This is a basic set of instructions to get started using Diode NAPALM agent on a local machine.

## Requirements

The Diode NAPALM Agent requires a Python runtime environment and has the following requirements:
- napalm==5.0.0
- netboxlabs-diode-sdk==0.1.0
- pydantic==2.7.1
- python-dotenv==1.0.1

Instructions on installing the Diode SDK Python can be found [here](https://github.com/netboxlabs/diode-sdk-python).

## Installation

Clone the agent repository:

```bash
git clone https://github.com/netboxlabs/diode-agent.git
cd diode-agent/
```

Create a Python virtual environment and install the agent:

```bash
python3 -m venv venv
source venv/bin/activate
pip install ./diode-napalm-agent --no-cache-dir
```

### Create a discovery configuration file

A configuration file needs to be created with an inventory of devices to be discovered. An example (`config.sample.yaml`) is provided in the agent repository. The `config` section needs to be updated to reflect your Diode server environment and the `data` section should include a list of all devices (and their credentials) to be discovered.

```yaml
diode:
  config:
    target: grpc://localhost:8081
    api_key: ${DIODE_API_KEY}
  policies:
    discovery_1:
      config:
        netbox:
          site: New York NY
      data:
        - hostname: 192.168.0.32
          username: ${USER}
          password: admin
        - driver: eos
          hostname: 127.0.0.1
          username: admin
          password: ${ARISTA_PASSWORD}
          optional_args:
            enable_password: ${ARISTA_PASSWORD}
```

Variables (using `${ENV}` syntax) can be referenced in the configuration file from environmental variables or from a provided `.env` file.

The `driver` device attribute is optional. If not specified, the agent will attempt to find a match from NAPALM supported/installed drivers.

Detailed information about `optional_args` can be found in the NAPALM [documentation](https://napalm.readthedocs.io/en/latest/support/#optional-arguments).


## Running the agent

Usage:

```
usage: diode-napalm-agent [-h] [-V] -c config.yaml [-e .env] [-w N]

Diode Agent for NAPALM

options:
  -h, --help            show this help message and exit
  -V, --version         Display Diode Agent, NAPALM and Diode SDK versions
  -c config.yaml, --config config.yaml
                        Agent yaml configuration file
  -e .env, --env .env   File containing environment variables
  -w N, --workers N     Number of workers to be used
```

Run `diode-napalm-agent` with a discovery configuration file named `config.yaml`:

```bash
diode-napalm-agent -c config.yaml
```

### Supported drivers

The default supported drivers are the natively supported [NAPALM](https://napalm.readthedocs.io/en/latest/#supported-network-operating-systems) drivers:

- Arista EOS ("eos")
- Cisco IOS ("ios")
- Cisco IOS-XR ("iosxr")
- Cisco NX-OS ("nxos")
- Juniper JunOS ("junos")

Moreover, if a NAPALM [community driver](https://github.com/napalm-automation-community) is installed in the environment, it can be used in the agent's policy and also in automatic driver matching when none are specified.

### Supported Netbox Object Types

Currently, once napalm agent connects to a network device, it tries to fetch and ingest to Diode the following Netbox Object Types:

- [DCIM.Device](https://netboxlabs.com/docs/netbox/en/stable/models/dcim/device/)
- [DCIM.DeviceType](https://netboxlabs.com/docs/netbox/en/stable/models/dcim/devicetype/)
- [DCIM.Interface](https://netboxlabs.com/docs/netbox/en/stable/models/dcim/interface/)
- [DCIM.Platform](https://netboxlabs.com/docs/netbox/en/stable/models/dcim/platform/)
- [IPAM.IPAddress](https://netboxlabs.com/docs/netbox/en/stable/models/ipam/ipaddress/)
- [IPAM.Prefix](https://netboxlabs.com/docs/netbox/en/stable/models/ipam/prefix/)

## License

Distributed under the Apache 2.0 License. See [LICENSE.txt](./diode-proto/LICENSE.txt) for more information.
