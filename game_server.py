import socket
import threading

# Define a Player class to hold information about each player
class Player:
    def __init__(self, conn, address):
        self.conn = conn  # The socket connection for this player
        self.address = address  # The address of the player
        self.username = None  # The player's username
        self.score = 0  # The player's score
        self.choice = None  # The player's choice in the current round

# Function to authenticate a player by asking for their username
def authenticate_player(player):
    player.conn.sendall(b"Enter your username: ")  # Prompt for username
    player.username = player.conn.recv(1024).decode().strip()  # Receive username
    player.conn.sendall(f"Welcome, {player.username}!\n".encode())  # Welcome message

# Function to get the player's choice of rock, paper, or scissors
def get_choice(player):
    while True:
        player.conn.sendall(b"Enter your choice (rock, paper, scissors): ")  # Prompt for choice
        choice = player.conn.recv(1024).decode().strip()  # Receive choice
        if choice in ["rock", "paper", "scissors"]:  # Validate choice
            return choice  # Return valid choice
        player.conn.sendall(b"Invalid choice. Please enter rock, paper, or scissors.\n")  # Error message

# Function to handle the game logic for both players
def handle_game(player1, player2):
    # Notify both players that the game is starting
    player1.conn.sendall(b"Both players are connected. Let's start the game!\n")
    player2.conn.sendall(b"Both players are connected. Let's start the game!\n")

    for _ in range(5):  # Loop for 5 rounds
        # Get choice from player1
        player1.choice = get_choice(player1)
        player2.conn.sendall(f"Waiting for {player1.username} to make a choice...\n".encode())

        # Get choice from player2
        player2.choice = get_choice(player2)

        # Determine the outcome of the round
        result = determine_outcome(player1.choice, player2.choice)

        # Send round results to both players
        send_round_results(player1, player2, result)

    # Declare final scores after all rounds are done
    final_message = f"Game over! {player1.username}: {player1.score}, {player2.username}: {player2.score}\n"
    player1.conn.sendall(final_message.encode())
    player2.conn.sendall(final_message.encode())

# Function to determine the outcome of the round based on player choices
def determine_outcome(choice1, choice2):
    if choice1 == choice2:  # If choices are the same, it's a tie
        return "tie"
    # Determine if player1 wins
    if (choice1 == "rock" and choice2 == "scissors") or \
       (choice1 == "paper" and choice2 == "rock") or \
       (choice1 == "scissors" and choice2 == "paper"):
        return "player1"
    return "player2"  # Otherwise, player2 wins

# Function to send round results to both players
def send_round_results(player1, player2, result):
    if result == "tie":
        player1.conn.sendall(b"This round is a tie!\n")
        player2.conn.sendall(b"This round is a tie!\n")
    elif result == "player1":
        player1.score += 1  # Increment player1's score
        player1.conn.sendall(b"You win this round!\n")
        player2.conn.sendall(f"{player1.username} wins this round!\n".encode())
    else:
        player2.score += 1  # Increment player2's score
        player1.conn.sendall(f"{player2.username} wins this round!\n".encode())
        player2.conn.sendall(b"You win this round!\n")

# Main function to set up the server and accept player connections
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
    server.bind(("", 5000))  # Bind the server to localhost on port 8080
    server.listen(2)  # Listen for up to 2 connections
    print("Server started on :5000")

    players = []  # List to hold the player connections

    while len(players) < 2:  # Loop until we have 2 players
        conn, address = server.accept()  # Accept a new connection
        print(f"Connection from {address} has been established.")
        player = Player(conn, address)  # Create a new Player instance

        authenticate_player(player)  # Authenticate the player
        players.append(player)  # Add the player to the list

        if len(players) == 2:  # If we have 2 players, start the game
            # Start the game in a new thread
            threading.Thread(target=handle_game, args=(players[0], players[1])).start()

# Entry point of the program
if __name__ == "__main__":
    main()  # Run the main function
