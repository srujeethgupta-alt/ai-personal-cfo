"""
Simple local tunnel - makes your app accessible from other machines on network
without needing firewall changes. Uses socat-like approach with Python.
"""
import socket
import threading
import sys

def forward_port(local_port, remote_host, remote_port, listen_ip='0.0.0.0'):
    """Forward connections from listen_ip:local_port to remote_host:remote_port"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((listen_ip, local_port))
    server.listen(5)
    print(f"✓ Listening on {listen_ip}:{local_port} → {remote_host}:{remote_port}")
    
    def handle_client(client_sock, addr):
        try:
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.connect((remote_host, remote_port))
            
            def relay(src, dst):
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
            
            t1 = threading.Thread(target=relay, args=(client_sock, remote_sock))
            t2 = threading.Thread(target=relay, args=(remote_sock, client_sock))
            t1.daemon = True
            t2.daemon = True
            t1.start()
            t2.start()
        except:
            pass
        finally:
            client_sock.close()
    
    try:
        while True:
            client, addr = server.accept()
            threading.Thread(target=handle_client, args=(client, addr)).start()
    except KeyboardInterrupt:
        server.close()

if __name__ == '__main__':
    print("🌐 Starting local tunnel...\n")
    print("=" * 50)
    
    # Start frontend tunnel on 5173
    t1 = threading.Thread(
        target=forward_port,
        args=(5173, 'localhost', 5173),
        daemon=True
    )
    t1.start()
    
    # Start backend tunnel on 8000
    t2 = threading.Thread(
        target=forward_port,
        args=(8000, 'localhost', 8000),
        daemon=True
    )
    t2.start()
    
    print("\n✓ Both services exposed on 0.0.0.0")
    print("\nAccess from other machines:")
    print("  Frontend: http://<your-ip>:5173")
    print("  Backend:  http://<your-ip>:8000")
    print("\nPress Ctrl+C to stop\n")
    
    # Keep running
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\n\nShutdown...")
        sys.exit(0)
