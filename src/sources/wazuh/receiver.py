import socket
import json


# Listen on all network interfaces of the Windows machine.
# The Raspberry Pi will connect to this address through the local network.
HOST = "0.0.0.0"

# Dedicated TCP port for communication between the Raspberry Pi
# and the Windows Python receiver.
PORT = 5001


# Blender runs on the same Windows machine as the Python receiver.
# Therefore, communication with Blender is restricted to the local machine.
BLENDER_HOST = "127.0.0.1"

# Dedicated TCP port for communication between the Python receiver and Blender.
# Port 5001 is already used for Raspberry Pi → Python communication.
BLENDER_PORT = 5002


def normalize_alert(alert):
    """
    Convert a raw Wazuh alert into a simplified SIEM event.

    The normalized structure contains only the information
    required by the rest of the project, including Blender.
    """

    # Extract the Wazuh rule information from the alert.
    rule = alert.get("rule", {})

    # Extract the Wazuh agent information from the alert.
    agent = alert.get("agent", {})

    # Build a simplified and standardized SIEM event.
    return {
        "source": "wazuh",
        "timestamp": alert.get("timestamp"),
        "severity": rule.get("level"),
        "rule": rule.get("id"),
        "description": rule.get("description"),
        "agent": agent.get("name")
    }


def send_to_blender(event):
    """
    Send a normalized SIEM event to Blender through TCP.
    """

    # Convert the Python dictionary into a JSON string
    # and then encode it into UTF-8 bytes for transmission.
    data = json.dumps(event).encode("utf-8")

    # Create a TCP connection to the Blender receiver.
    # A timeout prevents the receiver from waiting indefinitely
    # if Blender is unavailable.
    with socket.create_connection(
        (BLENDER_HOST, BLENDER_PORT),
        timeout=5
    ) as connection:

        # Send the complete normalized event to Blender.
        connection.sendall(data)

    # Confirm that the event was successfully sent to Blender.
    print("[+] Event sent to Blender")


def start_server():
    """
    Start the TCP server that receives alerts from the Raspberry Pi.
    """

    # Create an IPv4 TCP socket.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow the port to be reused quickly after the receiver is restarted.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the server to all Windows network interfaces on port 5001.
    server.bind((HOST, PORT))

    # Start listening for incoming connections.
    server.listen(1)

    print(f"[*] Wazuh receiver listening on port {PORT}")
    print("[*] Waiting for alerts...")

    # Keep the receiver running continuously.
    while True:

        # Wait until the Raspberry Pi forwarder establishes a connection.
        connection, address = server.accept()

        print(
            f"\n[+] Connection received from "
            f"{address[0]}:{address[1]}"
        )

        # Automatically close the connection when processing is finished.
        with connection:

            # TCP data can arrive in several parts.
            # The buffer temporarily stores the received data.
            buffer = ""

            while True:

                # Receive up to 4096 bytes from the TCP connection.
                data = connection.recv(4096)

                # If no data is received, the client has closed the connection.
                if not data:
                    break

                # Decode the received bytes as UTF-8 text
                # and add them to the buffer.
                buffer += data.decode("utf-8")

                try:

                    # Convert the JSON data into a Python dictionary.
                    alert = json.loads(buffer)

                    # Convert the raw Wazuh alert into the normalized
                    # SIEM event structure used by the project.
                    event = normalize_alert(alert)

                    # Forward the normalized event to Blender.
                    send_to_blender(event)

                    # Display the normalized event in the Windows console.
                    print("\n--- SIEM Event ---")
                    print(json.dumps(event, indent=2))
                    print("------------------")

                    # Clear the buffer after the event has been processed.
                    buffer = ""

                except json.JSONDecodeError:

                    # The JSON may not be complete yet.
                    # Wait for the next piece of data before trying again.
                    continue


# Start the Wazuh receiver when this Python file is executed directly.
if __name__ == "__main__":
    start_server()
