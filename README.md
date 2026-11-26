# Computer Vision Portfolio

**Azat Oral | Mechatronics Engineering | İzmir Kâtip Çelebi University**

Computer vision, dataset engineering and experimental machine learning using Python, OpenCV and YOLO.

## Featured Project — TEKNOFEST 2026

**Saturn Rocket Team · MİMAS | Computer Vision Development**

I independently carried out the computer vision and model development work within the team. My responsibilities covered visual data preparation, annotation, dataset organization, YOLO experiments, software development and experimental testing.

### My Contributions

- Prepared and organized visual datasets and annotations.
- Developed Python utilities for visual data preparation and processing.
- Worked with YOLO-family models and conducted model development experiments.
- Developed computer vision software using Python and OpenCV.
- Conducted practical testing in a student engineering project.

### Model Development & Project Archive

The original project archive includes three model files named `yolov8n.pt`, `yolo11n.pt` and `yolo26n.pt`, Python scripts, annotation files and dataset configuration documents.

The checkpoint provenance and training metrics have not been independently verified. The model binaries and original annotations are not included in this public repository. The archive does not contain the corresponding image samples, so it is not a complete reproducible dataset.

**Technical stack:** Python · OpenCV · YOLO · CVAT · Linux · Raspberry Pi

## Published Source Code

| Component | Description |
| --- | --- |
| [Video Frame Extraction](examples/video_processing/extract_frames.py) | Independent offline video processing utility adapted from my original project archive. |
| [Canny Edge Detection](examples/image_processing/edge_detection.py) | Standalone classical image processing example. |
| [Software Tests](tests/test_examples.py) | Functional tests using synthetic media. |

### Example Output

![Illustration of Canny edge extraction](assets/canny-demo.svg)

Synthetic image processing demonstration, separate from the TEKNOFEST model development experiments.

## Getting Started

```bash
python -m pip install -r requirements.txt
python examples/image_processing/edge_detection.py path/to/image.jpg
python examples/video_processing/extract_frames.py ./videos ./frames
python -m unittest discover -s tests -v
```

## References

- Original source: my TEKNOFEST 2026 project archive.
- [OpenCV](https://docs.opencv.org/)
- [Ultralytics](https://docs.ultralytics.com/)
- [CVAT](https://docs.cvat.ai/)
