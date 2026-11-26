# Computer Vision Portfolio

**Azat Oral · Mechatronics Engineering · İzmir Kâtip Çelebi University**

I work with Python and OpenCV on image processing, dataset preparation, and embedded computer vision. This portfolio brings together a team project case study and a standalone implementation.

## Portfolio

| Project | What it demonstrates |
| --- | --- |
| [TEKNOFEST 2026 computer vision case study](projects/teknofest_2026/README.md) | My contributions to image collection, frame extraction, CVAT annotation, and laboratory testing with Saturn Rocket Team (MİMAS) |
| [Canny edge detection](examples/image_processing/edge_detection.py) | Grayscale conversion, Gaussian smoothing, and edge extraction on a local image |

## Run the OpenCV example

From the repository root, install the dependency and give the script the path to a local image.

```bash
python -m pip install -r requirements.txt
python examples/image_processing/edge_detection.py path/to/image.jpg
```

The script opens the original image and the edge map in separate desktop windows. Press any key in an OpenCV window to close them.

**Verification.** With OpenCV 4.6.0, the image-processing path produced 188 edge pixels for a 96 × 96 synthetic image containing a white square. Window display was disabled during this test.
