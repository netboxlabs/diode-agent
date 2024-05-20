# diode-napalm-agent

This is an example agent that demonstrates how NAPALM can be used to ingest information to NetBox by using `diode-sdk-python`

# Quickstart

This is a basic set of instructions on how to get started using Diode on your local machine.

## Requirements

- Napalm version 5.0.0
- Diode Python SDK
- Pydantic

### Create a `config.yml` for your discovery

The `config.yml` needs to be updated with an inventory of devices to be discovered. The file will look something like this, where the `data` section needs to be populated with the list of devices and their credentials that you want to have discovered. The config session should be filled with your diode server information.

```yaml
diode:
  config:
    target: localhost:8081
    api_key: abcde
    tls_verify: false
  policies:  
    discovery_1:
      config:
        netbox:
          site: New York NY
      data:
        - driver: eos
          username: 127.0.0.1
          password: admin
          hostname: admin
          optional_args:
            enable_password: admin
        - driver: ios
          username: 127.0.0.1
          password: admin
          hostname: admin
```

The detailed information for `optional_args` can be found in NAPALM [documentation](https://napalm.readthedocs.io/en/latest/support/#optional-arguments).