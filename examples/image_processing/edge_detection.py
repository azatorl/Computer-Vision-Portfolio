"""Standalone Canny edge detection example for local still images."""
import argparse
import cv2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="Input image path")
    args = parser.parse_args()

    image = cv2.imread(args.image)
    if image is None:
        raise FileNotFoundError(args.image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    cv2.imshow("Original Image", image)
    cv2.imshow("Edge Detection", edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
