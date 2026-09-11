import struct

with open("libg.so", "rb") as f:
    data = f.read()

# Parse ELF64 header
e_phoff = struct.unpack("<Q", data[32:40])[0]
e_phnum = struct.unpack("<H", data[56:58])[0]
e_phentsize = struct.unpack("<H", data[54:56])[0]

loads = []
for i in range(e_phnum):
    ph = data[e_phoff + i * e_phentsize : e_phoff + (i + 1) * e_phentsize]
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack("<IIQQQQQQ", ph[:56])
    if p_type == 1: # PT_LOAD
        loads.append((p_vaddr, p_memsz, p_offset, p_filesz))
        print(f"PT_LOAD: vaddr=0x{p_vaddr:x} memsz=0x{p_memsz:x} off=0x{p_offset:x} filesz=0x{p_filesz:x}")

def vaddr_to_offset(vaddr):
    for va, ms, off, fs in loads:
        if va <= vaddr < va + ms:
            return off + (vaddr - va)
    return None

vtables = [
    0x014a9cc8,  # Captured [0]
    0x014aef68,  # Captured [1]
    0x014a63f8,  # Captured [2, 5, 9, 13, 15, 18, 22, 23]
    0x014aae28,  # Captured [3, 4]
    0x014a7d88,  # Captured [6, 10, 16, 19]
    0x014a9358,  # PLANT_VTABLE
    0x014a82c8,  # HARVEST_VTABLE
    0x014a9598,  # SELL_VTABLE
]

for vt in vtables:
    fo = vaddr_to_offset(vt)
    fo_str = f"0x{fo:x}" if fo is not None else "None"
    print(f"\n=== VTABLE 0x{vt:08x} (file offset: {fo_str}) ===")
    if fo and fo >= 8 and fo + 40 <= len(data):
        ti = struct.unpack("<Q", data[fo-8:fo])[0]
        methods = struct.unpack("<5Q", data[fo:fo+40])
        print(f"  typeinfo: 0x{ti:x}")
        ti_fo = vaddr_to_offset(ti)
        if ti_fo and 0 < ti_fo < len(data) - 16:
            ti_name_ptr = struct.unpack("<Q", data[ti_fo+8:ti_fo+16])[0]
            name_fo = vaddr_to_offset(ti_name_ptr)
            if name_fo and 0 < name_fo < len(data):
                end = data.find(b"\x00", name_fo)
                mangled = data[name_fo:end].decode("latin1", errors="ignore")
                print(f"  Name: {mangled}")
        print(f"  Methods: {[hex(m) for m in methods]}")
