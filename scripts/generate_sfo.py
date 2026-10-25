#!/usr/bin/env python3
import struct

def build_sfo(params):
    key_table = bytearray()
    data_table = bytearray()
    entries = []

    for key, val, fmt, max_len in params:
        key_offset = len(key_table)
        key_table.extend(key.encode('utf-8') + b'\x00')

        data_offset = len(data_table)
        if fmt == 'utf8':
            data_bytes = val.encode('utf-8') + b'\x00'
            padded_data = data_bytes.ljust(max_len, b'\x00')
            fmt_code = 0x0204
            used_len = len(data_bytes)
            data_table.extend(padded_data)
        elif fmt == 'int32':
            data_bytes = struct.pack('<I', val)
            fmt_code = 0x0404
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
        ('APP_TYPE', 0, 'int32', 4),
        ('APP_VER', '01.00', 'utf8', 8),
        ('ATTRIBUTE', 0, 'int32', 4),
        ('CATEGORY', 'gd', 'utf8', 4),
        ('CONTENT_ID', 'IV0000-PS4APP000_00-PS4APPMANAGER000', 'utf8', 48),
        ('DOWNLOAD_DATA_SIZE', 0, 'int32', 4),
        ('FORMAT', 'obs', 'utf8', 4),
        ('PARENTAL_LEVEL', 1, 'int32', 4),
        ('SYSTEM_VER', 0, 'int32', 4),
        ('TITLE', 'PS4 App Manager', 'utf8', 128),
        ('TITLE_ID', 'PS4APP000', 'utf8', 12),
        ('VERSION', '01.00', 'utf8', 8)
    ]

    sfo_data = build_sfo(params)
    with open('assets/param.sfo', 'wb') as f:
        f.write(sfo_data)

    print(f"Generated compliant binary assets/param.sfo ({len(sfo_data)} bytes)")
