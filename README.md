# Computer Vision Portfolio

**Azat Oral · Mechatronics Engineering · İzmir Kâtip Çelebi University**

I work with Python and OpenCV on image processing, dataset preparation, and embedded computer vision. This portfolio includes standalone OpenCV implementations for image and offline video processing.

## Portfolio

| Project | What it demonstrates |
| --- | --- |
| [Canny edge detection](examples/image_processing/edge_detection.py) | Grayscale conversion, Gaussian smoothing, and edge extraction on a local image |
| [Offline video frame extraction](examples/video_processing/extract_frames.py) | Sampling local MP4 videos and exporting JPEG frames |

## Run the OpenCV example

From the repository root, install the dependency and give the script the path to a local image.

```bash
python -m pip install opencv-python
python examples/image_processing/edge_detection.py path/to/image.jpg
```

The script opens the original image and the edge map in separate desktop windows. Press any key in an OpenCV window to close them.

**Verification.** With OpenCV 4.6.0, the image-processing path produced 188 edge pixels for a 96 × 96 synthetic image containing a white square. Window display was disabled during this test.

## Offline video processing

The frame extraction utility is adapted from my 2026 student competition project archive, with machine-specific paths replaced by command-line arguments. It processes local video files independently of any detection or control system.

```bash
python examples/video_processing/extract_frames.py ./videos ./frames
```

The default sampling interval is 0.08 seconds (rounded to whole video frames). Use an empty output directory to avoid overwriting existing images.
