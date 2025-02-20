#!/usr/bin/env python3

import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(
        description="Invert colors and increase contrast of a video using GPU acceleration (NVENC) for fast, lossless encoding."
    )
    parser.add_argument("input_video", help="Path to the input video file.")
    parser.add_argument("output_video", help="Path to the output (processed) video file.")
    parser.add_argument("--contrast", type=float, default=1.5,
                        help="Contrast multiplier (default is 1.5; values >1 increase contrast).")
    args = parser.parse_args()

    if not os.path.isfile(args.input_video):
        print(f"Error: The input file '{args.input_video}' does not exist.")
        return

    # Build filter chain: first invert colors, then adjust contrast.
    filter_chain = f"negate,eq=contrast={args.contrast}"

    # Construct the FFmpeg command using GPU acceleration:
    #   -hwaccel cuda         -> Use GPU for accelerated decoding (if supported)
    #   -c:v h264_nvenc        -> Use NVIDIA's GPU-based H.264 encoder
    #   -qp 0                  -> Attempt lossless encoding (if supported)
    #   -preset lossless       -> NVENC preset for lossless encoding (your build/GPU must support this)
    #   -c:a copy             -> Copy the audio stream without re-encoding
    cmd = [
        "ffmpeg",
        "-hwaccel", "cuda",
        "-i", args.input_video,
        "-vf", filter_chain,
        "-c:v", "h264_nvenc",
        "-qp", "0",             # Lossless encoding attempt
        "-preset", "lossless",  # NVENC lossless preset
        "-c:a", "copy",
        "-y",
        args.output_video
    ]

    print("Running FFmpeg command:")
    print(" ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
        print("Video processed successfully (GPU-accelerated, lossless).")
        print(f"Processed file saved at: {args.output_video}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed with return code {e.returncode}")
        print(e)

if __name__ == "__main__":
    main()
