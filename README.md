# Computer Vision Portfolio

**Azat Oral — Mechatronics Engineering | İzmir Kâtip Çelebi University**

Practical computer vision projects using Python, OpenCV and visual data processing.

## TEKNOFEST 2026

Computer vision development with Saturn Rocket Team — MİMAS.

My work focused on image processing, data annotation, YOLO experiments and video processing. This repository contains selected standalone computer vision examples, including a frame extraction utility adapted from my original project archive.

**Technologies:** Python · OpenCV · YOLO · CVAT · Raspberry Pi

## Projects

| Project | Description |
| --- | --- |
| [Canny Edge Detection](examples/image_processing/edge_detection.py) | Extracts edges from local images using OpenCV. |
| [Video Frame Extraction](examples/video_processing/extract_frames.py) | Converts local MP4 videos into sampled JPEG frames. |
| [Software Tests](tests/test_examples.py) | Functional checks using synthetic images and video. |

## Visual Demo

![Actual Canny output on a synthetic square](assets/canny-demo.svg)

Synthetic test: 188 edge pixels from a 96 × 96 input, using OpenCV 4.13.0. This is a portfolio demonstration, not a competition result.

<details>
<summary>Additional reference image</summary>

![External edge detection example](https://upload.wikimedia.org/wikipedia/commons/9/93/Valve_monochrome_canny_%286%29.PNG)

External example by [Simpsons contributor](https://commons.wikimedia.org/wiki/File:Valve_monochrome_canny_(6).PNG), Wikimedia Commons, [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). Unmodified; not my own experimental output.

</details>

## Quick Start

```bash
python -m pip install -r requirements.txt
python examples/image_processing/edge_detection.py path/to/image.jpg
python examples/video_processing/extract_frames.py ./videos ./frames
python -m unittest discover -s tests -v
```

## Project Status

- [x] Independent image and video processing examples
- [x] Dependencies, test scripts and visual demonstration
- [ ] Original project photographs and verified model evaluation results

The original archive contains annotations, model files and technical documents. Full competition datasets and checkpoints are not included in this public repository. Verified training metrics and original project photographs were not available in the supplied archive.

## References

- Original source: my TEKNOFEST 2026 project archive — `scripts/extract_frames.py` (adapted for portable use).
- [OpenCV — Canny Edge Detection](https://docs.opencv.org/4.8.0/da/d22/tutorial_py_canny.html)
- [Ultralytics documentation](https://docs.ultralytics.com/)
- [NumPy documentation](https://numpy.org/doc/)
