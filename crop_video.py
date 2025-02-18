#!/usr/bin/env python3

import argparse
import os
import subprocess
import cv2

def main():
    parser = argparse.ArgumentParser(
        description="Crop a video by selecting an ROI from the first frame."
    )
    parser.add_argument("input_path", help="Path to the input video.")
    parser.add_argument("output_path", help="Path for the cropped output video.")
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

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

    # 3) Scale down frame if it's larger than MAX_DIM in width or height
    MAX_DIM = 1080  # Adjust based on your monitor or preference
    orig_height, orig_width = frame.shape[:2]

    largest_dim = max(orig_width, orig_height)
    scaling_factor = 1.0
    if largest_dim > MAX_DIM:
        scaling_factor = MAX_DIM / float(largest_dim)
        new_width = int(orig_width * scaling_factor)
        new_height = int(orig_height * scaling_factor)
        display_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    else:
        display_frame = frame

    # 4) Let user select ROI on the (possibly) scaled frame
    roi = cv2.selectROI("Select Crop Region", display_frame, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    sx, sy, sw, sh = roi
    print(f"Scaled ROI => x:{sx}, y:{sy}, w:{sw}, h:{sh}")

    # 5) Convert scaled ROI back to original coordinates
    if scaling_factor != 1.0:
        x = int(sx / scaling_factor)
        y = int(sy / scaling_factor)
        w = int(sw / scaling_factor)
        h = int(sh / scaling_factor)
    else:
        x, y, w, h = sx, sy, sw, sh

    # 6) Clip ROI to avoid going out of image bounds
    x = max(0, min(x, orig_width - 1))
    y = max(0, min(y, orig_height - 1))
    w = max(1, min(w, orig_width - x))
    h = max(1, min(h, orig_height - y))

    print(f"Final ROI => x:{x}, y:{y}, w:{w}, h:{h}")

    # 7) Construct FFmpeg command to crop with NVIDIA GPU (NVENC)
    cmd = [
        "ffmpeg",
        # Use CUDA for hardware acceleration (decoding) if supported
        "-hwaccel", "cuda",
        "-i", input_path,
        # Crop filter: crop=w:h:x:y
        "-filter:v", f"crop={w}:{h}:{x}:{y}",
        # Copy audio without re-encoding
        "-c:a", "copy",
        # Encode video using GPU-based h264_nvenc
        "-c:v", "h264_nvenc",
        # CRF/preset can be tuned as desired
        "-crf", "23",
        "-preset", "fast",
        # Overwrite output if it exists
        "-y",
        output_path
    ]

    print("Running FFmpeg command:\n", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        print("Cropping completed successfully.")
        print(f"Cropped file saved at: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg failed with return code {e.returncode}")
        print(e)

if __name__ == "__main__":
    main()
