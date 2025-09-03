from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import os
import tempfile
import base64
from PIL import Image
import io
from finaly import FishDetector, detect_stars, calculate_fish_lengths, draw_boxes

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the fish detector once
fish_detector = FishDetector("model.ts")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Star Detection API is running"})

@app.route('/detect', methods=['POST'])
def detect_objects():
    """
    Main endpoint for object detection
    Accepts: multipart/form-data with 'image' field
    Returns: JSON with detection results and base64 encoded processed image
    """
    try:
        # Check if image is provided
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No image selected"}), 400
        
        # Read and process the image
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({"error": "Could not decode image"}), 400
        
        # Detect fish
        fish_boxes = fish_detector.detect_fish(image)
        
        # Detect stars
        star_boxes = detect_stars(image, "epoch162.pt")
        
        # Calculate fish lengths
        fish_lengths, pixels_per_inch = calculate_fish_lengths(fish_boxes, star_boxes)
        
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
        
        # Convert result image to base64
        _, buffer = cv2.imencode('.jpg', result_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Prepare response data
        response_data = {
            "success": True,
            "detections": {
                "fish_count": len(fish_boxes),
                "star_count": len(star_boxes),
                "pixels_per_inch": float(pixels_per_inch) if pixels_per_inch else None,
                "fish_details": []
            },
            "processed_image": img_base64,
            "image_format": "jpg"
        }
        
        # Add fish details
        for i, fish in enumerate(fish_lengths):
            response_data["detections"]["fish_details"].append({
                "fish_id": i + 1,
                "box": {
                    "x1": int(fish['box'][0]),
                    "y1": int(fish['box'][1]),
                    "x2": int(fish['box'][2]),
                    "y2": int(fish['box'][3])
                },
                "dimensions_px": {
                    "width": int(fish['width_px']),
                    "height": int(fish['height_px'])
                },
                "length_inch": float(fish['length_inch'])
            })
        
        # Add star details
        response_data["detections"]["star_details"] = []
        for i, star in enumerate(star_boxes):
            x1, y1, x2, y2 = star['box']
            response_data["detections"]["star_details"].append({
                "star_id": i + 1,
                "box": {
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2)
                },
                "confidence": float(star['conf']),
                "dimensions_px": {
                    "width": int(x2 - x1),
                    "height": int(y2 - y1)
                }
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/detect_base64', methods=['POST'])
def detect_objects_base64():
    """
    Alternative endpoint that accepts base64 encoded images
    Accepts: JSON with 'image' field containing base64 string
    Returns: JSON with detection results and base64 encoded processed image
    """
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        # Decode base64 image
        image_data = data['image']
        if image_data.startswith('data:image'):
            # Remove data URL prefix if present
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({"error": "Could not decode base64 image"}), 400
        
        # Process image (same logic as above)
        fish_boxes = fish_detector.detect_fish(image)
        star_boxes = detect_stars(image, "epoch162.pt")
        fish_lengths, pixels_per_inch = calculate_fish_lengths(fish_boxes, star_boxes)
        
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
        
        # Convert result image to base64
        _, buffer = cv2.imencode('.jpg', result_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Prepare response data (same as above)
        response_data = {
            "success": True,
            "detections": {
                "fish_count": len(fish_boxes),
                "star_count": len(star_boxes),
                "pixels_per_inch": float(pixels_per_inch) if pixels_per_inch else None,
                "fish_details": []
            },
            "processed_image": img_base64,
            "image_format": "jpg"
        }
        
        # Add fish details
        for i, fish in enumerate(fish_lengths):
            response_data["detections"]["fish_details"].append({
                "fish_id": i + 1,
                "box": {
                    "x1": int(fish['box'][0]),
                    "y1": int(fish['box'][1]),
                    "x2": int(fish['box'][2]),
                    "y2": int(fish['box'][3])
                },
                "dimensions_px": {
                    "width": int(fish['width_px']),
                    "height": int(fish['height_px'])
                },
                "length_inch": float(fish['length_inch'])
            })
        
        # Add star details
        response_data["detections"]["star_details"] = []
        for i, star in enumerate(star_boxes):
            x1, y1, x2, y2 = star['box']
            response_data["detections"]["star_details"].append({
                "star_id": i + 1,
                "box": {
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2)
                },
                "confidence": float(star['conf']),
                "dimensions_px": {
                    "width": int(x2 - x1),
                    "height": int(y2 - y1)
                }
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    print("Starting Star Detection API...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /detect - Upload image file (multipart/form-data)")
    print("  POST /detect_base64 - Send base64 encoded image (JSON)")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
