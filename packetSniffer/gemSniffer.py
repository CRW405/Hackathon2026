from scapy.all import sniff, IP, TCP, UDP, Ether

# --- 1. Define the Packet Handler Function ---
def packet_callback(packet):
    """
    Analyzes and prints information about the captured packet.
    """
    print("\n--- Packet Captured ---")
    
    # Check for the Ethernet layer
    if Ether in packet:
        print(f"Source MAC: {packet[Ether].src} -> Destination MAC: {packet[Ether].dst}")

    # Check for the IP layer
    if IP in packet:
        # Get the IP source and destination addresses
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        protocol = packet[IP].proto
        
        print(f"Source IP: {src_ip} -> Destination IP: {dst_ip}")
        
        # Check for TCP layer
        if TCP in packet:
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            print(f"Protocol: TCP | Source Port: {src_port} -> Destination Port: {dst_port}")
        
        # Check for UDP layer
        elif UDP in packet:
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
            print(f"Protocol: UDP | Source Port: {src_port} -> Destination Port: {dst_port}")
        
        # General IP protocol type (e.g., ICMP is protocol 1)
        else:
            print(f"Protocol: Other (Type {protocol})")

# --- 2. Start Sniffing ---
print("Starting packet sniffer... Press Ctrl+C to stop.")

try:
    # Use the sniff function to capture packets
    # iface: Specify the network interface (e.g., "eth0", "wlan0") - omit for default
    # filter: Optional BPF filter (e.g., "port 80" for HTTP traffic)
    # prn: The function to call for each captured packet
    # store: Do not store packets in memory
    
    sniff(
        # The interface parameter is often optional, but helpful for specificity
        # iface="eth0", 
        filter="tcp or udp", 
        prn=packet_callback, 
        store=0
    )

except KeyboardInterrupt:
    print("\nSniffing stopped by user.")
except Exception as e:
    print(f"\nAn error occurred: {e}")