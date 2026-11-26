"""Smoke tests using only synthetic geometric images and video."""
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def test_canny(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "square.png"
            image = np.zeros((96, 96, 3), dtype=np.uint8)
            image[24:72, 24:72] = 255
            self.assertTrue(cv2.imwrite(str(path), image))
            script = ROOT / "examples/image_processing/edge_detection.py"
            with patch.object(sys, "argv", [str(script), str(path)]), \
                    patch.object(cv2, "imshow") as show, \
                    patch.object(cv2, "waitKey", return_value=0), \
                    patch.object(cv2, "destroyAllWindows"):
                runpy.run_path(str(script), run_name="__main__")
            edges = show.call_args_list[1].args[1]
            self.assertEqual(edges.shape, (96, 96))
            self.assertGreater(np.count_nonzero(edges), 0)
            self.assertTrue(set(np.unique(edges)).issubset({0, 255}))

    def test_frame_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            videos = folder / "videos"
            videos.mkdir()
            frames = folder / "frames"
            writer = cv2.VideoWriter(str(videos / "sample.mp4"),
                                     cv2.VideoWriter_fourcc(*"mp4v"),
                                     25, (64, 64))
            self.assertTrue(writer.isOpened(), "MP4 encoder is unavailable")
            try:
                for i in range(20):
                    writer.write(np.full((64, 64, 3), i * 10, dtype=np.uint8))
            finally:
                writer.release()
            subprocess.run([sys.executable,
                            str(ROOT / "examples/video_processing/extract_frames.py"),
                            str(videos), str(frames), "--interval", "0.2"], check=True)
            outputs = sorted(frames.glob("*.jpg"))
            self.assertEqual(len(outputs), 4)
            for output in outputs:
                self.assertEqual(cv2.imread(str(output)).shape, (64, 64, 3))


if __name__ == "__main__":
    unittest.main()
