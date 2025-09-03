import requests
import base64
import json
from PIL import Image
import io

# API base URL
BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_file_upload(image_path):
    """Test file upload endpoint"""
    print(f"Testing file upload with {image_path}...")
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f"{BASE_URL}/detect", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Fish detected: {data['detections']['fish_count']}")
        print(f"Stars detected: {data['detections']['star_count']}")
        print(f"Pixels per inch: {data['detections']['pixels_per_inch']}")
        
        # Save the processed image
        img_data = base64.b64decode(data['processed_image'])
        with open(f"api_result_{image_path}", 'wb') as f:
            f.write(img_data)
        print(f"Processed image saved as: api_result_{image_path}")
        
        # Print fish details
        for fish in data['detections']['fish_details']:
            print(f"Fish {fish['fish_id']}: {fish['length_inch']:.2f}\"")
    else:
        print(f"Error: {response.text}")
    print()

def test_base64_upload(image_path):
    """Test base64 upload endpoint"""
    print(f"Testing base64 upload with {image_path}...")
    
    # Convert image to base64
    with open(image_path, 'rb') as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
    
    payload = {'image': base64_data}
    response = requests.post(f"{BASE_URL}/detect_base64", json=payload)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Fish detected: {data['detections']['fish_count']}")
        print(f"Stars detected: {data['detections']['star_count']}")
        print(f"Pixels per inch: {data['detections']['pixels_per_inch']}")
        
        # Save the processed image
        img_data = base64.b64decode(data['processed_image'])
        with open(f"api_result_base64_{image_path}", 'wb') as f:
            f.write(img_data)
        print(f"Processed image saved as: api_result_base64_{image_path}")
        
        # Print fish details
        for fish in data['detections']['fish_details']:
            print(f"Fish {fish['fish_id']}: {fish['length_inch']:.2f}\"")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Main test function"""
    print("Star Detection API Test Client")
    print("=" * 40)
    
    # Test health check
    test_health()
    
    # Test with an image from your directory
    test_image = "4104.jpg"  # You can change this to any image in your directory
    
    try:
        # Test file upload
        test_file_upload(test_image)
        
        # Test base64 upload
        test_base64_upload(test_image)
        
    except FileNotFoundError:
        print(f"Image file {test_image} not found. Please make sure the image exists in the current directory.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API. Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
