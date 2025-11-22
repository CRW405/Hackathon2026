"""Network sniffer that extracts SNI/HTTP hostnames and reports them to a server.

This script uses scapy to inspect TCP payloads and attempts to parse TLS SNI
extensions and HTTP `Host:` headers. When a host is discovered, a POST request
is sent to the configured backend server.

WARNING: Running this script may require root privileges and will observe
network traffic on the host. Use only on machines and networks where you have
permission to capture traffic.
"""

from scapy.all import sniff, IP, TCP, Raw
import socket
import time
import struct
import os
import getpass
import requests  # <-- ADDED: To send HTTP requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

# --- Configuration ---
# Build the POST URL from environment variables (fallbacks provided)
packet_base = os.environ.get("PACKET_SNIFFER_BASE_URL")
if not packet_base:
    backend_host = os.environ.get("BACKEND_HOST", "127.0.0.1")
    backend_port = os.environ.get("BACKEND_PORT", "6000")
    packet_base = f"http://{backend_host}:{backend_port}"

packet_path = os.environ.get("PACKET_SNIFFER_POST_PATH", "/api/packet/post")
SERVER_URL = f"{packet_base}{packet_path}"

dns_cache = {}
active_flows = set()


# --- User and Hostname Setup ---
def get_os_username():
    """Gets the currently logged-in OS user."""
    try:
        return os.getlogin()
    except OSError:
        return getpass.getuser()
    except Exception:
        return "unknown_user"


def get_hostname():
    """Gets the computer's network name."""
    return socket.gethostname()


CURRENT_USER = get_os_username()
CURRENT_HOSTNAME = get_hostname()


# --- NEW FUNCTION: Sends data to Flask server ---
def send_to_server(website_name, dest_ip, src_ip):
    """
    Bundles data and sends it to the central server.
    """
    payload = {
        "username": CURRENT_USER,
        "hostname": CURRENT_HOSTNAME,
        "website": website_name,
        "ip_address": dest_ip,
        "source_ip": src_ip,
    }

    try:
        # Send the data as JSON in the POST request body
        response = requests.post(SERVER_URL, json=payload, timeout=10)

        # Optional: Log success or failure
        if response.status_code == 200:
            print(f"Successfully reported: {website_name}")
        else:
            print(f"Error reporting to server: {response.status_code}")

    except requests.exceptions.RequestException as e:
        # Don't crash the sniffer if the server is down
        print(f"Server connection failed: {e}")


def resolve_ip(ip_address):
    # ... (this function is unchanged) ...
    if ip_address in dns_cache:
        return dns_cache[ip_address]
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        dns_cache[ip_address] = hostname
        return hostname
    except (socket.herror, socket.gaierror):
        dns_cache[ip_address] = ip_address
        return ip_address
    except Exception:
        return "Unknown"


def parse_sni(payload):
    # ... (this function is unchanged) ...
    try:
        if payload[0] != 0x16:
            return None
        pos = 5
        if payload[pos] != 0x01:
            return None
        pos += 4 + 2 + 32
        sess_id_len = payload[pos]
        pos += 1 + sess_id_len
        cipher_len = int.from_bytes(payload[pos : pos + 2], "big")
        pos += 2 + cipher_len
        comp_len = payload[pos]
        pos += 1 + comp_len
        if pos + 2 > len(payload):
            return None
        ext_len = int.from_bytes(payload[pos : pos + 2], "big")
        pos += 2
        end_ext = pos + ext_len
        while pos < end_ext:
            if pos + 4 > len(payload):
                break
            ext_type = int.from_bytes(payload[pos : pos + 2], "big")
            ext_data_len = int.from_bytes(payload[pos + 2 : pos + 4], "big")
            pos += 4
            if ext_type == 0x0000:
                pos += 2 + 1
                sni_name_len = int.from_bytes(payload[pos : pos + 2], "big")
                pos += 2
                sni_host = payload[pos : pos + sni_name_len].decode("utf-8")
                return sni_host
            pos += ext_data_len
    except Exception:
        pass
    return None


def extract_http_host(packet):
    # ... (this function is unchanged) ...
    try:
        payload = packet[Raw].load.decode("utf-8", errors="ignore")
        if "Host: " in payload:
            lines = payload.split("\r\n")
            host = next(
                (line.split(": ")[1] for line in lines if "Host: " in line), None
            )
            return host
    except Exception:
        pass
    return None


def packet_callback(packet):
    if IP in packet and TCP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        dst_port = packet[TCP].dport

        flow_id = (src_ip, dst_ip, dst_port)

        if packet.haslayer(Raw):
            payload = packet[Raw].load

            if dst_port == 443:
                sni = parse_sni(payload)
                if sni:
                    # --- MODIFIED ---
                    # Instead of printing, send to server
                    # send_to_server(website_name, dest_ip, src_ip)
                    send_to_server(sni, dst_ip, src_ip)
                    active_flows.add(flow_id)
                    return

            elif dst_port == 80:
                host = extract_http_host(packet)
                if host:
                    # --- MODIFIED ---
                    # Instead of printing, send to server
                    send_to_server(host, dst_ip, src_ip)
                    active_flows.add(flow_id)
                    return

        if flow_id not in active_flows:
            active_flows.add(flow_id)
            # You could also report these generic connections if you want
            # host_name = resolve_ip(dst_ip)
            # send_to_server(f"Unknown (IP: {host_name})", dst_ip, src_ip)


# --- Main Execution ---
print("--- Website Sniffer (Reporting to Server) ---")
print(f"--- Monitoring traffic for user: {CURRENT_USER} on {CURRENT_HOSTNAME} ---")
print(f"--- Reporting to: {SERVER_URL} ---")
print("-" * 60)

# Sniff for TCP traffic
sniff(filter="tcp", prn=packet_callback, store=0)
