import bpy
import socket
import threading
import json
import time
import queue


HOST = "127.0.0.1"
PORT = 5002

ROTATION_AXIS = "Z"

BASE_SPEED = 0.01
SPEED_PER_ALERT = 0.002
MAX_ALERTS_FOR_SPEED = 50


severity_counts = {
    1: 0,
    2: 0,
    3: 0
}


SPHERE_NAMES = {
    1: "sp1",
    2: "sp2",
    3: "sp3"
}


server = None
receiver_thread = None
receiver_running = False

event_queue = queue.Queue()


def get_severity_bucket(severity):

    if severity <= 6:
        return 1

    elif severity <= 11:
        return 2

    else:
        return 3


def update_severity_count(severity):

    bucket = get_severity_bucket(severity)

    severity_counts[bucket] += 1

    print(
        f"[SIEM] Severity {severity} -> bucket {bucket}"
    )


def rotate_spheres():

    for bucket, sphere_name in SPHERE_NAMES.items():

        sphere = bpy.data.objects.get(sphere_name)

        if sphere is None:
            print(
                f"[!] Blender object not found: {sphere_name}"
            )
            continue

        alert_count = min(
            severity_counts[bucket],
            MAX_ALERTS_FOR_SPEED
        )

        if alert_count == 0:
            continue

        speed = (
            BASE_SPEED
            + alert_count * SPEED_PER_ALERT
        )

        if ROTATION_AXIS == "X":
            sphere.rotation_euler.x += speed

        elif ROTATION_AXIS == "Y":
            sphere.rotation_euler.y += speed

        else:
            sphere.rotation_euler.z += speed


def process_events():

    while not event_queue.empty():

        try:
            event = event_queue.get_nowait()

        except queue.Empty:
            break

        severity = event.get("severity") or 0

        try:
            severity = int(severity)

        except (TypeError, ValueError):
            severity = 0

        update_severity_count(severity)

        print(
            f"[SIEM] Event received | "
            f"severity={severity} | "
            f"sp1={severity_counts[1]} | "
            f"sp2={severity_counts[2]} | "
            f"sp3={severity_counts[3]}"
        )

    rotate_spheres()

    return 0.1


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

        server.bind(
            (HOST, PORT)
        )

        server.listen(5)

        server.setblocking(False)

        receiver_running = True

        print(
            f"[*] SIEM receiver listening on {HOST}:{PORT}"
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

                    event_queue.put(event)

                except json.JSONDecodeError:

                    print(
                        "[!] Invalid JSON received"
                    )

                except ConnectionError:

                    print(
                        "[!] Connection error"
                    )

                finally:

                    connection.close()

            except BlockingIOError:

                time.sleep(0.1)

    except Exception as error:

        print(
            "[!] SIEM receiver error:",
            repr(error)
        )

    finally:

        receiver_running = False

        if server:
            server.close()

        server = None

        print(
            "[*] SIEM receiver stopped"
        )


def start_receiver():

    global receiver_thread

    if receiver_thread and receiver_thread.is_alive():

        print(
            "[!] SIEM receiver already running"
        )

        return

    receiver_thread = threading.Thread(
        target=receive_events,
        daemon=True,
        name="WazuhBlenderReceiver"
    )

    receiver_thread.start()

    if not bpy.app.timers.is_registered(process_events):

        bpy.app.timers.register(
            process_events,
            first_interval=0.1
        )

    print(
        "[*] SIEM receiver started"
    )


def stop_receiver():

    global receiver_running

    receiver_running = False

    print(
        "[*] Stopping SIEM receiver..."
    )


print("SIEM x BLENDER")
print("Severity buckets: 0-6 / 7-11 / +=12")
print("Receiver ready")
