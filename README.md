# LEADS: Lightweight Embedded Assisted Driving System

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/ProjectNeura/LEADS)
![PyPI](https://img.shields.io/pypi/v/leads)
![PyPI - Downloads](https://img.shields.io/pypi/dm/leads)
![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/ProjectNeura/LEADS)

LEADS is a lightweight embedded assisted driving system. It is designed to simplify the development of the
instrumentation and control system for electric vehicles. It is written in well-organized Python and C/C++ with
impressive performance. It is not only plug-and-play
(the [VeC Project](https://www.villanovacollege.org/giving/vec-project)) but also fully customizable. It provides
multiple abstract layers that allow users to pull out the components and rearrange them into a new project. You can
either configure the existing executable module `leads_vec` and `leads_vec_rc` simply through a JSON file or write your
own codes based on the framework as easily as building a LEGO.

The hardware components chosen for this project are geared towards amateur developers. It uses neither a CAN bus nor any
dedicated circuit board, but generic development kits such as Raspberry Pi and Arduino instead. However, as it is a
high-level system running on a host computer, the software framework has the ability to adapt to any type of hardware
component if you are willing to write some codes.

This document will guide you through LEADS VeC. You will find a detailed
version [here](https://leads-docs.projectneura.org/en/latest/vec).

LEADS VeC Demo

![demo](docs/assets/demo.png)

LEADS VeC Demo (Manual Mode)

![demo](docs/assets/demo-manual.png)

:link: [Docs](https://leads-docs.projectneura.org)

:link: [Remote Analyst Online Dashboard](https://leads-vec-rc.projectneura.org)

## Key Features

- [x] Modern UI design
- [x] Auto dark mode support
- [x] Fancy widgets
- [x] TCP communication system
- [x] Remote analyst
- [x] Replaying recorded data
- [ ] Data recording system with the following components
    - [x] A speed recording system
    - [ ] A G force recording system
    - [x] A GPS recording system
    - [x] A battery voltage recording system
- [ ] ESC with the following components
    - [x] DTCS (Dynamic Traction Control System)
    - [x] ABS (Anti-lock Braking System)
    - [ ] EBI (Emergency Braking Intervention)
    - [ ] ATBS (Automatic Trail Braking System)

## To High School Students

The codes are never designed for average high school students to understand. You may find it hard to read the codes if
you do not satisfy the following requirements of skills and knowledge.

- Advanced Python knowledge (you should be familiar with everything and even programming philosophy in Python)
- Solid knowledge of Physics (you should understand how a car moves in reality)
- Basic embedded development experience (C/C++, Raspberry Pi, Arduino, serial communication, PWM)
- Rich experience in Web development (React, Next.js, FastAPI, TCP/IP, sockets)
- Basic machine learning knowledge (linear regression, polynomial regression)

## Installation

### Python

Note that LEADS requires **Python >= 3.12**. To set up the environment on a Raspberry Pi by only a single line of
command, see [Environment Setup](#environment-setup).

```shell
pip install Pillow PySDL2 customtkinter gpiozero lgpio pynmea2 pynput pysdl2-dll pyserial leads
```

`numpy` and `pandas` will be automatically installed with `leads`.

`Pillow`, `PySDL2`, `customtkinter`, `gpiozero`, `lgpio`, `pynmea2`, `pynput`, `pysdl2-dll`, and `pyserial` are optional.

If you only want the framework, run the following.

```shell
pip install leads
```

#### Verify

```shell
python -m leads_vec info
```

### Arduino

You can install [LEADS-Arduino](https://github.com/ProjectNeura/LEADS-Arduino) from Arduino Library Manager. Note that
it is named "LEADS", not "LEADS-Arduino", in the index.

## LEADS Framework

See [Read the Docs](https://leads-docs.projectneura.org) for the documentation of how to customize and make use of
the framework in your project.

## Quick Start

### Main

```shell
python -m leads_vec run
```

#### Optional Arguments

Run the following to get a list of all the supported arguments.

```shell
python -m leads_vec -h
```

##### Specify a Configuration File

```shell
python -m leads_vec -c path/to/the/config/file.json run
```

If not specified, all configurations will be default values.

To learn about the configuration file, read [Configurations](#Configurations).

##### Specify a Devices Module

```shell
python -m leads_vec -d path/to/the/devices.py run
```

To learn about the devices module, read [Devices Module](#devices-module).

##### Generate a Configuration File

```shell
python -m leads_vec -r config run
```

This will generate a default "config.json" file under the current directory.

##### Register as a Systemd Service

```shell
python -m leads_vec -r systemd run
```

This will register a system service to start the program.

To enable auto-start at boot, run the following.

```shell
systemctl daemon-reload
systemctl enable leads_vec
```

##### Specify a Theme

```shell
python -m leads_vec -t path/to/the/theme.json run
```

To learn about themes, read [Color and Themes](https://customtkinter.tomschimansky.com/documentation/color).

##### Magnify Font Sizes

```shell
python -m leads_vec -mfs 1.5 run
```

This will magnify all font sizes by 1.5.

##### Use Emulation

```shell
python -m leads_vec --emu run
```

This will force the program to use emulation even if the environment is available.

##### Automatically Magnify Font Sizes

```shell
python -m leads_vec --auto-mfs run
```

Similar to [Magnify Font Sizes](#magnify-font-sizes), but instead of manually deciding the factor, the program will
automatically calculate the best factor to keep the original proportion as designed.

### Remote Analyst

```shell
python -m leads_vec_rc
```

Go to the online dashboard at https://leads-vec-rc.projectneura.org.

#### Optional Arguments

Run the following to get a list of all the supported arguments.

```shell
python -m leads_vec_rc -h
```

##### Server Port

```shell
python -m leads_vec_rc -p 80
```

If not specified, the port is `8000` by default.

##### Specify a Configuration File

```shell
python -m leads_vec_rc -c path/to/the/config/file.json
```

If not specified, all configurations will be default values.

To learn about the configuration file, read [Configurations](#configurations).

If you install Python using the scripts, you will not find `python ...`, `python3 ...`, `pip ...`, or `pip3 ...` working
because you have to specify the Python version such that `python3.12 ...` and `python3.12 -m pip ...`.

## Environment Setup

This section helps you set up the identical environment we have for the VeC project. A more detailed guide of
reproduction is available [here](https://leads-docs.projectneura.org/en/latest/vec), but first of all, we run an
Ubuntu 22.04 LTS on a Raspberry Pi 4 Model B 8GB. After the OS is set up, just run the one-line commands listed below.
You may also choose to clone the repository or download the scripts from
[releases](https://github.com/ProjectNeura/LEADS/releases) (only stable releases provide scripts).

You can simply run "[setup.sh](scripts/setup.sh)" and it will install everything including LEADS for you. If anything
goes wrong, you can also manually install everything.

```shell
/bin/sh "setup.sh$(wget -O setup.sh https://raw.githubusercontent.com/ProjectNeura/LEADS/master/scripts/setup.sh)" && rm setup.sh || rm setup.sh
```

We also use OBS Studio for streaming, but it is not required. If you want to install,
run "[obs-install.sh](scripts/obs-install.sh)".

```shell
/bin/sh "obs-install.sh$(wget -O obs-install.sh https://raw.githubusercontent.com/ProjectNeura/LEADS/master/scripts/obs-install.sh)" && rm obs-install.sh || rm obs-install.sh
```

Do not run the OBS Studio directly, instead, use "[obs-run.sh](scripts/obs-run.sh)".

```shell
wget -O obs-run.sh https://raw.githubusercontent.com/ProjectNeura/LEADS/master/scripts/obs-run.sh
/bin/sh obs-run.sh
```

## Configurations

The configuration is a JSON file that has the following settings. You can have an empty configuration file like the
following as all the settings are optional.

```json
{}
```

Note that a purely empty file could cause an error.

| Index               | Type    | Usage                                                     | Used By      | Default       |
|---------------------|---------|-----------------------------------------------------------|--------------|---------------|
| `w_debug_level`     | `str`   | `"DEBUG"`, `"INFO"`, `"WARN"`, `"ERROR"`                  | Main, Remote | `"DEBUG"`     |
| `data_seq_size`     | `int`   | Buffer size of history data                               | Main         | `100`         |
| `data_dir`          | `str`   | The directory for the data recording system               | Remote       | `"data"`      |
| `width`             | `int`   | Window width                                              | Main         | `720`         |
| `height`            | `int`   | Window height                                             | Main         | `480`         |
| `fullscreen`        | `bool`  | `True`: auto maximize; `False`: window mode               | Main         | `False`       |
| `no_title_bar`      | `bool`  | `True`: no title bar; `False`: default title bar          | Main         | `False`       |
| `theme_mode`        | `bool`  | `"system"`, `"light"`, `"dark`"                           | Main         | `False`       |
| `manual_mode`       | `bool`  | `True`: hide control system; `False`: show control system | Main         | `False`       |
| `refresh_rate`      | `int`   | GUI frame per second                                      | Main         | `30`          |
| `m_ratio`           | `float` | Meter widget size ratio                                   | Main         | `0.7`         |
| `font_size_small`   | `int`   | Small font size                                           | Main         | `14`          |
| `font_size_medium`  | `int`   | Medium font size                                          | Main         | `28`          |
| `font_size_large`   | `int`   | Large font size                                           | Main         | `42`          |
| `font_size_x_large` | `int`   | Extra large font size                                     | Main         | `56`          |
| `comm_addr`         | `str`   | Communication server address                              | Remote       | `"127.0.0.1"` |
| `comm_port`         | `int`   | The port on which the communication system runs on        | Main, Remote | `16900`       |
| `save_data`         | `bool`  | `True`: save data; `False`: discard data                  | Remote       | `False`       |

## Devices Module

### Example

```python
from leads import controller, MAIN_CONTROLLER
from leads_emulation import RandomController


@controller(MAIN_CONTROLLER)
class MainController(RandomController):
    pass
```

The devices module will be executed after configuration registration. Register your devices in this module using AOP
paradigm. A more detailed explanation can be found [here](https://leads-docs.projectneura.org/en/latest/device.html).

## Architecture

### Main

#### Pin Configuration

![pin-config](docs/assets/pin-config.png)

### Remote Analyst

![comm-flowchart](docs/assets/comm-flowchart.png)

## Collaborations

### Community

#### Issues

Our team management completely relies on GitHub. Tasks are published and assigned as
[issues](https://github.com/ProjectNeura/LEADS/issues). You will be notified if you are assigned to certain tasks.
However, you may also join other discussions for which you are not responsible.

There are a few labels that classify the issues.

- `bug` reports a bug
- `code review` discusses a code review or comment
- `documentation` suggests a documentation enhancement
- `duplicate` marks that a similar issue has been raised
- `enhancement` proposes a new feature or request
- `help wanted` means that extra attention is needed to this issue
- `invalid` marks that the issue is in a valid format
- `question` requests further information
- `report` states that it is discussed in the meeting
- `todo` creates a new task
- `wontfix` marks that the issue is ignored

Label your issue with at least one of the labels above before you submit.

#### Projects

You can have a look at the whole schedule of each project in a timeline using
the [projects](https://github.com/orgs/ProjectNeura/projects/) feature.

### Code Contributions

See [CONTRIBUTING.md](CONTRIBUTING.md).
