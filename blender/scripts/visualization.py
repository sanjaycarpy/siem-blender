import bpy


def handle_event(event):
    print("\n--- Blender SIEM Event ---")
    print(f"Source: {event.get('source')}")
    print(f"Severity: {event.get('severity')}")
    print(f"Rule: {event.get('rule')}")
    print(f"Description: {event.get('description')}")
    print(f"Agent: {event.get('agent')}")
    print("--------------------------")


print("SIEM × BLENDER")
print("Blender event handler ready")