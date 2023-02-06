import kazoo.client

# Connect to Zookeeper instance
zk = kazoo.client.KazooClient(hosts="172.20.0.2:2181")
zk.start()
service_path = "/services/service1"
if zk.exists(service_path):
    children = zk.get_children(service_path)
    for child in children:
        node, _ = zk.get(service_path + "/" + child)
        address = node.decode("utf-8")
        host, port = address.split(":")
        print(str(host) +":" + str(int(port)))
