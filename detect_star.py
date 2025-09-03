import cv2
from ultralytics import YOLO
print('hello')

# Load your trained model
model = YOLO("epoch162.pt")

# Input image
image_path = "4103.jpg"  # change this if needed
results = model(image_path)

# Draw results on the image
for result in results:
    boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
    confs = result.boxes.conf.cpu().numpy()  # confidence scores
    clss = result.boxes.cls.cpu().numpy()    # class IDs

    img = cv2.imread(image_path)

    for (box, conf, cls) in zip(boxes, confs, clss):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(img, f"star {conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Save output
    cv2.imwrite("output.jpg", img)

print("✅ Detection done. See output.jpg")
