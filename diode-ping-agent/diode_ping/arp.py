#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Diode Ping Agent ARP."""

import fcntl
import socket
import struct
import binascii
from ipaddress import IPv4Network

# Constants
SIOCGIFHWADDR = 0x8927  # Get hardware address
SIOCGIFADDR = 0x8915  # Get IP address


def get_mac_address(ifname: bytes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(sock.fileno(), SIOCGIFHWADDR, struct.pack("256s", ifname[:15]))
    return ":".join(["%02x" % b for b in info[18:24]])


def create_arp_request(src_mac, src_ip, target_ip):
    eth_header = struct.pack(
        "!6s6s2s",
        b"\xff\xff\xff\xff\xff\xff",  # Destination MAC (Broadcast)
        binascii.unhexlify(src_mac.replace(":", "")),  # Source MAC
        b"\x08\x06",
    )  # ARP protocol

    arp_header = struct.pack(
        "!2s2s1s1s2s6s4s6s4s",
        b"\x00\x01",  # Hardware type (Ethernet)
        b"\x08\x00",  # Protocol type (IP)
        b"\x06",  # Hardware size
        b"\x04",  # Protocol size
        b"\x00\x01",  # Opcode (request)
        binascii.unhexlify(src_mac.replace(":", "")),  # Sender MAC
        socket.inet_aton(src_ip),  # Sender IP
        b"\x00\x00\x00\x00\x00\x00",  # Target MAC
        socket.inet_aton(target_ip),
    )  # Target IP
    return eth_header + arp_header


def parse_arp_response(packet):
    eth_header = packet[0:14]
    eth = struct.unpack("!6s6s2s", eth_header)

    if eth[2] == b"\x08\x06":  # Check if it's an ARP packet
        arp_header = packet[14:42]
        arp = struct.unpack("!2s2s1s1s2s6s4s6s4s", arp_header)

        src_mac = binascii.hexlify(arp[5]).decode("utf-8")
        src_ip = socket.inet_ntoa(arp[6])
        return src_ip, src_mac
    return None, None


def arp_scan(ifname: str, src_ip: IPv4Network, target_ip: IPv4Network) -> str:
    src_mac = get_mac_address(ifname.encode())
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    sock.bind((ifname, 0))
    arp_request = create_arp_request(src_mac, src_ip, target_ip)
    sock.send(arp_request)
    while True:
        raw_packet = sock.recv(65536)
        src_ip, src_mac = parse_arp_response(raw_packet)
        if src_ip:
            return src_mac
