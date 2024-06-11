# diode-napalm-agent

This is an example agent that demonstrates how NAPALM can be used to ingest information to NetBox by using `diode-sdk-python`

# Quickstart

This is a basic set of instructions on how to get started using Diode on your local machine.

## Requirements

- napalm==5.0.0
- netboxlabs-diode-sdk==0.1.0
- pydantic==2.7.1
- python-dotenv==1.0.1

## Usage

Firstly, you should clone the repository and install the agent 
```bash
git clone https://github.com/netboxlabs/diode-agent.git
cd diode-agent/
pip install ./diode-napalm-agent --no-cache-dir
```

Then, you can run `diode-napalm-agent`

```
usage: diode-napalm-agent [-h] [-V] -c config.yaml [-e .env] [-w N]
```

Simple example:
```bash
diode-napalm-agent -c config.yaml
```

### Create a `config.yaml` for your discovery

The `config.yaml` needs to be updated with an inventory of devices to be discovered. The file will look something like this, where the `data` section needs to be populated with the list of devices and their credentials that you want to have discovered. The config session should be filled with your diode server information.

You can pass environment variables e.g. `${ENV}`, so they will be resolved at parsing time. Also, if `driver` is not specified, diode napalm agent will try to find the best match for it.

```yaml
diode:
  config:
    target: grpc://localhost:8081
    api_key: ${API_KEY}
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

The detailed information for `optional_args` can be found in NAPALM [documentation](https://napalm.readthedocs.io/en/latest/support/#optional-arguments).

### Supported drivers
The default supported drivers are the ones that are natively supported by [napalm](https://napalm.readthedocs.io/en/latest/#supported-network-operating-systems).
- Arista EOS ("eos")
- Cisco IOS ("ios")
- Cisco IOS-XR ("iosxr")
- Cisco NX-OS ("nxos")
- Juniper JunOS ("junos")