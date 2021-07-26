# SDSS
Simple Delay Sync Service,
# Intro 🚪
Distributed systems play an important role in our lives today; there is a huge number of Google servers that exist around the globe or machines in Amazon's cloud. <br />
This program is peer-to-peer networking. <br />
No single node is the server,a node can either be a client or a server or switch from one to another. <br />
Here, we measure delay between nodes (i.e. devices) and their peers in order to distribute a workload in the most efficient way. <br />
# What does the program do exactly? <br />
1. each node sends a broadcast message once every second, so other nodes know about its existence. <br />
2. once node [A] detects a message from a non-recognized node [B]; it'll initiate a TCP connection to node [B]. <br />
3. Node B will send a TCP message to node [A] containing [B]'s timestamp. <br />
4. Node [A] will compute the delay by subtracting A's timestamp from B's timestamp, then it'll store that delay in a hashtable containing the node ID as key and its (delay, broadcast_count) as values [NeighborInfo object]. This will be the delay from [B] -> [A], we won't need to compute the delay in the other direction. Each node will know the delay "to" its neighbors only not in both ways. <br />
5. This table is updated every 10 broadcasts for each node. <br />
# Protocol Format
All broadcast messages are sent/received over port number 35498 which is included  as get_broadcast_port(). <br />
1-Broadcast Message [UDP] <br />
We always need to broadcast a message to inform peers in the network of node's existence. Towards that end, the following message format is used. <br />
[NODE_UUID] ON [TCP_SERVER_PORT] <br />

 -NODE_UUID is a randomly generated 8-char partial-UUID (string) to identify each node, it changes every time code is run. <br />
 -TCP_SERVER_PORT the random TCP server port assigned by the operating system to our socket. <br />
 -Each token in a protocol message is followed by a space, except the last one. <br />
 -Encode/Decode messages as UTF-8. <br />
 -ON is uppercase. <br />
2-Timestamp [TCP] <br />
Nodes are exchanging UTC timestamps not the system-wide timestamps. <br />
# Implemenattion steps:
1. every function that ends with _thread is run in its own thread. <br />
2. TCP socket is set and starts accepting clients (tcp_server_thread). <br />
3. UDP socket is set  and send broadcasts (send_broadcast_thread). <br />
4. Received broadcasts are parsed (receive_broadcast_thread). <br />
5. TCP clients are accepted and get sent node's timestamp and connection gets closed  (tcp_server_thread). <br />
6. TCP connection is Initiated  to newly discovered nodes and timestamps  get exchanged (exchange_timestamps_thread). <br />
7. neighbor information  is refreshed every 10 broadcasts. <br />





