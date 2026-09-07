
import socket
import json

HOST = "0.0.0.0"
PORT = 5001


def normalize_alert(alert):
    rule = alert.get("rule", {})
    agent = alert.get("agent", {})

    return {
        "source": "wazuh",
        "timestamp": alert.get("timestamp"),
        "severity": rule.get("level"),
        "rule": rule.get("id"),
        "description": rule.get("description"),
        "agent": agent.get("name")
    }


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"[*] Wazuh receiver listening on port {PORT}")
    print("[*] Waiting for alerts...")

    while True:
        connection, address = server.accept()

        print(f"\n[+] Connection received from {address[0]}:{address[1]}")

        with connection:
            buffer = ""

            while True:
                data = connection.recv(4096)

                if not data:
                    break

                buffer += data.decode("utf-8")

                try:
                    alert = json.loads(buffer)

                    event = normalize_alert(alert)

                    print("\n--- SIEM Event ---")
                    print(json.dumps(event, indent=2))
                    print("------------------")

                    buffer = ""

                except json.JSONDecodeError:
                    continue


if __name__ == "__main__":
    start_server()
    