# Diode NAPALM Agent

The Diode Ping Agent is a lightweight network device discovery tool that uses ping to streamline IPAM data entry into NetBox through the [Diode](https://github.com/netboxlabs/diode) ingestion service.

# Get started

This is a basic set of instructions to get started using Diode NAPALM agent on a local machine.

## Requirements

The Diode Ping Agent requires a Python runtime environment and has the following requirements:
- ping3==4.0.8
- netboxlabs-diode-sdk==0.2.0
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
pip install ./diode-ping-agent --no-cache-dir
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
      interface: eth0
      network: 192.168.0.1/24
```

Variables (using `${ENV}` syntax) can be referenced in the configuration file from environmental variables or from a provided `.env` file.

The `interface` attribute is optional. If not specified, the agent will attempt to find the most used interface in the host machine.
The `network` attribute is optional. If not specified, the agent will attempt to find ip range based on the specified interface.


## Running the agent

Usage:

```
usage: diode-ping-agent [-h] [-V] -c config.yaml [-e .env]

Diode Ping Agent

options:
  -h, --help            show this help message and exit
  -V, --version         Display Diode Agent and Diode SDK versions
  -c config.yaml, --config config.yaml
                        Agent yaml configuration file
  -e .env, --env .env   File containing environment variables
```

Run `diode-ping-agent` with a discovery configuration file named `config.yaml`:

```bash
diode-napalm-agent -c config.yaml
```

### Supported Netbox Object Types

The Diode Ping agent tries to fetch information from network devices about the following NetBox object types:

- [IPAM.IPAddress](https://netboxlabs.com/docs/netbox/en/stable/models/ipam/ipaddress/)
- [IPAM.Prefix](https://netboxlabs.com/docs/netbox/en/stable/models/ipam/prefix/)

## License

Distributed under the Apache 2.0 License. See [LICENSE](./LICENSE) for more information.
