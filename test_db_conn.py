import socket
import time

def test_conn(host, port):
    start = time.time()
    try:
        s = socket.create_connection((host, int(port)), timeout=5)
        s.close()
        end = time.time()
        print(f"✅ Connected to {host}:{port} in {end - start:.4f}s")
    except Exception as e:
        print(f"❌ Failed to connect to {host}:{port} - {e}")

print("Testing DB Connection Speed...")
port = 5433 # From docker-compose

print("\n--- Test 1: localhost ---")
test_conn("127.0.0.1", port)

print("\n--- Test 2: localhost (DNS) ---")
test_conn("localhost", port)

print("\n--- Test 3: host.docker.internal ---")
test_conn("host.docker.internal", port)
