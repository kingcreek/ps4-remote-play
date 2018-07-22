# Copyright (c) 2018, Pierre Bourdon <delroth@gmail.com>
# SPDX-License-Identifier: Apache-2.0
"""
Discovers PS4 consoles on the local network and wakes them up on demand.
"""

import binascii
import enum
import email
import socket
import time

_DISCOVERY_PORT = 987


class ConsoleStatus(enum.Enum):
    standby = 0
    ready = 1


def _parse_http_response(data):
    # Remove the firstline for separate handling.
    firstline, data = data.split(b'\n', 1)
    code = int(firstline.split()[1])

    m = email.message_from_bytes(data)
    return code, dict(m.items())


def find_console(console, timeout=3.0):
    """Finds a console on the local network and returns its status."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', 12345))

    data = b'SRCH * HTTP/1.1\r\n'
    data += b'device - discovery - protocol - version:0020020\r\n'
    data += b'\r\n'

    deadline = time.time() + timeout
    while time.time() < deadline:
        sock.sendto(data, ('255.255.255.255', _DISCOVERY_PORT))
        sock.settimeout(deadline - time.time())
        try:
            data, addr = sock.recvfrom(65536)
        except socket.timeout:
            break

        code, headers = _parse_http_response(data)
        if binascii.a2b_hex(headers['host-id']) != console.host_id:
            continue
        if code == 620:
            status = ConsoleStatus.standby
        else:
            status = ConsoleStatus.ready
        return addr[0], status

    return None, None


def wake_up(ip, console):
    """Asks a PS4 in standby mode to turn itself on."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 12345))

    credentials = int(console.registration_key, 16)

    data = b'WAKEUP * HTTP/1.1\n'
    data += b'client-type:vr\n'
    data += b'auth-type:R\n'
    data += b'model:w\n'
    data += b'app-type:r\n'
    data += b'user-credential:%d\n' % credentials
    data += b'device-discovery-protocol-version:0020020\n'

    sock.sendto(data, (ip, _DISCOVERY_PORT))
