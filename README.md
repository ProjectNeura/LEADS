# LEADS: Lightweight Embedded Assisted Driving System

<img src="https://projectneura.org/img/logo.png" alt="logo" style="zoom:25%;" />

LEADS only supports two drive-wheel configurations: single rear wheel (SRW) mode and dual rear wheel (DRW) mode.

This project aims to implement the following features:

- [x] A basic instrumentation system
- [x] A basic communication system
- [x] A basic control system
- [ ] A data recording system with the following components
  - [x] A speed recording system
  - [ ] A G force recording system
  - [ ] A GPS recording system
  - [ ] A battery voltage recording system
- [ ] A control system with the following components
  - [ ] DTCS (Dynamic Traction Control System)
  - [ ] ABS (Anti-lock Braking System)
  - [ ] EBI (Emergency Braking Intervention)
  - [ ] ATBS (Automatic Trail Braking System)


The codes are never designed for average high school students to understand. You may find it hard to read the codes if you do not satisfy the following requirements of skills and knowledge.

- Advanced Python knowledge (you should be familiar with everything and even programming philosophy in Python)
- Solid knowledge of Physics (you should understand how a car moves in reality)
- Basic embedded development experience (C/C++, Raspberry Pi, Arduino, serial communication, PWM)
- Rich experience in Web development (React, NextJS, FastAPI, TCP/IP, sockets)
- Basic machine learning knowledge (linear regression, polynomial regression)

## Installation

### Python

Note that LEADS requires **Python >= 3.11**.

```shell
pip install pysimplegui keyboard RPi.GPIO pyserial leads
```

`numpy` will be automatically installed with `leads`.

`pysimplegui`, `keyboard`, `RPi.GPIO`, and `pyserial` are optional.

If you need only the skeleton, run the following.

```shell
pip install leads
```

#### Verify

```shell
python -m leads_vec info
```

### Arduino

You can install [LEADS-Arduino](https://github.com/ProjectNeura/LEADS-Arduino) from Arduino Library Manager. Note that it is named "LEADS", not "LEADS-Arduino", in the index.

## Quickstart

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

### Remote Controller

```shell
python -m leads_vec_rc
```

Go to the online dashboard https://leads-vec-rc.projectneura.org.

#### Register as a Systemd Service

```shell
python -m leads_vec_rc -r systemd
```

This will register a system service to start the program.

To enable auto-start at boot, run the following.

```shell
systemctl daemon-reload
systemctl enable leads_vec_rc
```

### Configurations

The configuration is a json file that has the following columns. You can have an empty configuration file like the following as all the columns are optional.

```json
{}
```

Note that a purely empty file could cause error.

|                           | Type    | Usage                                                        | Used By      | Default       |
| ------------------------- | ------- | ------------------------------------------------------------ | ------------ | ------------- |
| `srw_mode`                | `bool`  | `True`: single rear wheel; `False`: dual rear wheel          | Main, Remote | `True`        |
| `width`                   | `int`   | Window width                                                 | Main         | `720`         |
| `height`                  | `int`   | Window height                                                | Main         | `480`         |
| `fullscreen`              | `bool`  | `True`: auto maximize; `False`: window mode                  | Main         | `False`       |
| `no_title_bar`            | `bool`  | `True`: no title bar; `False`: default title bar             | Main         | `False`       |
| `manual_mode`             | `bool`  | `True`: hide control system; `False`: show control system    | Main         | `False`       |
| `refresh_rate`            | `int`   | GUI frame per second                                         | Main         | `30`          |
| `font_size_small`         | `int`   | Small font size                                              | Main         | `8`           |
| `font_size_medium`        | `int`   | Medium font size                                             | Main         | `16`          |
| `font_size_large`         | `int`   | Large font size                                              | Main         | `32`          |
| `font_size_x_large`       | `int`   | Extra large font size                                        | Main         | `48`          |
| `scaling_factor`          | `float` | A factor used to scale every component                       | Main         | `1`           |
| `comm_addr`               | `str`   | Communication server address                                 | Remote       | `"127.0.0.1"` |
| `comm_port`               | `int`   | The port on which the communication system runs on           | Main, Remote | `16900`       |
| `data_dir`                | `str`   | The directory for the data recording system                  | Remote       | `"./data"`    |
| `enable_data_persistence` | `bool`  | `True`: enable data persistence; `False`: disable data persistence | Remote       | `True`        |

## Submodules

- [LEADS-Arduino](https://github.com/ProjectNeura/LEADS-Arduino)
- [leads-docs](https://github.com/ProjectNeura/leads-docs)
- [leads-vec-rc](https://github.com/ProjectNeura/leads-vec-rc) (Private)

## Full Docs

Besides the [docs](docs) on GitHub, we also host our docs on [Read the Docs](https://leads.projectneura.org) (TBC).

## Periodic Report

See [reports](docs/reports).

## Architecture

### Main

#### Pin Configuration

![pin-config](docs/assets/pin-config.png)

### Remote Controller

![comm-flowchart](docs/assets/comm-flowchart.png)

## Collaborations

### Community

#### Issues

Our team management completely relies on GitHub. Tasks are published and assigned as [issues](https://github.com/ProjectNeura/LEADS/issues). You will be notified if you are assigned to certain tasks. However, you may also join other discussions for which you are not responsible.

There are a few labels that classify the issues.

- `bug` reports a bug
- `code review` discusses a code review or comment
- `documentation` suggests a documentation enhancement
- `duplicate` marks that a similar issue has been raised
- `enhancement` proposes a new feature or request
- `help wanted` means that extra attention is needed to this issue
- `invalid` marks that the issue is in a valid format
- `question` requests further information
- `report` starts a periodic report discussion
- `todo` creates a new task
- `wontfix` marks that the issue is ignored

Label your issue with at least one of the labels above before you submit.

#### Projects

You can have a look at the whole schedule of each project in a timeline using the [projects](https://github.com/orgs/ProjectNeura/projects/) feature.

### Code Contributions

See [CONTRIBUTING.md](CONTRIBUTING.md).
