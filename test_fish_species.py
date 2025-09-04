#!/usr/bin/env python3
"""
Test script for fish species recognition
"""
import requests
import base64

def test_fish_species_api():
    """Test the fish species recognition API"""
    
    # API base URL
    BASE_URL = "http://localhost:5000"
    
    print("Testing Fish Species Recognition API...")
    print("=" * 50)
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test file upload
    print("2. Testing file upload with species recognition...")
    test_image = "4104.jpg"  # Change this to your test image
    
    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{BASE_URL}/fish-length", files=files)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Fish detected: {data['fish_count']}")
            print(f"   Fish lengths: {data['fish_lengths']}")
            print(f"   Fish species: {data['fish_species']}")
        else:
            print(f"   Error: {response.text}")
    except FileNotFoundError:
        print(f"   Error: Test image {test_image} not found")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test base64 upload
    print("3. Testing base64 upload with species recognition...")
    try:
        with open(test_image, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        
        payload = {'image': base64_data}
        response = requests.post(f"{BASE_URL}/fish-length-base64", json=payload)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Fish detected: {data['fish_count']}")
            print(f"   Fish lengths: {data['fish_lengths']}")
            print(f"   Fish species: {data['fish_species']}")
        else:
            print(f"   Error: {response.text}")
    except FileNotFoundError:
        print(f"   Error: Test image {test_image} not found")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_fish_species_api()
