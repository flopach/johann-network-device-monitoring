<div align="center">
  <img width="300" src="images/logo/johann-logo-full.png">
</div>

**johann** is a simple network device monitoring tool for **Cisco IOS XE devices**. Gather configuration and operational data of your networking device in a structured way!

## Features

* Add single or multiple devices (.csv file) at once to the johann database
* Show device information on a structured web-dashboard
* Update all device information
* Toolset:
	* Enable RESTCONF on a single IOS XE device
	* Test RESTCONF: Get current configuration in JSON format
	* Show logs

### Supported Devices

* ASR 1000
* ASR 900 RSP2/RSP3, ASR 920, NCS 520 and NCS 4200
* Catalyst 9200,9300,9400,9500,9600,9800
* Catalyst 8000V
* CSR 1000v
* ESS 3x00
* IR 1101
* IE 3x00
* ISR 1000
* ISR 4000

## Installation

johann is easy installable with Docker Compose:

```
git clone https://github.com/flopach/johann-network-device-monitoring
cd johann-network-device-monitoring/docker
docker compose up
```

After nginx has started, you can access the web-dashboard via [http://localhost](http://localhost).

## Built With

* Django
* Redis
* [Cisco UI Kit](https://developer.cisco.com/site/uiux/)
* jQuery
* Featured Python Libraries: Requests, Netmiko

## Versioning

**0.1.0pre** - Pre-Alpha Release

## Authors

* **Florian Pachinger** - *Initial work* - [flopach](https://github.com/flopach)

## License

This project is licensed under the Cisco Sample Code License 1.1 - see the [LICENSE.md](LICENSE.md) file for details

## Further Links

* [Cisco DevNet Website](https://developer.cisco.com)