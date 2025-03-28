#!/usr/bin/env python3

import argparse
import os
import subprocess
import cv2

def main():
    parser = argparse.ArgumentParser(
        description="Crop a video by selecting multiple ROIs (lossless cropping) with visual feedback."
    )
    parser.add_argument("input_path", help="Path to the input video.")
    parser.add_argument(
        "output_path",
        help="Full output path for the cropped videos (e.g., '/videos/commoncrop/commonname.mp4')."
    )
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    # Ensure output directory exists. If not, create it.
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Determine base filename and extension
    base_name, ext = os.path.splitext(os.path.basename(output_path))
    if ext == "":
        ext = ".mp4"

    # 1) Check input file existence
    if not os.path.isfile(input_path):
        print(f"Error: The file '{input_path}' does not exist.")
        return

    # 2) Capture first frame
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file '{input_path}'.")
        return

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Error: Could not read the first frame from the video.")
        return

    # 3) Scale down frame if it's larger than MAX_DIM (to fit on screen)
    MAX_DIM = 1080
    orig_height, orig_width = frame.shape[:2]
    largest_dim = max(orig_width, orig_height)
    scaling_factor = 1.0
    if largest_dim > MAX_DIM:
        scaling_factor = MAX_DIM / float(largest_dim)
        new_width = int(orig_width * scaling_factor)
        new_height = int(orig_height * scaling_factor)
        display_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    else:
        display_frame = frame.copy()

    # Create an overlay copy for drawing selected ROIs
    overlay_frame = display_frame.copy()

    # Define a list of colors (in BGR) for each ROI
    colors = [
        (0, 255, 0),   # Green
        (0, 0, 255),   # Red
        (255, 0, 0),   # Blue
        (255, 255, 0), # Cyan
        (0, 255, 255), # Yellow
        (255, 0, 255)  # Magenta
    ]

    # Create a single named window to be used for both ROI selection and feedback
    window_name = "ROI"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    rois = []
    for i in range(6):
        print(f"Select ROI #{i+1} (draw the box and press ENTER; press ESC to cancel selection):")
        # Show the current overlay before selection
        cv2.imshow(window_name, overlay_frame)
        cv2.waitKey(1)  # Allow the window to update
        
        # Use the same window for selection; this will block until selection is made
        roi = cv2.selectROI(window_name, overlay_frame, fromCenter=False, showCrosshair=True)
        
        # If ROI selection is cancelled, (0,0,0,0) is returned.
        if roi == (0, 0, 0, 0):
            print("ROI selection cancelled. Exiting loop.")
            break

        rois.append(roi)
        # Draw the selected ROI on the overlay_frame using the corresponding color
        x, y, w, h = roi
        color = colors[i % len(colors)]
        cv2.rectangle(overlay_frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(overlay_frame, f"ROI {i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        # Update the window with the new overlay
        cv2.imshow(window_name, overlay_frame)
        cv2.waitKey(500)  # Brief pause for visual confirmation

    cv2.destroyWindow(window_name)

    # 4) Process each ROI and crop the video using FFmpeg
    for idx, roi in enumerate(rois, start=1):
        sx, sy, sw, sh = roi
        print(f"ROI {idx} (scaled): x:{sx}, y:{sy}, w:{sw}, h:{sh}")
        # Convert ROI from scaled coordinates back to original dimensions
        if scaling_factor != 1.0:
            x = int(sx / scaling_factor)
            y = int(sy / scaling_factor)
            w = int(sw / scaling_factor)
            h = int(sh / scaling_factor)
        else:
            x, y, w, h = sx, sy, sw, sh

        # Clip ROI to be within image bounds
        x = max(0, min(x, orig_width - 1))
        y = max(0, min(y, orig_height - 1))
        w = max(1, min(w, orig_width - x))
        h = max(1, min(h, orig_height - y))
        print(f"ROI {idx} (original): x:{x}, y:{y}, w:{w}, h:{h}")

        # Create a unique output file name for this ROI
        output_file = os.path.join(output_dir, f"{base_name}_roi{idx}{ext}")
        cmd = [
            "ffmpeg",
            "-hwaccel", "cuda",
            "-i", input_path,
            "-filter:v", f"crop={w}:{h}:{x}:{y}, negate",
            "-an",  # Disable audio if not needed
            "-c:v", "hevc_nvenc",
            "-rc", "constqp",
            "-qp", "20",
            "-preset", "slow",
            "-y",
            output_file
        ]
        print(f"Running FFmpeg command for ROI {idx}:\n{' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
            print(f"Cropping for ROI {idx} completed successfully.")
            print(f"Cropped file saved at: {output_file}\n")
        except subprocess.CalledProcessError as e:
            print(f"Error: FFmpeg failed with return code {e.returncode} for ROI {idx}")
            print(e)

if __name__ == "__main__":
    main()
