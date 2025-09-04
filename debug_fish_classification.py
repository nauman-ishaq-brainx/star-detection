#!/usr/bin/env python3
"""
Debug script to test fish classification functionality
"""
import os
import sys
from fish_recognition import recognize_fish_from_image

def test_fish_recognition():
    """Test fish recognition with a sample image"""
    
    print("Testing Fish Recognition...")
    print("=" * 40)
    
    # Check if credentials are set
    from dotenv import load_dotenv
    load_dotenv('config.env')
    
    api_key = os.getenv('FISHIAL_API_KEY')
    secret_key = os.getenv('FISHIAL_SECRET_KEY')
    
    print(f"API Key: {'SET' if api_key and api_key != 'YOUR_API_KEY' else 'NOT SET'}")
    print(f"Secret Key: {'SET' if secret_key and secret_key != 'YOUR_SECRET_API_KEY' else 'NOT SET'}")
    
    if not api_key or api_key == 'YOUR_API_KEY':
        print("❌ ERROR: Please set your FISHIAL_API_KEY in config.env")
        return
    
    if not secret_key or secret_key == 'YOUR_SECRET_API_KEY':
        print("❌ ERROR: Please set your FISHIAL_SECRET_KEY in config.env")
        return
    
    # Test with a sample image
    test_image = "4104.jpg"  # Change this to your test image
    
    if not os.path.exists(test_image):
        print(f"❌ ERROR: Test image {test_image} not found")
        print("Available images:")
        for file in os.listdir('.'):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"  - {file}")
        return
    
    print(f"Testing with image: {test_image}")
    
    try:
        # Read image
        with open(test_image, 'rb') as f:
            image_data = f.read()
        
        print(f"Image size: {len(image_data)} bytes")
        
        # Test fish recognition
        print("Calling fish recognition...")
        species = recognize_fish_from_image(image_data, test_image)
        
        print(f"Recognition result: {species}")
        
        if species:
            print("✅ Fish species detected:")
            for i, fish in enumerate(species):
                print(f"  {i+1}. {fish['name']} (accuracy: {fish['accuracy']})")
        else:
            print("❌ No fish species detected")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fish_recognition()
