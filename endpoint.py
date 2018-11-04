import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(('127.0.0.1', 8019))
print("Bound...")
sock.listen(1)
sock.settimeout(1)
conn = None
while conn is None:
    try:
        conn, addr = sock.accept()
    except socket.timeout:
        print("Timeout")

print("Accepted...")
while True:
    try:
        data = conn.recv(1024)
        print(data)
    except socket.timeout:
    	pass
