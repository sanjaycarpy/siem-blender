import socket
import json
import subprocess

MAC_IP = "192.168.1.211"
MAC_PORT = 5001

ALERTS_FILE = "/var/ossec/logs/alerts/alerts.json"


def send_alert(alert):
    data = json.dumps(alert).encode("utf-8")

    with socket.create_connection((MAC_IP, MAC_PORT)) as connection:
        connection.sendall(data)


def main():
    command = [
        "docker",
        "exec",
        "single-node-wazuh.manager-1",
        "tail",
        "-n",
        "0",
        "-F",
        ALERTS_FILE,
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    print("[*] Wazuh forwarder started")
    print(f"[*] Sending alerts to {MAC_IP}:{MAC_PORT}")
    print("[*] Waiting for new alerts...")

    for line in process.stdout:
        line = line.strip()

        if not line:
            continue

        try:
            alert = json.loads(line)
            send_alert(alert)

            print(
                f"[+] Alert sent: "
                f"rule={alert.get('rule', {}).get('id')}"
            )

        except json.JSONDecodeError:
            print("[!] Invalid JSON alert")

        except ConnectionError:
            print("[!] Unable to connect to receiver")


if __name__ == "__main__":
    main()
