import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 8018))
sock.send('{"type": "IK", "deltaX": 0.0, "deltaY": 0, "deltaZ": 0, "deltaTilt": 0, "deltaJointE": 0}'.encode())
# sock.send('{"type": "FK", "joint_a": 1.57, "joint_b": -0.5, "joint_c": 0, "joint_d": 0, "joint_e": 0}'.encode())


# sock.bind(('127.0.0.1', 8019))
# print("Bound...")
# sock.listen(1)
# sock.settimeout(1)
# conn = None
# while conn is None:
#     try:
#         conn, addr = sock.accept()
#     except socket.timeout:
#         print("Timeout")

# print("Accepted...")
# while True:
#     try:
#         data = conn.recv(1024)
#         print(data)
#     except socket.timeout:
#     	pass
