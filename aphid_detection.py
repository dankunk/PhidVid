import cv2
import argparse
from ultralytics import YOLO
import supervision as sv
#from inference.models.utils import get_robo_flowmodel

# setting path to video 
video_path = "./videos/Camera0_20250326_151512_0-215999.mp4"
print(f"Video found: {video_path}")

# path to model 
model = YOLO('yolov8n.pt')

# setting frames with supervision
#frame_generator = sv.get_video_frames_generator(video_path)
#
#window_name = "arbitrary_window_name"
#win_height = 1280
#win_width = 720

# for frame in frame_generator:
#     # showing image by first creating window
#     cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
#     # resizing in 16:9 
#     cv2.resizeWindow(window_name, win_height, win_width)
#     # showing window
#     cv2.imshow(window_name, frame)
#     if cv2.waitKey(1) == ord("q"):
#         print("Stopping Video Stream...")
#         break
# cv2.destroyAllWindows()

cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    width = int(cap.get(3))
    height = int(cap.get(4))

    if success:
        
        # Run YOLOv8 inference on the frame
        resized_frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_LINEAR)

        # Visualize the results on the frame
        results = model(resized_frame, conf=0.1,classes=2)
        
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    else:
        # Break the loop if the end of the video is reached
        break

cap.release()
cv2.destroyAllWindows()
