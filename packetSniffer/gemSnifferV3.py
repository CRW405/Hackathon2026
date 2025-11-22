from scapy.all import sniff, IP, TCP, Raw
import socket
import time
import struct

# --- Configuration ---
# Cache to store IP -> Hostname mappings to speed up processing
dns_cache = {}
# Set to track active connections so we don't spam the console
active_flows = set()

def resolve_ip(ip_address):
    """
    Resolves an IP to a hostname with caching to prevent lag.
    """
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
    """
    Manually parses the TLS Client Hello to extract the Server Name Indication (SNI).
    This reveals the website name in HTTPS traffic.
    """
    try:
        # Check for TLS Handshake (0x16) and Version (0x0301, 0x0302, 0x0303)
        if payload[0] != 0x16: return None
        
        # Skip Record Header (5 bytes)
        # Handshake Header: Type (1), Length (3), Version (2), Random (32)
        pos = 5 
        
        if payload[pos] != 0x01: return None # Must be Client Hello message
        
        pos += 4 # Skip Handshake Type & Length
        pos += 2 # Skip Hello Version
        pos += 32 # Skip Random
        
        # Skip Session ID
        sess_id_len = payload[pos]
        pos += 1 + sess_id_len
        
        # Skip Cipher Suites
        cipher_len = int.from_bytes(payload[pos:pos+2], 'big')
        pos += 2 + cipher_len
        
        # Skip Compression Methods
        comp_len = payload[pos]
        pos += 1 + comp_len
        
        # We are now at Extensions
        if pos + 2 > len(payload): return None
        ext_len = int.from_bytes(payload[pos:pos+2], 'big')
        pos += 2
        
        end_ext = pos + ext_len
        while pos < end_ext:
            if pos + 4 > len(payload): break
            # Extension Type (2 bytes)
            ext_type = int.from_bytes(payload[pos:pos+2], 'big')
            # Extension Data Length (2 bytes)
            ext_data_len = int.from_bytes(payload[pos+2:pos+4], 'big')
            pos += 4
            
            # Extension Type 0 is "server_name"
            if ext_type == 0x0000: 
                # SNI List Length (2)
                pos += 2
                # SNI Type (1) - 0 is host_name
                pos += 1 
                # SNI Name Length (2)
                sni_name_len = int.from_bytes(payload[pos:pos+2], 'big')
                pos += 2
                # The actual Hostname string
                sni_host = payload[pos:pos+sni_name_len].decode('utf-8')
                return sni_host
            
            pos += ext_data_len
            
    except Exception:
        pass # Parsing failed, likely not a standard Client Hello
    return None

def extract_http_host(packet):
    """Attempts to read the HTTP Host header."""
    try:
        payload = packet[Raw].load.decode('utf-8', errors='ignore')
        if "Host: " in payload:
            lines = payload.split('\r\n')
            host = next((line.split(': ')[1] for line in lines if "Host: " in line), None)
            return host
    except Exception:
        pass
    return None

def packet_callback(packet):
    if IP in packet and TCP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        dst_port = packet[TCP].dport
        
        # Unique ID for this connection flow
        flow_id = (src_ip, dst_ip, dst_port)

        # Check for Raw payload (Data)
        if packet.haslayer(Raw):
            payload = packet[Raw].load
            
            # --- HTTPS (Port 443) Analysis ---
            if dst_port == 443:
                sni = parse_sni(payload)
                if sni:
                    print(f"\n[HTTPS] Connecting to: {sni} ({dst_ip})")
                    active_flows.add(flow_id) # Mark flow as seen
                    return

            # --- HTTP (Port 80) Analysis ---
            elif dst_port == 80:
                host = extract_http_host(packet)
                if host:
                    print(f"\n[HTTP]  Connecting to: {host} ({dst_ip})")
                    active_flows.add(flow_id)
                    return

        # --- General Connection Summary (Fallback) ---
        if flow_id not in active_flows:
            active_flows.add(flow_id)
            # Only do slow Reverse DNS if we couldn't get the name from SNI/HTTP
            host_name = resolve_ip(dst_ip)
            # print(f"[{time.strftime('%H:%M:%S')}] New Connection: {dst_ip} ({host_name}) port {dst_port}")

# Clear the screen and start
print("--- Website Sniffer (SNI & HTTP) Started ---")
print("Detects website names from HTTPS Handshakes and HTTP Headers.")
print("-" * 60)

# Sniff for TCP traffic
sniff(filter="tcp", prn=packet_callback, store=0)