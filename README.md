# Computer Vision Portfolio

**Azat Oral | Mechatronics Engineering | İzmir Kâtip Çelebi University**

A collection of practical computer vision work focused on Python, OpenCV, image processing, offline video processing, and reproducible engineering experiments.

## Projects

| Project | Technical focus | Status |
| --- | --- | --- |
| [Canny edge detection](examples/image_processing/edge_detection.py) | Grayscale conversion, Gaussian smoothing and edge extraction | Smoke tested |
| [Offline video frame extraction](examples/video_processing/extract_frames.py) | MP4 decoding, temporal sampling and JPEG export | Smoke tested |
| TEKNOFEST 2026 — computer vision experience | Image acquisition, annotation workflows, object detection research and experimental evaluation | Project experience documented; selected independent code available |

## TEKNOFEST 2026 — Project Background

I contributed to computer vision development as part of a student engineering team participating in TEKNOFEST 2026. My work involved Python-based image processing, data preparation and experiments with YOLO-family object detection models. The experience strengthened my understanding of practical visual data workflows and the challenges of integrating computer vision into a larger engineering project.

The original project archive contains Python scripts, annotation files, YAML configuration files, model files and technical documents. The public repository presents a standalone offline video processing utility derived from that archive, rather than the complete competition system.

The archive includes files named `yolov8n.pt`, `yolo11n.pt` and `yolo26n.pt`. Their exact checkpoint provenance and training status have not been verified. The supplied archive does not contain image or video samples or verified training-performance plots. Accordingly, this portfolio does not claim that a complete dataset, trained custom model or reproducible model benchmark is included.

## Repository Structure

```text
Computer-Vision-Portfolio/
├── README.md
├── requirements.txt
├── examples/
│   ├── image_processing/
│   │   └── edge_detection.py
│   └── video_processing/
│       └── extract_frames.py
└── tests/
    └── test_examples.py
```

## Getting Started

Python 3.13.5 was used for the latest smoke tests.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The desktop image example requires an OpenCV-compatible graphical environment. The automated tests do not open GUI windows.

### 1. Image Processing — Canny Edge Detection

```bash
python examples/image_processing/edge_detection.py path/to/image.jpg
```

The implementation converts a local image to grayscale, applies Gaussian smoothing and produces a binary edge map using the Canny algorithm. The original image and the edge map are displayed in separate windows.

### 2. Offline Video Processing — Frame Extraction

```bash
python examples/video_processing/extract_frames.py ./videos ./frames
```

The utility reads local MP4 files and exports sampled frames as sequentially named JPEG files. The original competition archive's frame extraction script was adapted to accept portable command-line paths instead of machine-specific directories. Existing output files are protected against accidental overwriting.

## Verification and Testing

```bash
python -m unittest discover -s tests -v
```

| Test | Input | Verified result |
| --- | --- | --- |
| Canny smoke test | Synthetic 96 × 96 grayscale-compatible square image | Non-empty binary edge map with expected dimensions |
| Frame extraction smoke test | Synthetic 20-frame, 25 FPS MP4 video | Four readable 64 × 64 JPEG frames at a 0.2-second sampling interval |

Both tests passed locally with Python 3.13.5, OpenCV 4.13.0 and NumPy 2.3.5. These are functional software checks, not object detection accuracy or field-performance benchmarks.

## Engineering Skills

- Python and OpenCV
- Classical image preprocessing
- Video decoding and offline frame sampling
- Visual data organization and annotation workflows
- Object detection research with YOLO-family models
- Reproducible testing and technical documentation

## Development Checklist

- [x] Publish standalone image processing example.
- [x] Adapt and publish the archive-derived offline frame extraction utility.
- [x] Document dependencies and usage.
- [x] Verify both examples with synthetic-media smoke tests.
- [ ] Add independently shareable example photographs and output visualizations.
- [ ] Document verified model-evaluation results when suitable supporting records are available.

## References and Source Attribution

- **Original project source:** Azat Oral's 2026 TEKNOFEST computer vision project archive, specifically the original `scripts/extract_frames.py` utility. The public version includes portability and error-handling adaptations.
- [OpenCV documentation](https://docs.opencv.org/) — image processing and video I/O.
- [NumPy documentation](https://numpy.org/doc/) — numerical arrays and synthetic test data.
- [Ultralytics documentation](https://docs.ultralytics.com/) — background reference for YOLO-family object detection research; Ultralytics is not required to execute the published examples.
- [Python unittest documentation](https://docs.python.org/3/library/unittest.html) — automated functional tests.

The original competition materials and the public examples are distinct. The tests were added during portfolio preparation; they are not historical competition results.
