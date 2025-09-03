import cv2
from inference import YOLOInference
from ultralytics import YOLO

# ----- Fish Detector -----
class FishDetector:
    def __init__(self, model_path="model.ts"):
        self.yolo_inference = YOLOInference(model_path, yolo_ver='v10')

    def detect_fish(self, image):
        try:
            results = self.yolo_inference.predict(image)
            fish_boxes = []
            if results and results[0]:
                for result in results[0]:
                    fish_boxes.append(result.get_box())
            return fish_boxes
        except Exception as e:
            print(f"Error in fish detection: {e}")
            return []

# ----- Star Detection -----
def detect_stars(image, model_path="epoch162.pt"):
    model = YOLO(model_path)
    results = model(image)
    
    star_boxes = []
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()
        for box, conf in zip(boxes, confs):
            x1, y1, x2, y2 = map(int, box)
            star_boxes.append({'box': (x1, y1, x2, y2), 'conf': float(conf)})
    return star_boxes

# ----- Draw boxes and add info -----
def draw_boxes(image, fish_boxes, star_boxes, pixels_per_inch=None, fish_lengths=None):
    result_image = image.copy()
    
    # Draw fish boxes
    for i, box in enumerate(fish_boxes):
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        length_in = fish_lengths[i]['length_inch'] if fish_lengths else 0
        cv2.putText(result_image, f"Fish {i+1}: {width}px x {height}px, {length_in:.2f}\"",
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw star boxes
    for i, star in enumerate(star_boxes):
        x1, y1, x2, y2 = star['box']
        width = x2 - x1
        height = y2 - y1
        cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        if pixels_per_inch:
            cv2.putText(result_image, f"Star {i+1}: {width}px x {height}px, PPI={pixels_per_inch:.2f}",
                        (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        else:
            cv2.putText(result_image, f"Star {i+1}: {width}px x {height}px",
                        (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    return result_image

# ----- Calculate fish lengths -----
def calculate_fish_lengths(fish_boxes, star_boxes, star_real_width=1.6):
    if not star_boxes:
        print("No stars detected for scale reference")
        return [], None

    # Use the star with highest confidence
    best_star = max(star_boxes, key=lambda x: x['conf'])
    x1, y1, x2, y2 = best_star['box']
    star_pixel_width = x2 - x1
    pixels_per_inch = star_pixel_width / star_real_width
    print(f"Using star width {star_real_width}\" -> pixels_per_inch = {pixels_per_inch:.2f}")

    fish_lengths = []
    for box in fish_boxes:
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        fish_length_px = max(width, height)
        fish_length_in = fish_length_px / pixels_per_inch
        fish_lengths.append({'box': box, 'length_inch': fish_length_in, 'width_px': width, 'height_px': height})
    
    return fish_lengths, pixels_per_inch

# ----- Main function -----
def main():
    image_path = "4104.jpg"
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not load image: {image_path}")
        return

    # Detect fish
    fish_detector = FishDetector("model.ts")
    fish_boxes = fish_detector.detect_fish(image)
    print(f"Detected {len(fish_boxes)} fish")

    # Detect stars
    star_boxes = detect_stars(image, "epoch162.pt")
    print(f"Detected {len(star_boxes)} stars")

    # Calculate fish lengths
    fish_lengths, pixels_per_inch = calculate_fish_lengths(fish_boxes, star_boxes)
    for i, fish in enumerate(fish_lengths):
        print(f"Fish {i+1}: {fish['length_inch']:.2f}\" ({fish['width_px']}px x {fish['height_px']}px)")

    # Draw all boxes and info
    result_image = draw_boxes(image, fish_boxes, star_boxes, pixels_per_inch, fish_lengths)

    # Draw length lines for fish
    for fish in fish_lengths:
        x1, y1, x2, y2 = fish['box']
        if (x2 - x1) > (y2 - y1):
            start_point = (x1, (y1+y2)//2)
            end_point = (x2, (y1+y2)//2)
        else:
            start_point = ((x1+x2)//2, y1)
            end_point = ((x1+x2)//2, y2)
        cv2.line(result_image, start_point, end_point, (0, 255, 255), 2)
        cv2.putText(result_image, f"{fish['length_inch']:.2f}\"", 
                    (start_point[0], start_point[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255),2)

    # Save result
    cv2.imwrite("combined_result_with_info.jpg", result_image)
    print("Result saved to combined_result_with_info.jpg")

if __name__ == "__main__":
    main()
