import socket
import time
import kazoo.client
import threading

def register_service():
    # Register the service with Apache Zookeeper
    print("registering myself")
    zk = kazoo.client.KazooClient(hosts="172.20.0.2:2181")
    zk.start()
    service_path = "/services/service1"
    zk.ensure_path(service_path)
    zk.create(service_path + "/node", b"172.20.0.3:10000")
    print("finished registering myself")

def find_service():
    # Search for another service in Apache Zookeeper
    zk = kazoo.client.KazooClient(hosts="172.20.0.2:2181")
    zk.start()
    service_path = "/services/service2"
    if zk.exists(service_path):
        children = zk.get_children(service_path)
        for child in children:
            node, _ = zk.get(service_path + "/" + child)
            address = node.decode("utf-8")
            print("address found at: " + str(address))
            host, port = address.split(":")
            return host, int(port)
    return None, None

def receive_hello():
    # Open a socket to receive "hello world"
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 10000))
    server_socket.listen(1)
    while True:
        client_socket, client_address = server_socket.accept()
        data = client_socket.recv(1024).decode("utf-8")
        print("Received from client:", data)
        client_socket.close()

def send_hello(host, port):
    # Connect to another service and send "hello world"
    try:
        print("sending hello world to: " + str(host))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        client_socket.send("hello world".encode("utf-8"))
        client_socket.close()
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    print("starting")
    register_service()
    receive_thread = threading.Thread(target=receive_hello)
    receive_thread.start()
    while True:
        host, port = find_service()
        if host is not None and port is not None:
            send_hello(host, port)
        time.sleep(1)

