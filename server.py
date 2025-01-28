import socket


clients = []
# Create a server socket
serverSocket = socket.socket()

print("Server socket created")

# Associate the server socket with the IP and Port
ip = "127.0.0.1"
port = 9999

serverSocket.bind((ip, port))

print("Server socket bound with ip {} port {}".format(ip, port))

# Make the server listen for incoming connections
serverSocket.listen()

# Server incoming connections "one by one"
count = 0
TIME_COMMAND = "Time 30"

def send_and_wait_ack(client, message, player_index):
    """Send a message to the client and wait for acknowledgment."""
    client.send(str.encode(message))
    response = client.recv(1024).decode()
    if response != "OK":
        print(f"Unexpected response from client: {response}")
    else:
        print(f"Client {player_index}: {message} -> {response}")
       

while True:
    # Wait for the two agents to connect
    (clientConnection, clientAddress) = serverSocket.accept()
    count += 1
    clients.append(clientConnection)

    (clientConnection, clientAddress) = serverSocket.accept()
    count += 1
    clients.append(clientConnection)

    print("Accepted {} connections".format(count))

    # Send "Connected to the server" to both clients
    send_and_wait_ack(clients[0], "Connected to the server", 0)
    send_and_wait_ack(clients[1], "Connected to the server", 1)

    # Send time to clients
    send_and_wait_ack(clients[0], TIME_COMMAND, 0)
    send_and_wait_ack(clients[1], TIME_COMMAND, 1)

    # Handle Setup command for initial position
    setup_positions = "Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2 Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7"
    send_and_wait_ack(clients[0], "Setup " + setup_positions, 0)
    send_and_wait_ack(clients[1], "Setup " + setup_positions, 1)

    # Send Begin message to clients after the setup
    send_and_wait_ack(clients[0], "Begin", 0)
    send_and_wait_ack(clients[1], "Begin", 1)

    # Send the game colors to both players
    send_and_wait_ack(clients[0], "White", 0)
    send_and_wait_ack(clients[1], "Black", 1)

    # Start the game logic
    player_index = 0  # White starts first

    while True:
        # Notify the other player of the turn
        if player_index == 0:
            send_and_wait_ack(clients[1], "White's turn", 0)
        else:
            send_and_wait_ack(clients[0], "Black's turn", 1)


        msg = str.encode("Your turn")
        clients[player_index].send(msg)
        try:
            data = clients[player_index].recv(1024)
            if not data:  # If no data is received, the connection is closed
                break
        except ConnectionAbortedError as e:
            print(f"Connection was aborted for player {player_index}: {e}")
            break
        if data:
            data = data.decode()
            print(f"Client {player_index}: {data}")

            if data == "exit":
                # Notify both clients of game termination
                clients[0].send(str.encode("exit"))
                clients[1].send(str.encode("exit"))
                print("Agent wants to end the game. Connection closed.")
                break

            if data.startswith("Win"):
                winner = data.split()[1]  # Extract the winner's color (either "White" or "Black")
                if winner == "White":
                    print("White player won!")
                elif winner == "Black":
                    print("Black player won")
                clients[0].send(str.encode("exit"))
                clients[1].send(str.encode("exit"))
                break

            # Send the move to the opponent
            player_index = 1 - player_index
            clients[player_index].send(data.encode())

    break
