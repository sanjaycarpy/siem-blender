import bpy
import socket
import threading
import json
import time
import queue


HOST = "127.0.0.1"
PORT = 5002

server = None
receiver_thread = None
receiver_running = False

event_queue = queue.Queue()
received_events = []


# ============================================================
# BLENDER VISUALIZATION
# ============================================================

def create_alert_cube(event):
    severity = event.get("severity") or 0
    rule = event.get("rule") or "UNKNOWN"

    try:
        severity = int(severity)
    except (TypeError, ValueError):
        severity = 0

    # Positionner les cubes horizontalement
    index = len(received_events) - 1
    x = index * 3

    # Créer le cube
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(x, 0, 1)
    )

    cube = bpy.context.object

    cube.name = f"SIEM_ALERT_{rule}_{index}"

    # Hauteur selon la sévérité
    cube.scale.z = max(1, severity / 5)

    # Informations utiles dans les propriétés Blender
    cube["source"] = event.get("source")
    cube["timestamp"] = event.get("timestamp")
    cube["severity"] = severity
    cube["rule"] = rule
    cube["description"] = event.get("description")
    cube["agent"] = event.get("agent")

    print(
        f"[BLENDER] Cube créé | "
        f"rule={rule} | severity={severity}"
    )


# ============================================================
# PROCESS EVENTS ON BLENDER MAIN THREAD
# ============================================================

def process_events():
    while not event_queue.empty():

        try:
            event = event_queue.get_nowait()
        except queue.Empty:
            break

        received_events.append(event)

        print("\n--- BLENDER SIEM EVENT ---")
        print(f"Source:      {event.get('source')}")
        print(f"Timestamp:   {event.get('timestamp')}")
        print(f"Severity:    {event.get('severity')}")
        print(f"Rule:        {event.get('rule')}")
        print(f"Description: {event.get('description')}")
        print(f"Agent:       {event.get('agent')}")
        print("--------------------------")

        create_alert_cube(event)

    return 0.1


# ============================================================
# NETWORK RECEIVER
# ============================================================

def receive_events():

    global server
    global receiver_running

    try:

        server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server.bind((HOST, PORT))
        server.listen(5)
        server.setblocking(False)

        receiver_running = True

        print(
            f"[*] Blender SIEM receiver listening "
            f"on {HOST}:{PORT}"
        )

        while receiver_running:

            try:

                connection, address = server.accept()

                print(
                    f"[+] Connection received from "
                    f"{address[0]}:{address[1]}"
                )

                connection.settimeout(5)

                try:

                    data = connection.recv(4096)

                    if not data:
                        connection.close()
                        continue

                    event = json.loads(
                        data.decode("utf-8")
                    )

                    # IMPORTANT :
                    # Le thread réseau ne touche pas à bpy.
                    event_queue.put(event)

                    print("[+] Event added to Blender queue")

                except json.JSONDecodeError:

                    print("[!] Invalid JSON received")

                except ConnectionError:

                    print("[!] Connection error")

                finally:

                    connection.close()

            except BlockingIOError:

                time.sleep(0.1)

    except Exception as error:

        print(
            "[!] Blender SIEM receiver error:",
            repr(error)
        )

    finally:

        receiver_running = False

        if server:
            server.close()

        server = None

        print("[*] Blender SIEM receiver stopped")


# ============================================================
# START / STOP
# ============================================================

def start_receiver():

    global receiver_thread

    if receiver_thread and receiver_thread.is_alive():

        print("[!] Blender receiver already running")
        return

    receiver_thread = threading.Thread(
        target=receive_events,
        daemon=True,
        name="WazuhBlenderReceiver"
    )

    receiver_thread.start()

    # Timer exécuté par le thread principal de Blender
    if not bpy.app.timers.is_registered(process_events):

        bpy.app.timers.register(
            process_events,
            first_interval=0.1
        )

    print("[*] Blender SIEM receiver started")


def stop_receiver():

    global receiver_running

    receiver_running = False

    print("[*] Stopping Blender SIEM receiver...")


print("SIEM × BLENDER")
print("Blender event visualization ready")