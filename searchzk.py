from kazoo.client import KazooClient
import re
import os
import networkx as nx

# Connect to ZooKeeper
zk = KazooClient(hosts='172.20.0.2:2181')
zk.start()

# Define the regex pattern to match IP addresses and ports
pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)')

# Recursive function to search through all znodes
def search_znodes(znode, services):
    # Get the data of the current znode
    data, stat = zk.get(znode)
    # Check if the data matches the regex pattern
    match = pattern.search(data.decode())
    if match:
        # Extract the IP address and port from the matched string
        ip_port = match.group(1)
        # Get the name of the znode (which is assumed to be the name of the service)
        service_name = znode
        # Add the service and its IP address and port to the output dictionary
        services[service_name] = ip_port
    # Recursively search through all child znodes
    for child in zk.get_children(znode):
        search_znodes(znode + '/' + child, services)

# Call the recursive function to search through all znodes
services = {}
search_znodes('/', services)

# Recursive function to search through all files from the current directory
def search_files(path, services, graph, current_service=None):
    if os.path.isfile(path):
        return
    # Iterate over all files in the current directory
    for filename in os.listdir(path):
        # Ignore hidden files and directories
        if filename.startswith('.'):
            continue
        filepath = os.path.join(path, filename)
        # Recursively search subdirectories
        if os.path.isdir(filepath):
            search_files(filepath, services, graph, current_service=current_service)
        # Search for mentions of the services in the file
        elif os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                for service in services:
                    # Split the service name by '/' and search for each segment separately
                    segments = service.split('/')
                    for i in range(1, len(segments)):
                        segment = segments[i]
                        if segment and segment in content:
                            # Add an edge to the call graph
                            graph.add_edge(filepath, service)
                            # Recursively search for other services in the file
                            search_files(filepath, services, graph, current_service=service)
                            break

# Call the recursive function to search through all files
graph = nx.DiGraph()
search_files('.', services, graph)

# Print the output
for service, ip_port in services.items():
    print(f'{service}: {ip_port}')
# Get a list of unique edges in the graph
unique_edges = list(set(graph.edges))

# Remove the current graph edges
graph.clear()

# Re-add the unique edges
graph.add_edges_from(unique_edges)

# Print the call graph
print('Call graph:')
print(graph.edges())

# Close the ZooKeeper connection
zk.stop()

