import kazoo.client

# Connect to Zookeeper instance
zk = kazoo.client.KazooClient(hosts="172.20.0.2:2181")

# Start the connection
zk.start()

# Your code here
service_path = "/services/service1"
zk.ensure_path(service_path)
zk.create(service_path + "/node", b"127.0.0.1:10000")
# Stop the connection when done
zk.stop()

