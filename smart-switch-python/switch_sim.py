import socket
from packets import InstructionBlock
from interface import TransportInterface

class TCPInterface(TransportInterface):
    def __init__(self, port: int):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", port))
        self.server_socket.listen(1)
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Connection established with {self.client_address}")

    def send(self, data: bytes):
        self.client_socket.sendall(data)

    def receive(self) -> bytes:
        return self.client_socket.recv(1024)  # Adjust buffer size as needed

    def close(self):
        self.client_socket.close()
        self.server_socket.close()

if __name__ == "__main__":
    from switch import Switch

    PORT = 5123

    # Create the interface
    switch_interface = TCPInterface(PORT)

    # Create the switch
    switch = Switch(switch_interface)

    try:
        # Start the switch
        switch.start()
    except KeyboardInterrupt:
        print("\nSwitch shutting down...")
    finally:
        switch_interface.close()
