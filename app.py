from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from finaly import FishDetector, detect_stars, calculate_fish_lengths
from fish_recognition import recognize_fish_from_image

app = Flask(__name__)

# Initialize the fish detector once
fish_detector = FishDetector("model.ts")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Fish Length Detection API is running"})

@app.route('/fish-length', methods=['POST'])
def get_fish_length():
    """
    Get fish lengths and species from uploaded image
    Returns: JSON with fish lengths array and species, or 0 if no fish detected
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
        
        # If no fish detected, return 0
        if not fish_boxes:
            return jsonify({
                "success": True,
                "fish_lengths": 0,
                "fish_count": 0,
                "fish_species": []
            })
        
        # Detect stars for scale reference
        star_boxes = detect_stars(image, "epoch162.pt")
        
        # Calculate fish lengths
        fish_lengths, pixels_per_inch = calculate_fish_lengths(fish_boxes, star_boxes)
        
        # Extract only the length values
        lengths = []
        if fish_lengths:
            for fish in fish_lengths:
                lengths.append(round(fish['length_inch'], 2))
        
        # Recognize fish species
        fish_species = recognize_fish_from_image(image_bytes, file.filename)
        
        # If no valid lengths calculated, return 0
        if not lengths:
            return jsonify({
                "success": True,
                "fish_lengths": 0,
                "fish_count": len(fish_boxes),
                "fish_species": fish_species
            })
        
        return jsonify({
            "success": True,
            "fish_lengths": lengths,
            "fish_count": len(lengths),
            "fish_species": fish_species
        })
        
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/fish-length-base64', methods=['POST'])
def get_fish_length_base64():
    """
    Get fish lengths and species from base64 encoded image
    Returns: JSON with fish lengths array and species, or 0 if no fish detected
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
        
        # Detect fish
        fish_boxes = fish_detector.detect_fish(image)
        
        # If no fish detected, return 0
        if not fish_boxes:
            return jsonify({
                "success": True,
                "fish_lengths": 0,
                "fish_count": 0,
                "fish_species": []
            })
        
        # Detect stars for scale reference
        star_boxes = detect_stars(image, "epoch162.pt")
        
        # Calculate fish lengths
        fish_lengths, pixels_per_inch = calculate_fish_lengths(fish_boxes, star_boxes)
        
        # Extract only the length values
        lengths = []
        if fish_lengths:
            for fish in fish_lengths:
                lengths.append(round(fish['length_inch'], 2))
        
        # Recognize fish species
        fish_species = recognize_fish_from_image(image_bytes, "fish.jpg")
        
        # If no valid lengths calculated, return 0
        if not lengths:
            return jsonify({
                "success": True,
                "fish_lengths": 0,
                "fish_count": len(fish_boxes),
                "fish_species": fish_species
            })
        
        return jsonify({
            "success": True,
            "fish_lengths": lengths,
            "fish_count": len(lengths),
            "fish_species": fish_species
        })
        
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting Fish Length & Species Detection API...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /fish-length - Upload image file (multipart/form-data)")
    print("  POST /fish-length-base64 - Send base64 encoded image (JSON)")
    print()
    print("Response format:")
    print("  - If fish detected: {'success': True, 'fish_lengths': [4.2, 3.8], 'fish_count': 2, 'fish_species': [{'name': 'Bass', 'accuracy': 0.95}]}")
    print("  - If no fish: {'success': True, 'fish_lengths': 0, 'fish_count': 0, 'fish_species': []}")
    print()
    print("Make sure to set your FISHIAL_API_KEY and FISHIAL_SECRET_KEY in config.env")
    
    app.run(host='0.0.0.0', port=5000, debug=True)