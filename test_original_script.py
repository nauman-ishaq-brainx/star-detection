#!/usr/bin/env python3
"""
Test the original recognize_fish.py script directly
"""
import subprocess
import os
from dotenv import load_dotenv

def test_original_script():
    """Test the original recognize_fish.py script"""
    
    print("Testing Original recognize_fish.py Script")
    print("=" * 40)
    
    # Load environment variables
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
    
    # Test with your image
    test_image = "ç.jpg"
    
    if not os.path.exists(test_image):
        print(f"❌ ERROR: Test image {test_image} not found")
        return
    
    print(f"Testing with image: {test_image}")
    
    # Run the original script
    cmd = [
        'python3', 'recognize_fish.py',
        '-k', api_key,
        '-s', secret_key,
        test_image
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        print(f"Return code: {result.returncode}")
        print()
        print("STDOUT:")
        print(result.stdout)
        print()
        print("STDERR:")
        print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Script ran successfully!")
        else:
            print("❌ Script failed!")
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out!")
    except Exception as e:
        print(f"❌ Error running script: {e}")

if __name__ == "__main__":
    test_original_script()
