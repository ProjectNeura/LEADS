# LEADS: Lightweight Embedded Assisted Driving System

LEADS is a system designed for [VeC](https://www.villanovacollege.org/giving/vec-project).

LEADS only supports two drive-wheel configurations: single rear wheel (SRW) mode and dual rear wheel (DRW) mode.

Python is generally not the best choice for writing embedded systems. We made this decision for the following reasons.

- Data analysis
- Short development cycle
- Official support for Raspberry Pi
- Low difficulty in getting started for team members

This project aims to implement the following functions:

- A basic instrumentation system
- A basic communication system
- A basic control system
- A data recording system with the following components
  - A speed recording system
  - A G force recording system
  - A GPS recording system
  - A battery voltage recording system
- A control system with the following components
  - DTCS (Dynamic Traction Control System)
  - ABS (Anti-lock Braking System)
  - EBI (Emergency Braking Intervention)
  - ATBS (Automatic Trail Braking System)

## Installation

Note that LEADS requires **Python >= 3.11**.

```shell
pip install pysimplegui keyboard pyserial leads
```

`numpy` will be automatically installed with `leads`.

`pysimplegui`, `keyboard`, and `pyserial` are optional.

If you need only the skeleton, run the following.

```shell
pip install leads
```

## Quickstart

### Main

```shell
python -m leads_vec
```

### Remote Server (Remote)

```shell
python -m leads_vec --remote
```

### Optional Arguments

#### Configuration File

```shell
python -m leads_vec config=path/to/the/config/file
```

If not specified, all configurations will be default values.

To learn about the configuration file, read [Configurations](#Configurations).

### Configurations

|                 | Type    | Usage                                               | Used By      | Default       |
|-----------------|---------|-----------------------------------------------------|--------------|---------------|
| `srw_mode`      | `bool`  | `True`: single rear wheel; `False`: dual rear wheel | Main, Remote | `True`        |
| `analysis_rate` | `float` | The interval between two analysis frames in seconds | Main         | `0.01`        |
| `update_rate`   | `float` | The interval between two render frames in seconds   | Main         | `0.25`        |
| `comm_addr`     | `str`   | The communication server address                    | Main         | `"127.0.0.1"` |
| `comm_port`     | `int`   | The communication system port                       | Main, Remote | `16900`       |
| `data_dir`      | `str`   | The directory for the data recording system         | Remote       | `"./data"`    |

## Periodic Report

See [reports](docs/reports).

## Collaborations

### Community

#### Issues

Our team management completely relies on GitHub. Tasks are published and assigned
as [issues](https://github.com/ProjectNeura/LEADS/issues). You will be notified if
you are assigned to certain tasks. However, you may also choose to join other
discussions for which you are not responsible.

There are a few labels that classify the issues.

- `bug` reports a bug
- `code review` discusses a code review or comment
- `documentation` suggests a documentation enhancement
- `duplicate` marks that a similar issue has been raised
- `enhancement` proposes a new feature or request
- `help wanted` means that extra attention is needed to this issue
- `invalid` marks that the issue is in valid format
- `question` requests further information
- `report` starts a periodic report discussion
- `todo` creates a new task
- `wontfix` marks that the issue is ignored

Label your issue with at least one of the labels above before you submit.

#### Projects

You can have a look on the whole schedule of each project in timeline using the
[projects](https://github.com/orgs/ProjectNeura/projects/) feature.

### Code Contributions

Please fork the project into your own repository. Before your pull request, make
sure that you have tested all possible impacts on other parts of the project.
If no certainty is assured, please reach out to our core team members to have
official supports.

#### Code Specifications

All code must be type-annotated and follow the [Code Style Guide](docs/Code%20Style%20Guide.md).
