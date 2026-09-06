# Wazuh Integration

## Role of Wazuh

Wazuh is the **security monitoring and threat detection platform** used as the event source for this project.

It runs on a **Raspberry Pi 5** using Docker and generates security events that are later processed by Python on macOS.

```text
Wazuh
  │
  │ Security alerts
  ▼
JSON events
  │
  ▼
Python
```

## Wazuh Components

The Wazuh environment is composed of three main services:

|    Component    |                  Role                   |
|:---------------:|:---------------------------------------:|
|  Wazuh Manager  |  Collects and analyzes security events  |
|  Wazuh Indexer  |        Stores and indexes alerts        |
| Wazuh Dashboard | Provides a web interface for monitoring |

All three components run as Docker containers on the Raspberry Pi 5.

## Alert Generation

Wazuh generates alerts when a monitored event matches one of its detection rules.

Each alert contains information such as:

- Event timestamp
    
- Rule identifier
    
- Rule severity
    
- Alert description
    
- Source agent
    

For example, Wazuh generated the following alert when the Manager started:

```json
{
  "timestamp": "2026-09-04T13:33:26.584+0000",
  "rule": {
    "level": 3,
    "description": "Wazuh server started.",
    "id": "502"
  },
  "agent": {
    "id": "000",
    "name": "wazuh.manager"
  }
}
```

## JSON Alert Format

The project uses Wazuh's JSON alert format as the input for the Python processing layer.

The main fields used by the project are:

|Field|Purpose|
|---|---|
|`timestamp`|Time when the event occurred|
|`rule.level`|Alert severity|
|`rule.id`|Wazuh detection rule|
|`rule.description`|Description of the event|
|`agent.name`|Source of the event|

Using JSON provides a structured format that can easily be parsed and processed by Python.

## Alert Integration

The Wazuh Manager produces the alerts that will be consumed by the Python application running on macOS.

The integration follows this flow:

```text
Raspberry Pi 5
     │
     ▼
Wazuh Manager
     │
     ▼
JSON Alert
     │
     ▼
Python on macOS
     │
     ▼
Blender
```

Wazuh is therefore responsible for **detecting and generating the security events**, while Python and Blender handle their processing and visualization.

## Project Scope

This project does not aim to reproduce the complete Wazuh platform.

The focus is on using Wazuh as a **real security event generator** and transforming its alerts into data that can be visualized in a 3D environment.