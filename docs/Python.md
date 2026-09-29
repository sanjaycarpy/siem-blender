## Wazuh Forwarder

### Objective

The forwarder is responsible for monitoring the Wazuh Manager alert stream and transmitting new JSON alerts to the Python receiver running on MacOS.

### Location

```text
~/wazuh-forwarder/forwarder.py
```

### Execution

```bash
python3 ~/wazuh-forwarder/forwarder.py
```

#### Example 

<img src="/Media/screen forwarder script.png" height="450">

## Python Receiver

The receiver runs on MacOS and listens on TCP port `5001`.

```text
0.0.0.0:5001
```

It receives the Wazuh JSON event and extracts the fields required by the visualization layer:

```text
source
timestamp
severity
rule
description
agent
```

#### Example 

<img src="/Media/screen receiver script.png" height="450">


### Result

The Python layer successfully performs two responsibilities:

1. Monitor new Wazuh alerts.
2. Normalize received security events into a common structure.

This normalized structure will later provide the input for Blender.

Current pipeline:

```text
Wazuh
  ↓
JSON Alert
  ↓
Python Forwarder
  ↓
TCP
  ↓
Python Receiver
  ↓
Normalized Event
  ↓
Blender
```