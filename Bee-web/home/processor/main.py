from ultralytics import YOLO
import cv2
import os
import time
def return_time():
    return str(time.time())

# Load the YOLO model
model = YOLO(os.path.join(os.path.dirname(__file__), 'best_bkl.pt'))

def process (name):
    # Check if the file exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__),'../../media/videos', name)):
        print("File not found")
        return
    else:
        pass
    # Path to the video file
    video_path = os.path.join(os.path.dirname(__file__),'../../media/videos', name)
    output_path = os.path.join(os.path.dirname(__file__),'../../media/return_videos', name.split('.')[0] + '_output.mp4')
    process_path = os.path.join(os.path.dirname(__file__),'../../media/return_videos', name.split('.')[0] + '_p_output.mp4')
    

    # Load the video
    cap = cv2.VideoCapture(video_path)

    # Get video details
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define the codec and create VideoWriter object
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Process the video frame by frame
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break  # Exit loop when the video ends

        # Perform inference with YOLO
        results = model(frame)

        # Draw the results on the frame
        annotated_frame = results[0].plot()

        # Write the frame to the output video
        out.write(annotated_frame)
        print("Frame processed")

        # # Optional: Display the video in real-time
        # cv2.imshow('YOLO Detection', annotated_frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # Release resources
    cap.release()
    out.release()
    # cv2.destroyAllWindows()
    print("Video processing complete. Saved to:", output_path)
    # Run ffmpeg -i output_video.mp4 -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p otput_video.mp4
    os.system(f'ffmpeg -i {output_path} -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p {process_path}')