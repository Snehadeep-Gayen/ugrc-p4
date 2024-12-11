from scapy.fields import *
from scapy.packet import Packet
from enum import Enum

class InstructionBlock(Packet):

    class MessageCode(Enum):
        HELLO = 1
        HELLO_REPLY = 2
        REG_SEND0 = 4
        REG_SEND1 = 5
        REG_SEND2 = 6
        REG_SEND3 = 7
        INSTS = 8
        INSTS_REPLY = 9
        TERMINATE_REG0 = 10
        REG_STORE0 = 12
        REG_STORE1 = 13
        REG_STORE2 = 14
        REG_STORE3 = 15
        ACK = 31
        LOAD_REPLY = 16


    fields_desc = [
        BitField("version", 0, 2),              # 2 bits for version
        BitField("message_code", 0, 6),         # 6 bits for message code
        BitField("flags", 0, 4),                # 4 bits for flags
        BitField("a_seq_num", 0, 4),            # 4 bits for A/Seq. #
        ShortField("checksum", 0),              # 16 bits for checksum
        IntField("instruction_1", 0),          # Instruction #1 / Context
        IntField("instruction_2", 0),          # Instruction #2 / Address
        IntField("instruction_3", 0),          # Instruction #3 / Value
        IntField("instruction_4", 0),          # Instruction #4 / PC Offset
    ]

################### BOOLEAN CONVENIENCE FUNCTIONS #######################

    def has_store(self) -> bool:
        """
        Checks if the packet message has a store instruction or not
        """
        if self.instruction_1 & 2 != 0:
            return True
        return False

    def has_pc(self) -> bool:
        """
        Checks if the packet has the next PC or not
        """
        if self.message_code != self.MessageCode.INSTS_REPLY:
            return False
        return self.message_code & 1 != 0

    def has_ack(self) -> bool:
        """
        Checks if the packet is an ack or not
        """
        return self.instruction_1 & 1 == 1

    def is_hello(self) -> bool:
        """
        Checks if the packet is a hello packet or not
        """
        return self.message_code == 1

