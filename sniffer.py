#!/usr/bin/env python3
"""Minimal Linux packet sniffer using AF_PACKET."""

import socket
import struct
import sys
import signal

# ─── Setup ────────────────────────────────────────────────────────────────────

def create_socket(interface=None):
    """Create an AF_PACKET raw socket. Pass interface name to filter."""
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
    if interface:
        s.bind((interface, 0))
    return s


# ─── Parsers ──────────────────────────────────────────────────────────────────

def parse_ethernet(data):
    """Parse 14-byte Ethernet header."""
    dst_mac = data[0:6].hex(':')
    src_mac = data[6:12].hex(':')
    ethertype = struct.unpack("!H", data[12:14])[0]
    return dst_mac, src_mac, ethertype, data[14:]


def parse_ip(data):
    """Parse 20-byte IPv4 header (may be longer with options)."""
    ver_ihl, tos, total_len, ip_id, flags_frag, ttl, proto, chk, src, dst = \
        struct.unpack("!BBHHHBBH4s4s", data[:20])
    ihl = (ver_ihl & 0x0F) * 4  # header length in bytes
    src_ip = socket.inet_ntoa(src)
    dst_ip = socket.inet_ntoa(dst)
    return {
        "version": (ver_ihl >> 4) & 0x0F,
        "ihl": ihl,
        "tos": tos,
        "total_len": total_len,
        "id": ip_id,
        "flags": (flags_frag >> 13) & 0x07,
        "frag_offset": flags_frag & 0x1FFF,
        "ttl": ttl,
        "proto": proto,
        "checksum": chk,
        "src": src_ip,
        "dst": dst_ip,
    }, data[ihl:]


def parse_tcp(data):
    """Parse 20-byte TCP header (may be longer with options)."""
    src_port, dst_port, seq, ack, offset_flags = struct.unpack("!HHIIH", data[:14])
    offset = (offset_flags >> 4) & 0x0F
    flags = offset_flags & 0x3F
    flag_str = "".join([
        "S" if flags & 0x02 else "",
        "F" if flags & 0x01 else "",
        "R" if flags & 0x04 else "",
        "P" if flags & 0x08 else "",
        "A" if flags & 0x10 else "",
        "U" if flags & 0x20 else "",
    ])
    return {
        "src_port": src_port,
        "dst_port": dst_port,
        "seq": seq,
        "ack": ack,
        "flags": flag_str,
    }, data[offset * 4:]


def parse_udp(data):
    """Parse 8-byte UDP header."""
    src_port, dst_port, length, chk = struct.unpack("!HHHH", data[:8])
    return {
        "src_port": src_port,
        "dst_port": dst_port,
        "length": length,
        "checksum": chk,
    }, data[8:]


def parse_icmp(data):
    """Parse 8-byte ICMP header."""
    icmp_type, code, chk, ident, seq = struct.unpack("!BBHHH", data[:8])
    return {
        "type": icmp_type,
        "code": code,
        "checksum": chk,
        "id": ident,
        "seq": seq,
    }, data[8:]


# ─── Main ─────────────────────────────────────────────────────────────────────

def handle_packet(data):
    """Parse and print one captured frame."""
    dst_mac, src_mac, ethertype, payload = parse_ethernet(data)

    if ethertype != 0x0800:  # not IPv4
        return

    ip, ip_payload = parse_ip(payload)
    proto = ip["proto"]

    line = (
        f"[{ip['src']}:{'?' if proto not in (6,17) else ''} → {ip['dst']}]"
        f"  proto={proto}  ttl={ip['ttl']}  len={ip['total_len']}"
    )

    if proto == 6:
        tcp, _ = parse_tcp(ip_payload)
        line += f"  TCP {tcp['src_port']}→{tcp['dst_port']} [{tcp['flags']}]"
    elif proto == 17:
        udp, _ = parse_udp(ip_payload)
        line += f"  UDP {udp['src_port']}→{udp['dst_port']}"
    elif proto == 1:
        icmp, _ = parse_icmp(ip_payload)
        type_names = {0: "Echo Reply", 8: "Echo Request", 11: "Time Exceeded"}
        line += f"  ICMP {type_names.get(icmp['type'], icmp['type'])} id={icmp['id']} seq={icmp['seq']}"

    print(line, flush=True)


def main():
    interface = sys.argv[1] if len(sys.argv) > 1 else None  # e.g. "eth0"

    if interface is None:
        # Auto-detect: use the interface that has the default route
        with open("/proc/net/route") as f:
            for line in f.readlines()[1:]:
                parts = line.split()
                if parts[1] == "00000000":  # default gateway
                    interface = parts[0]
                    break
        if interface is None:
            interface = "eth0"

    print(f"Sniffing on {interface} (Ctrl+C to stop)\n")
    s = create_socket(interface)

    def _sigint(sig, frame):
        s.close()
        print("\nStopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, _sigint)

    while True:
        data, _ = s.recvfrom(65535)
        handle_packet(data)


if __name__ == "__main__":
    main()   