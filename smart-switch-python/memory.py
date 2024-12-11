from typing import Optional

class Memory:
    def __init__(self, size: int = 2048, readSegment: int = 1024) -> None:
        """
        Initialize memory with a given size (default is 2048 bytes).
        Each address holds a byte (8 bits).
        """
        assert readSegment < size, "Read Only Segment is larger than total size!"
        self.size: int = size
        self.readBound: int = readSegment
        self.memory: bytearray = bytearray(size)  # Initialize memory as a byte array filled with zeroes
        self.setup: bool = True
    
    def CloseSetup(self) -> None:
        """Close setup mode, disabling certain memory access."""
        self.setup = False

    def GetByte(self, address: int) -> int:
        """
        Retrieves a byte from the specified address.
        """
        if 0 <= address < self.size:
            return self.memory[address]
        else:
            raise ValueError("Address out of range")
        
    def GetWord(self, address: int) -> int:
        """
        Retrieves a word (4 bytes) from the specified address.
        Assumes big-endian byte order.
        """
        if 0 <= address <= self.size - 4:
            return (
                (self.memory[address] << 24) |
                (self.memory[address + 1] << 16) |
                (self.memory[address + 2] << 8) |
                self.memory[address + 3]
            )
        else:
            raise ValueError("Address out of range")

    def StoreByte(self, address: int, value: int) -> None:
        """
        Stores a byte at the specified address.
        """
        if (self.setup or self.readBound <= address) and address < self.size:
            if 0 <= value <= 0xFF:
                self.memory[address] = value
            else:
                raise ValueError("Byte value out of range (0-255)")
        else:
            raise ValueError("Address out of range")
        
    def StoreWord(self, address: int, value: int) -> None:
        """
        Stores a word (4 bytes) at the specified address.
        Assumes big-endian byte order.
        """
        if (self.setup or self.readBound <= address) and address + 3 < self.size:
            if 0 <= value <= 0xFFFFFFFF:
                self.memory[address] = (value >> 24) & 0xFF  # Most significant byte
                self.memory[address + 1] = (value >> 16) & 0xFF
                self.memory[address + 2] = (value >> 8) & 0xFF
                self.memory[address + 3] = value & 0xFF  # Least significant byte
            else:
                raise ValueError("Word value out of range (0-4294967295)")
        else:
            raise ValueError("Address out of range")
        
    def pretty_print(self):
        """
        Prints non-zero chunks of memory in a readable format.
        Each chunk is displayed with its start address and data in hexadecimal.
        """
        print("Non-zero memory chunks:")
        in_chunk = False
        chunk_start = 0
        chunk_data = []
        
        for addr in range(self.size):
            value = self.memory[addr]
            if value != 0:
                if not in_chunk:
                    # Start a new chunk
                    in_chunk = True
                    chunk_start = addr
                    chunk_data = [value]
                else:
                    # Continue the current chunk
                    chunk_data.append(value)
            else:
                if in_chunk:
                    # End the current chunk and print it
                    in_chunk = False
                    self._print_chunk(chunk_start, chunk_data)
        
        # Handle any remaining chunk at the end
        if in_chunk:
            self._print_chunk(chunk_start, chunk_data)

    def _print_chunk(self, start: int, data: list):
        """
        Helper function to print a memory chunk.
        """
        hex_data = " ".join(f"{byte:02X}" for byte in data)
        print(f"Address 0x{start:08X}: {hex_data}")
