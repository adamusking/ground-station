import threading
import queue
import sys
import time

input_queue = queue.Queue()
def read_input():
    """Reads full-linende input in a separate thread and stores it in a queue."""
    while True:
        user_input = sys.stdin.readline().strip()
        input_queue.put(user_input)

# Start the input thread
threading.Thread(target=read_input, daemon=True).start()

print("Type a command and press Enter.")

while True:

    if not input_queue.empty():
        command = input_queue.get()
        print(f"Received command: {command}")

    time.sleep(1)  # Simulated delay
