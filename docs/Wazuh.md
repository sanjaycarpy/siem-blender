## Wazuh → Python Communication

### Objective

Validate the automatic transmission of real Wazuh security alerts from the Wazuh Manager running on the Raspberry Pi to a Python receiver running on MacOS.

### Architecture

```text
Wazuh Agent — MacOS
        │
        │ Security event
        ▼
Wazuh Manager — Raspberry Pi
        │
        │ alerts.json
        ▼
forwarder.py
        │
        │ TCP :5001
        ▼
receiver.py — MacOS
        │
        ▼
Normalized SIEM Event
```

### Wazuh Alerts

The Wazuh Manager stores generated alerts in:

```text
/var/ossec/logs/alerts/alerts.json
```

The Python forwarder monitors this file through the Wazuh Manager container.

### Result

The communication between Wazuh and the Python processing layer is operational.

A real Wazuh security event is now automatically transferred from the Raspberry Pi to MacOS over the local network.

This validates the first complete integration path of the project:

```text
Wazuh → Python
```