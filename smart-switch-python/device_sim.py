import socket
from packets import InstructionBlock
from interface import TransportInterface
from program_setup import Device

class TCPInterface(TransportInterface):
    def __init__(self, server_ip: str, port: int):
        self.server_ip = server_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_ip, port))

    def send(self, data: bytes):
        self.socket.sendall(bytes(data))

    def receive(self) -> bytes:
        return self.socket.recv(1024)  # Adjust buffer size as needed

    def close(self):
        self.socket.close()

if __name__ == "__main__":

    SERVER_IP = "127.0.0.1"  # Localhost
    PORT = 5123

    # Create the interface
    device_interface = TCPInterface(SERVER_IP, PORT)

    # Create the device
    device = Device("instructions.asm", "data.asm", device_interface)

    try:
        # Start the device
        device.start()
    except KeyboardInterrupt:
        print("\nDevice shutting down...")
    finally:
        device_interface.close()