################## INSTRUCTION CREATING FUNCTIONS ########################

    def make_reg_send(self, index : int, regs : List[int]):
        assert len(regs)==4
        reg_send = InstructionBlock()
        if index==0:
            reg_send.message_code = self.MessageCode.REG_SEND0.value
        elif index==1:
            reg_send.message_code = self.MessageCode.REG_SEND1.value
        elif index==2:
            reg_send.message_code = self.MessageCode.REG_SEND2.value
        elif index==3:
            reg_send.message_code = self.MessageCode.REG_SEND3.value
        reg_send.instruction_1 = regs[0]
        reg_send.instruction_2 = regs[1]
        reg_send.instruction_3 = regs[2]
        reg_send.instruction_4 = regs[3]
        reg_send.flags = 0b0001
        reg_send.set_checksum()
        return reg_send
    

    def make_reg_store(self, index : int, regs : List[int]):
        assert len(regs)==4
        for i in range(4):
            if regs[i] < 0:
                regs[i] = 2**32 + 1 + regs[i]
        reg_store = InstructionBlock()
        if index==0:
            reg_store.message_code = self.MessageCode.REG_STORE0.value
        elif index==1:
            reg_store.message_code = self.MessageCode.REG_STORE1.value
        elif index==2:
            reg_store.message_code = self.MessageCode.REG_STORE2.value
        elif index==3:
            reg_store.message_code = self.MessageCode.REG_STORE3.value
        reg_store.instruction_1 = regs[0]
        reg_store.instruction_2 = regs[1]
        reg_store.instruction_3 = regs[2]
        reg_store.instruction_4 = regs[3]
        reg_store.flags = 0b0001
        reg_store.set_checksum()
        return reg_store
    
    def make_ack_packet(self):
        ack_packet = InstructionBlock()
        ack_packet.message_code = self.MessageCode.ACK.value
        ack_packet.flags = 0b0001        # Set example flags for hello
        ack_packet.set_checksum()
        return ack_packet
    

    def make_pc_packet(self, pc : int):
        pc_packet = InstructionBlock()
        pc_packet.message_code = self.MessageCode.INSTS_REPLY.value
        pc_packet.flags = 0b0001
        pc_packet.instruction_1 = 0x1   # means nothing other than PC is valid
        pc_packet.instruction_4 = pc
        pc_packet.set_checksum()
        return pc_packet

    def make_hello(self):
        """
        Create a new InstructionBlock configured as a hello packet.
        """
        hello_pkt = InstructionBlock()  # Create a new packet instance
        hello_pkt.message_code = self.MessageCode.HELLO.value    # Set example message code for hello
        hello_pkt.flags = 0b0001        # Set example flags for hello
        # Set other fields as needed, like version, checksum, etc.
        hello_pkt.version = 0
        hello_pkt.set_checksum()        # Ensure checksum is valid
        return hello_pkt


    def make_hello_reply(self):
        """
        Modify the packet to be a hello reply packet.
        """
        hello_reply_pkt = InstructionBlock()
        hello_reply_pkt.message_code = self.MessageCode.HELLO_REPLY.value  # Example code for hello reply
        hello_reply_pkt.flags = 0b0001    # Example flag configuration for hello reply
        # Additional fields can be set as necessary
        hello_reply_pkt.set_checksum()
        return hello_reply_pkt
    
    def register_packet(self, regno : int, reg0 : int, reg1 : int, reg2 : int, reg3 : int):
        """
        Modify the packet to make it a register send packet
        """
        assert regno<4, "Register number can be atmost 4"
        self.message_code = regno + 4 # means the register number is 0, 1, 2, 3, 4
        self.flags = 0b0001
        self.instruction_1 = reg0
        self.instruction_2 = reg1
        self.instruction_3 = reg2
        self.instruction_4 = reg3
        
        self.set_checksum()

        return self
    
    def make_instruction_packet(self, inst1 : int, inst2 : int, inst3 : int, inst4 : int):
        
        pkt = InstructionBlock()
        pkt.message_code = self.MessageCode.INSTS.value
        pkt.flags = 0b0001 # ack
        pkt.instruction_1 = inst1
        pkt.instruction_2 = inst2
        pkt.instruction_3 = inst3
        pkt.instruction_4 = inst4

        pkt.set_checksum()
        
        return pkt
    
    def calculate_checksum(self, packet_bytes):
        """
        Calculate the Internet checksum for a given byte sequence.
        """
        checksum = 0
        length = len(packet_bytes)
        i = 0

        # Sum all 16-bit words
        while length > 1:
            word = (packet_bytes[i] << 8) + packet_bytes[i + 1]  # Combine two bytes
            checksum += word
            checksum = (checksum & 0xFFFF) + (checksum >> 16)  # Add carry bits
            i += 2
            length -= 2

        # If there's a single byte left, pad it with zeros to form a 16-bit word
        if length > 0:
            checksum += packet_bytes[i] << 8  # Add the remaining byte as high-order bits

        # Add carry bits again
        checksum = (checksum & 0xFFFF) + (checksum >> 16)

        # Take the one's complement
        checksum = ~checksum & 0xFFFF

        return checksum


    def verify_checksum(self):
        """
        Verify the checksum of the packet using the Internet checksum method.
        """
        # Temporarily set checksum to 0 for verification
        original_checksum = self.checksum
        self.checksum = 0

        # Calculate checksum over the packet
        calculated_checksum = self.calculate_checksum(bytes(self))

        # Restore the original checksum
        self.checksum = original_checksum

        # Return True if the checksum matches
        return calculated_checksum == original_checksum


    def set_checksum(self):
        """
        Calculate and set the checksum field of the packet using the Internet checksum method.
        """
        # Temporarily set checksum to 0 for calculation
        self.checksum = 0

        # Calculate the Internet checksum
        self.checksum = self.calculate_checksum(bytes(self))
        return self