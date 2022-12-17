# Multiplayer Battleship 2
A second version (and rewrite with a GUI) of my multiplayer battleship game made almost 1 year ago. This is a clone of Hasbro's Battleship game (however I plan on adding more things that the original game doesn't have).

# Setting up

## Player

### 1. Downloading

First, all dependencies must be satisfied. Make sure Python 3.10 is installed. You can download it [here](https://www.python.org/downloads/release/python-3109/).

Then install Pygame:
```
$ python3 -m pip install pygame
```

After Python is installed, you can download the latest version of this project.
Download the source code from the [latest release](https://github.com/AlexanderJCS/multiplayer-battleship-2/releases). Then, unzip the file. After, navigate to `multiplayer-battleship-2/client` and run `client.py`.

If this does not work, double check that all dependencies (Pygame) are met.

## Server

### 1. Port Forwarding
On the server network, please make sure that port 9850 is open. This is the port used for all communication between the client and server when the game is running.

### 2. Running the Server

First, download Python 3.10 (newer Python3 versions should work, but Python 3.10 is what is tested).

To run the server, download the source code from the [latest release](https://github.com/AlexanderJCS/multiplayer-battleship-2/releases), unzip the file, and navigate to the `multiplayer-battleship-2/server` directory. Then, run `server.py`:

```
$ python3 server.py
```

Console output is currently not supported, so don't be surprised when you don't see anything in the console. This will be added in a later date.

# Contributing

Contributing is welcome, but please keep this section in mind when doing so.

## Issues

Please try to be as descriptive as possible with error messages and provide any console output. If the console closes, you can run the program in the console to see any errors that were thrown.

## Pull Requests

For minor changes, please make a pull request and state what you changed. Please make one pull request per change.

For major changes, please create an issue the change can be discussed before time and effort is put into the change.
