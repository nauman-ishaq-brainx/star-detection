import cv2
from inference import YOLOInference

class FishDetector:
    def __init__(self, model_path="model.ts"):
        """
        Initialize the fish detector with YOLO model.
        """
        self.yolo_inference = YOLOInference(model_path, yolo_ver='v10')

    def detect_fish(self, image):
        """
        Detect fish in the image using YOLO model.

        Args:
            image (numpy.ndarray): Input image in BGR format

        Returns:
            list: List of fish bounding boxes as (x1, y1, x2, y2)
        """
        try:
            results = self.yolo_inference.predict(image)
            fish_boxes = []

            if results and results[0]:
                for result in results[0]:
                    # Take all detected objects as fish (or filter by class if needed)
                    fish_boxes.append(result.get_box())

            return fish_boxes

        except Exception as e:
            print(f"Error in fish detection: {e}")
            return []

    def draw_fish_boxes(self, image, fish_boxes):
        """
        Draw bounding boxes around detected fish.

        Args:
            image (numpy.ndarray): Input image
            fish_boxes (list): List of bounding boxes

        Returns:
            numpy.ndarray: Image with bounding boxes drawn
        """
        result_image = image.copy()
        for i, box in enumerate(fish_boxes):
            x1, y1, x2, y2 = box
            cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(result_image, f"Fish {i+1}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return result_image


def main():
    detector = FishDetector("model.ts")
    image_path = "3604.jpg"
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not load image: {image_path}")
        return

    fish_boxes = detector.detect_fish(image)
    print(f"Detected {len(fish_boxes)} fish")
    for i, box in enumerate(fish_boxes):
        print(f"Fish {i+1}: Bounding box = {box}")

    result_image = detector.draw_fish_boxes(image, fish_boxes)
    cv2.imwrite("fish_boxes_result.jpg", result_image)
    print("Result saved to fish_boxes_result.jpg")


if __name__ == "__main__":
    main()
