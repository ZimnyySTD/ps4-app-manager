#!/usr/bin/env python3
import struct

def build_sfo(params):
    key_table = bytearray()
    data_table = bytearray()
    entries = []

    for key, val, fmt in params:
        key_offset = len(key_table)
        key_table.extend(key.encode('utf-8') + b'\x00')

        data_offset = len(data_table)
        if fmt == 'utf8':
            data_bytes = val.encode('utf-8') + b'\x00'
            fmt_code = 0x0204
            max_len = len(data_bytes)
            used_len = len(data_bytes)
            data_table.extend(data_bytes)
        elif fmt == 'int32':
            data_bytes = struct.pack('<I', val)
            fmt_code = 0x0404
            max_len = 4
            used_len = 4
            data_table.extend(data_bytes)

        entries.append((key_offset, fmt_code, used_len, max_len, data_offset))

    header_size = 20
    entries_size = len(entries) * 16
    key_table_offset = header_size + entries_size
    data_table_offset = key_table_offset + len(key_table)

    header = struct.pack('<4sI3I', b'\x00PSF', 0x0101, key_table_offset, data_table_offset, len(entries))

    entries_bytes = bytearray()
    for key_offset, fmt_code, used_len, max_len, data_offset in entries:
        entries_bytes.extend(struct.pack('<HHIII', key_offset, fmt_code, used_len, max_len, data_offset))

    return header + entries_bytes + key_table + data_table

if __name__ == "__main__":
    params = [
        ('APP_VER', '01.00', 'utf8'),
        ('ATTRIBUTE', 0, 'int32'),
        ('CATEGORY', 'gd', 'utf8'),
        ('CONTENT_ID', 'IV0000-PS4APP000_00-PS4APPMANAGER000', 'utf8'),
        ('DOWNLOAD_DATA_SIZE', 0, 'int32'),
        ('SYSTEM_VER', 0, 'int32'),
        ('TITLE', 'PS4 App Manager', 'utf8'),
        ('TITLE_ID', 'PS4APP000', 'utf8'),
        ('VERSION', '01.00', 'utf8')
    ]

    sfo_data = build_sfo(params)
    with open('assets/param.sfo', 'wb') as f:
        f.write(sfo_data)

    print(f"Generated binary assets/param.sfo ({len(sfo_data)} bytes)")
