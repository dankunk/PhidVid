# PhidVid

PhidVid provides a simple script to crop aphid behavior videos via an interactive, draggable ROI (Region of Interest) selection. It uses OpenCV to display the first frame of a video and FFmpeg with NVIDIA GPU acceleration (NVENC) to process the crop.

---

## 1. Environment Setup

1. **Clone this repository (or download the scripts if not using Git):**

   ```bash
   git clone https://github.com/YourUsername/PhidVid.git
   cd PhidVid
   
2. Create and activate the conda environment (named phidvid) using the provided YAML file:

   ```bash
   conda env create -f phidvid_env.yml
   conda activate phidvid

3. Verify that ffmpeg has NVIDIA NVENC support (for GPU encoding which you probably want to use)

   ```
   ffmpeg -encoders | grep nvenc
You should see encoders like h264_nvenc. If not, you may need a different FFmpeg build with NVENC enabled.

## 2. Usage 

1. Activate the environment:

   ``` bash
   conda activate phidvid

2. Run the ```crop_video.py``` script with the input and output file paths specified (either cd to the dir or provide full path)
   ``` bash
   python crop_video.py /path/to/input_video.mp4 /path/to/output_cropped.mp4
   
- ```/path/to/input_video.mp4```: Full or relative path to your original video.
- ```/path/to/output_cropped.mp4```: Path (and filename) for saving the cropped video.

3. A window will pop up showing the first frame of the video. Click and drag the mouse to define the cropping rectangle.

   - Press Enter to confirm Selection. Press c to cancel.
   - The window will close automatically.

4. FFmpeg processes the video using your NVIDIA GPU if available (NVENC). It then saves the cropped video to your specified output path.

## 3. Customizing the Crop Window Scale

By default, any dimension larger than **1080 pixels** is scaled down for the ROI selection so you can see the entire frame on most screens. You can adjust the variable ```MAX_DIM``` in ```crop_video.py``` if you need:

```python
MAX_DIM = 1080
```

## 4. Notes

- NVIDIA GPU Encoding:
   - Ensure your machine has a compatible NVIDIA GPU and the appropriate FFmpeg version (with NVENC support).
   - You can adjust the CRF and preset options for H.264 NVENC if desired.
- CPU Usage:
   - Even with GPU encoding, some CPU usage is normal for demuxing, scaling, or other overhead.
- Audio:
   - The script copies the audio track (-c:a copy) without re-encoding. If the input video does not contain audio, this will not affect anything.

## 5. Troubleshooting

1. ROI Window Too Large / Off-screen:

   - Decrease MAX_DIM in crop_video.py so the frame is scaled further down.
   - Alternatively, use a larger monitor or higher resolution setting.

2. GPU Not Detected:

   - Check ffmpeg -encoders | grep nvenc. If no entries appear, install an FFmpeg build with NVENC support.
   - Confirm NVIDIA drivers are properly installed on your system.

3. Slow Performance:

   - Adjust the preset to -preset fast, -preset medium, or even -preset slower for different trade-offs between speed and compression.
   - For purely fastest encodes, try -preset p7 or -preset hp depending on your FFmpeg’s supported NVENC presets.

4. Cropping Region:

   - Ensure you press Enter after drawing the box.
   - The script automatically clamps any out-of-bound coordinates.







   

