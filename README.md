# Computer Vision Portfolio

**Python · OpenCV · Image Processing · Deep Learning**

A personal engineering portfolio featuring standalone computer vision examples and reflections on student engineering experience. The practical examples are intended for general-purpose civilian applications.

## Featured project

[**TEKNOFEST 2026 — Computer Vision Engineering Experience**](projects/teknofest_2026/README.md)

A retrospective covering CVAT annotation, data preparation, experimental engineering and multidisciplinary teamwork with the Saturn Rocket Team (MİMAS). The case study describes transferable skills and does not distribute operational project materials.

## Focus areas

- Image preprocessing and visualization
- Color-space transformations and segmentation
- Dataset preparation and model evaluation
- Graphical user interfaces for offline image analysis

## Project roadmap

| Area | Status |
| --- | --- |
| Classical image processing | Initial example available |
| Industrial visual inspection examples | Planned |
| Engineering experience case study | Available |

## About

Mechatronics Engineering student interested in robotics, computer vision and embedded systems.

**Status:** Portfolio under development. The Canny example was tested with OpenCV 4.6.0 on a 96 × 96 synthetic image containing a white square. It produced a binary edge map with 188 edge pixels. The test exercised image loading and processing with window display disabled.

## Getting started

The [Canny edge detection example](examples/image_processing/edge_detection.py) demonstrates grayscale conversion, Gaussian smoothing and edge detection on a local still image.

```bash
python -m pip install -r requirements.txt
python examples/image_processing/edge_detection.py path/to/image.jpg
```

A desktop environment is required to display the output windows.
