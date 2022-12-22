<div align="center">
  <img width="300" src="images/logo/johann-logo-full.png">
</div>
<p align="center">
  <a href="https://developer.cisco.com/codeexchange/github/repo/flopach/johann-network-device-monitoring">
    <img src="https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg" alt="DevNet Published">
  </a>
</p>

**johann** is a web-based network device monitoring tool for **Cisco IOS XE devices**. Collect configuration and operational data of your networking devices in a structured way in one single database!

**Get an Overview in this YouTube Video:**

[![Get an Overview in this YouTube Video](https://img.youtube.com/vi/qsJvul6yLBE/mqdefault.jpg)](https://youtu.be/qsJvul6yLBE)


## johann Architecture

![](images/johann-teaser.png)

Take a **look behind the scenes** of johann in the blog series at [https://blogs.cisco.com/tag/johann](https://blogs.cisco.com/tag/johann).

## Features

* Add single or multiple devices (.csv file) at once to the johann SQLite database
* Show device information on a structured web-dashboard
* Update all device information
* Show simple report graphs
* Export database as .xlsx
* Toolset:
	* Enable RESTCONF on a single IOS XE device
	* Test RESTCONF: Get current configuration in JSON format
	* Show logs

### Supported Devices*

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

_*RESTCONF needs to be supported in the IOS XE version!_

## Installation

johann is easy installable:

1. Install Docker Engine and [Docker Compose](https://docs.docker.com/compose/install/) (already included on macOS and Windows)

2. Then copy & paste into terminal (on Linux you may need to start Docker with a [non-root user](https://docs.docker.com/engine/install/linux-postinstall/)):

```
git clone https://github.com/flopach/johann-network-device-monitoring &&
cd johann-network-device-monitoring/docker/ &&
docker-compose up
```

After all containers are up, you can access the web-dashboard via [http://localhost](http://localhost).

## Demo GIF

![](images/johann-0.1.0-gif.gif)

*(size: 11MB)*

## Screenshots

| | | |
|:-------------------------:|:-------------------------:|:-------------------------:|
|![](images/scr_add.png) |  ![](images/scr_all.png) | ![](images/scr_detail.png) |
|![](images/scr_detail2.png)  |  ![](images/scr_report.png) |![](images/scr_json.png) |

## FAQs

**Are only IOS XE devices supported?** - For now, yes only IOS XE devices.

**What YANG modules do you use?** - Cisco IOS-XE native YANG models only.

**johann does not get _______ operational/configuration data!** - Feel free to add it or send a feature request.

**Why is some information empty in the johann database?** - The RESTCONF interface of the device did not provide this information.

**What is the password for Database admin?** - You can set the Django superuser in the ./docker/johann/Dockerfile. The default is admin/admin123 to acess the database.

**johann does not support ______ !** - Please put in a feature request of feel free to add this feature!

**When stopping Docker, what data will be saved? And where?** - The whole SQLite database and .log file will be saved in `docker/johann/stickydata/`.

## Known Limitations

* Currently, only timezone UTC is supported
* Devices can only be deleted via Django Database Manager 
* Passwords are not encrypted in the database 

## Technical Deep-Dive

**High-level architecture**

![](images/high-level-architecture.png)

**Sequence diagram for adding devices**

![](images/sequencediagram_add_device.png)

## Built With

* Django + Django Channels
* Redis
* [Cisco UI Kit](https://developer.cisco.com/site/uiux/)
* jQuery
* Featured Python Libraries: Requests, Netmiko (just for enabling RESTCONF), Matplotlib

## Versioning

**0.1.1 (22.12.2022)** - Open source version of johann

**0.1.0 (7.7.2021)** - Initial Release

## Authors

* **Florian Pachinger** - *Initial work* - [flopach](https://github.com/flopach)

## License

The project is licensed under the [Apache License version 2.0](LICENSE), except the fonts and CSS file. The OpenSans font is licensed under the [SIL Open Font License version 1.1](font.LICENSE). The cui-font and CSS file is copyright by Cisco (see [terms and conditions](http://cisco.com/en/US/swassets/sw293/sitewide_important_notices.html)).

## Further Links

* [Cisco DevNet Website](https://developer.cisco.com)
* [YouTube Video](https://youtu.be/qsJvul6yLBE)
