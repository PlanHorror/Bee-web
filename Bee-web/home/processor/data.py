import time
import socket
import cv2
import numpy as np
import json
import struct
import threading
from flask import Flask, Response, jsonify
from flask_cors import CORS

# Configuration
VIDEO_PORT = 65433  # Port for video stream
SENSOR_PORT = 65432  # Port for sensor data
HOST = '0.0.0.0'  # Listen on all interfaces

app = Flask(__name__)
CORS(app)
# Global variables to store the latest video frame and sensor data
latest_frame = None
latest_sensor_data = None

# Function to update the latest video frame
def update_latest_frame(frame):
    global latest_frame
    latest_frame = frame

# Function to update the latest sensor data
def update_latest_sensor_data(data):
    global latest_sensor_data
    latest_sensor_data = data

# Flask route to return the video stream
@app.route('/cam')
def video_feed():
    def generate():
        while True:
            if latest_frame is not None:
                ret, jpeg = cv2.imencode('.jpg', latest_frame)
                if ret:
                    frame = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            time.sleep(0.1)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Flask route to return the sensor data
@app.route('/sen')
def sensor_data():
    if latest_sensor_data is not None:
        response = jsonify(latest_sensor_data)
    else:
        response = jsonify({"error": "No sensor data available"}), 404

    # response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Update the handle_video_stream function to call update_latest_frame
def handle_video_stream():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as video_socket:
        video_socket.bind((HOST, VIDEO_PORT))
        video_socket.listen(1)
        print(f"Video server listening on port {VIDEO_PORT}")

        client_socket, addr = video_socket.accept()
        print(f"Video client connected from {addr}")

        while True:
            try:
                frame_length_data = client_socket.recv(4)
                if not frame_length_data:
                    break

                frame_length = struct.unpack('>I', frame_length_data)[0]

                frame_data = b''
                while len(frame_data) < frame_length:
                    packet = client_socket.recv(frame_length - len(frame_data))
                    if not packet:
                        break
                    frame_data += packet

                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                update_latest_frame(frame)

            except Exception as e:
                print(f"Error receiving video: {e}")
                break

# Update the handle_sensor_data function to call update_latest_sensor_data
def handle_sensor_data():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sensor_socket:
        sensor_socket.bind((HOST, SENSOR_PORT))
        sensor_socket.listen(1)
        print(f"Sensor server listening on port {SENSOR_PORT}")

        client_socket, addr = sensor_socket.accept()
        print(f"Sensor client connected from {addr}")

        while True:
            try:
                sensor_data = client_socket.recv(1024).decode()
                if not sensor_data:
                    break

                data = json.loads(sensor_data)
                update_latest_sensor_data(data)

            except json.JSONDecodeError:
                print("Failed to decode JSON. Skipping...")
            except Exception as e:
                print(f"Error receiving sensor data: {e}")
                break

# Main function to start the server
def main():
    try:
        threading.Thread(target=handle_video_stream, daemon=True).start()
        threading.Thread(target=handle_sensor_data, daemon=True).start()

        app.run(host='0.0.0.0', port=5000, debug=False, ssl_context='adhoc')
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")
# Function to handle video streaming
# def handle_video_stream():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as video_socket:
#         video_socket.bind((HOST, VIDEO_PORT))
#         video_socket.listen(1)
#         print(f"Video server listening on port {VIDEO_PORT}")

#         client_socket, addr = video_socket.accept()
#         print(f"Video client connected from {addr}")

#         while True:
#             try:
#                 # Receive the length of the frame data (4 bytes)
#                 frame_length_data = client_socket.recv(4)
#                 if not frame_length_data:
#                     break

#                 frame_length = struct.unpack('>I', frame_length_data)[0]

#                 # Receive the frame data
#                 frame_data = b''
#                 while len(frame_data) < frame_length:
#                     packet = client_socket.recv(frame_length - len(frame_data))
#                     if not packet:
#                         break
#                     frame_data += packet

#                 # Decode the frame and display it
#                 frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
#                 cv2.imshow("Received Video", frame)

#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break

#             except Exception as e:
#                 print(f"Error receiving video: {e}")
#                 break

#         cv2.destroyAllWindows()


# # Function to handle sensor data
# def handle_sensor_data():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sensor_socket:
#         sensor_socket.bind((HOST, SENSOR_PORT))
#         sensor_socket.listen(1)
#         print(f"Sensor server listening on port {SENSOR_PORT}")

#         client_socket, addr = sensor_socket.accept()
#         print(f"Sensor client connected from {addr}")

#         while True:
#             try:
#                 # Receive sensor data (ensure full message is received)
#                 sensor_data = client_socket.recv(1024).decode()
#                 if not sensor_data:
#                     break

#                 # Parse and print the sensor data
#                 data = json.loads(sensor_data)
#                 print(f"Received Sensor Data: {data}")

#             except json.JSONDecodeError:
#                 print("Failed to decode JSON. Skipping...")
#             except Exception as e:
#                 print(f"Error receiving sensor data: {e}")
#                 break


# # Main function to start the server
# def main():
#     app.run(host='0.0.0.0', port=5000)
#     try:
#         # Start threads for video and sensor servers
#         threading.Thread(target=handle_video_stream, daemon=True).start()
#         threading.Thread(target=handle_sensor_data, daemon=True).start()

#         # Keep the main thread running
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("\nServer shutting down gracefully.")


if __name__ == '__main__':
    main()