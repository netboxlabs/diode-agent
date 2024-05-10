# diode-suzieq-agent

This is an example agent that demonstrates how SuzieQ can be used to ingest information to NetBox by using `diode-sdk-python`

# Quickstart

This is a basic set of instructions on how to get started using Diode on your local machine using Docker.

## Requirements

- Due to SuzieQ limitation, it requires Python >3.8.1, <3.10 to run the agent

### Create a `config.yml` for your discovery

The `config.yml` needs to be updated with an inventory of devices to be discovered. The file will look something like this, where the `hosts:` section needs to be populated with the list of devices and their credentials that you want to have discovered. The config session should be filled with your diode server information.

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
        inventory: 
          sources:
            - name: default_inventory
              hosts:
                - url: ssh://1.2.3.4:2021 username=user password=password
                - url: ssh://resolvable.host.name username=user password=password
          devices:
            - name: default_devices
              transport: ssh
              ignore-known-hosts: true
              slow-host: true
          namespaces:
            - name: default_namespace
              source: default_inventory
              device: default_devices
```

The `inventory:` section of the `config.yml` follows the SuzieQ Inventory File Format. Please refer to the SuzieQ [documentation](https://suzieq.readthedocs.io/en/latest/inventory/) for additional details.