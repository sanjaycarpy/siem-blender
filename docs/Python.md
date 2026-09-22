## Wazuh Forwarder

### Objective

The forwarder is responsible for monitoring the Wazuh Manager alert stream and transmitting new JSON alerts to the Python receiver running on Windows.

### Location

```text
~/wazuh-forwarder/forwarder.py
```

### Execution

```bash
python3 ~/wazuh-forwarder/forwarder.py
```

Expected output:

```text
[*] Wazuh forwarder started
[*] Sending alerts to 192.168.1.211:5001
[*] Waiting for new alerts...
```

When a new Wazuh alert is detected:

```text
[+] Alert sent: rule=5402
```

### Data Flow

```text
alerts.json
     │
     ▼
forwarder.py
     │
     │ JSON over TCP
     ▼
receiver.py
     │
     ▼
normalize_alert()
     │
     ▼
Normalized SIEM Event
```

## Python Receiver

The receiver runs on Windows and listens on TCP port `5001`.

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

### Validation

A real Wazuh alert was successfully received:

```json
--- SIEM Event ---

{
  "source": "wazuh",
  "timestamp": "2026-09-07T19:10:58.806+0000",
  "severity": 3,
  "rule": "5402",
  "description": "Successful sudo to ROOT executed.",
  "agent": "Windows11"
}
```

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
