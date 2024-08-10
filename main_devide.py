import socket
import threading
import pickle
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import zipfile
import os

# main.....................................
PORT = 5000
BUFFER_SIZE = 4096
NUM_DEVICES = 4


def handle_device_connection(conn, addr, image_datas):
    print(f"Connected to {addr}")
    data = b""

    # Receive data in chunks
    while True:
        packet = conn.recv(BUFFER_SIZE)
        if not packet:
            break
        data += packet

    # Save the received data as a ZIP file
    zip_path = "received.zip"
    with open(zip_path, "wb") as f:
        f.write(data)

    # Create an extraction directory if it doesn't exist
    extract_dir = "extracted_files"
    os.makedirs(extract_dir, exist_ok=True)

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

        # Process each file in the ZIP archive
        for file_name in zip_ref.namelist():
            file_path = os.path.join(extract_dir, file_name)

            # Determine the file type
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                # Process image files
                img = mpimg.imread(file_path)
                if img is not None:
                    print(f"Displaying image: {file_name}")
                    plt.figure(figsize=(8, 6))
                    plt.imshow(img)
                    plt.title(f"Received Image - {file_name}")
                    plt.axis('off')  # Hide axes
                    plt.show()
                    with open(file_path, "rb") as f:
                        image_datas.append(f.read())
                else:
                    print(f"Failed to load image from: {file_path}")
            elif file_name.lower().endswith('.txt'):
                # Process text files
                with open(file_path, 'r') as f:
                    text_data = f.read()
                    print(f"Content of text file {file_name}:")
                    print(text_data)
            else:
                print(f"Unsupported file type: {file_name}")

    print(f"DATA appended {len(image_datas)}")
    conn.close()


def start_main_device():
    image_datas = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen(NUM_DEVICES)

    print("Waiting for device connections...")
    threads = []
    for _ in range(NUM_DEVICES):
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_device_connection, args=(conn, addr, image_datas))
        thread.start()
        threads.append(thread)
    print("")
    for thread in threads:
        thread.join()

    server_socket.close()
    print("socket closed")
    print(len(image_datas))


if _name_ == "_main_":
    start_main_device()