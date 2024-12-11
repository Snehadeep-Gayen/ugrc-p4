from memory import Memory

def test_memory():
    # Initialize memory
    mem = Memory(size=2048, readSegment=1024)

    # Test Byte Storage and Retrieval
    mem.StoreByte(0, 0x12)
    assert mem.GetByte(0) == 0x12, "Failed to store/retrieve byte at address 0"

    mem.StoreByte(1023, 0xAB)
    assert mem.GetByte(1023) == 0xAB, "Failed to store/retrieve byte at read-bound address"

    # Test Word Storage and Retrieval
    mem.StoreWord(4, 0x12345678)
    assert mem.GetWord(4) == 0x12345678, "Failed to store/retrieve word at address 4"

    # Test Address Out of Range for GetByte
    try:
        mem.GetByte(2048)
    except ValueError as e:
        assert str(e) == "Address out of range", "Failed to catch out-of-range GetByte"

    # Test Address Out of Range for StoreByte
    try:
        mem.StoreByte(2048, 0xFF)
    except ValueError as e:
        assert str(e) == "Address out of range", "Failed to catch out-of-range StoreByte"

    # Test Byte Value Out of Range
    try:
        mem.StoreByte(0, 0x1FF)
    except ValueError as e:
        assert str(e) == "Byte value out of range (0-255)", "Failed to catch out-of-range byte value"

    # Test Word Value Out of Range
    try:
        mem.StoreWord(8, 0x1FFFFFFFF)
    except ValueError as e:
        assert str(e) == "Word value out of range (0-4294967295)", "Failed to catch out-of-range word value"

    # Test Address Out of Range for GetWord
    try:
        mem.GetWord(2045)
    except ValueError as e:
        assert str(e) == "Address out of range", "Failed to catch out-of-range GetWord"

    # Test Address Out of Range for StoreWord
    try:
        mem.StoreWord(2045, 0x12345678)
    except ValueError as e:
        assert str(e) == "Address out of range", "Failed to catch out-of-range StoreWord"

    # Test Read-Only Restriction
    mem.CloseSetup()
    try:
        mem.StoreByte(512, 0x33)  # Should fail since 512 is in the read-only range
    except ValueError as e:
        assert str(e) == "Address out of range", "Failed to enforce read-only restriction"

    try:
        mem.StoreWord(512, 0x12345678)  # Should fail since 512 is in the read-only range
    except ValueError as e:
        assert str(e) == "Address out of range", "Failed to enforce read-only restriction"

    # Test Valid Write After Read-Only Bound
    mem.StoreByte(1024, 0x77)  # Should succeed since 1024 is writable
    assert mem.GetByte(1024) == 0x77, "Failed to store/retrieve byte after read-only bound"

    mem.StoreWord(1024, 0x89ABCDEF)  # Should succeed since 1024 is writable
    assert mem.GetWord(1024) == 0x89ABCDEF, "Failed to store/retrieve word after read-only bound"

    # Edge Case: Verify Setup Mode
    mem = Memory(size=2048, readSegment=2047)
    mem.StoreByte(0, 0x11)
    assert mem.GetByte(0) == 0x11, "Failed setup mode byte storage"
    mem.CloseSetup()
    try:
        mem.StoreByte(0, 0x22)
    except ValueError as e:
        assert str(e) == "Address out of range", "Failed to enforce setup restriction after CloseSetup"

    print("All test cases passed!")


# Run test cases
test_memory()
