from scapy.all import sniff, IP, TCP
import socket

def resolve_ip(ip_address):
    """
    Attempts to convert an IP address into a domain name (Hostname).
    """
    try:
        # socket.gethostbyaddr returns (hostname, aliaslist, ipaddrlist)
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except socket.herror:
        # Returns the original IP if resolution fails
        return ip_address
    except Exception:
        return "Unknown"

def packet_callback(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        # We only want to analyze outgoing traffic (requests) or incoming (responses)
        # Let's look at where the packet came FROM (Source)
        
        if TCP in packet:
            # Check specifically for web traffic ports (80 for HTTP, 443 for HTTPS)
            if packet[TCP].sport == 80 or packet[TCP].sport == 443:
                
                # Attempt to resolve the Source IP to a Website Name
                # Note: This causes lag in high-traffic environments
                host_name = resolve_ip(src_ip)
                
                print(f"Traffic from: {src_ip} ({host_name})")

print("Sniffing for web traffic (Port 80/443)... Press Ctrl+C to stop.")
sniff(filter="tcp port 80 or tcp port 443", prn=packet_callback, store=0)