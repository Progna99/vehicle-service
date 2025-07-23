import argparse
import can
from kuksa_client.grpc import VSSClient

def broker_to_can_loop(client, bus):
    print("[INFO] Subscribing to Vehicle.Speed")
    for updates in client.subscribe_current_values(['Vehicle.Speed']):
        print("[DEBUG] Received update:", updates)

        speed_update = updates.get('Vehicle.Speed')
        if speed_update is None or speed_update.value is None:
            print("[WARNING] Invalid or missing 'Vehicle.Speed' value:", speed_update)
            continue

        try:
            speed_val = float(speed_update.value)
            speed_int = int(speed_val * 10)  # Scale float to int for CAN message
            data = [(speed_int >> 8) & 0xFF, speed_int & 0xFF] + [0]*6  # Fill to 8 bytes
            msg = can.Message(arbitration_id=0x123, data=data, is_extended_id=False)
            bus.send(msg)
            print(f"[REMOTE→CAN] Sent CAN: {speed_val} km/h → {msg}")
        except Exception as e:
            print("[ERROR] Failed to process Vehicle.Speed update:", e)

def main(broker_ip, broker_port):
    print(f"[INFO] Connecting to DataBroker at {broker_ip}:{broker_port}")
    with VSSClient(broker_ip, broker_port) as client:
        print("[INFO] Connected to DataBroker.")

        # Initialize CAN bus using virtual CAN interface (vcan0)
        try:
            bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
        except Exception as e:
            print("[ERROR] Failed to initialize CAN bus:", e)
            return

        broker_to_can_loop(client, bus)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--broker', default='localhost', help='Kuksa DataBroker host')
    parser.add_argument('--port', type=int, default=55555, help='Kuksa DataBroker port')
    args = parser.parse_args()

    try:
        main(args.broker, args.port)
    except KeyboardInterrupt:
        print("[INFO] Interrupted by user.")
    except Exception as e:
        print("[ERROR] Top-level failure:", e)

