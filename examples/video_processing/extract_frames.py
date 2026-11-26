"""Extract JPEG frames from local MP4 videos.

Adapted from the author's original extract_frames.py; paths and sampling
interval are now command-line arguments rather than machine-specific values.
"""
import argparse
from pathlib import Path

import cv2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video_folder", type=Path)
    parser.add_argument("output_folder", type=Path)
    parser.add_argument("--interval", type=float, default=0.08,
                        help="Sampling interval in seconds")
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval must be positive")
    if not args.video_folder.is_dir():
        parser.error("video_folder must be an existing directory")
    args.output_folder.mkdir(parents=True, exist_ok=True)
    counter = 0
    for video in sorted(args.video_folder.iterdir()):
        if video.suffix.lower() != ".mp4" or not video.is_file():
            continue
        cap = cv2.VideoCapture(str(video))
        if not cap.isOpened():
            print(f"Could not open: {video.name}")
            cap.release()
            continue
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            if not fps > 0:
                fps = 30
            frame_skip = max(1, int(fps * args.interval))
            frame_id = 0
            saved = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_id += 1
                if frame_id % frame_skip:
                    continue
                output = args.output_folder / f"frame_{counter:06d}.jpg"
                if output.exists():
                    raise FileExistsError(f"Output already exists: {output}")
                if not cv2.imwrite(str(output), frame):
                    raise OSError(f"Could not write: {output}")
                counter += 1
                saved += 1
            print(f"{video.name}: {saved} frames")
        finally:
            cap.release()
    print(f"Total saved frames: {counter}")


if __name__ == "__main__":
    main()
