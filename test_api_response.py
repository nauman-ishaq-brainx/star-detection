#!/usr/bin/env python3
"""
Test API response to see what's being returned
"""
import requests
import json

def test_api_response():
    """Test the API and see the actual response"""
    
    print("Testing API Response...")
    print("=" * 40)
    
    # Test with a sample image
    test_image = "ç.jpg"  # Change this to your test image
    
    try:
        print(f"Testing with image: {test_image}")
        
        # Make API request
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post('http://localhost:5000/fish-length', files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2))
            
            # Check specific fields
            print("\n" + "="*40)
            print("Response Analysis:")
            print(f"Success: {data.get('success')}")
            print(f"Fish Count: {data.get('fish_count')}")
            print(f"Fish Lengths: {data.get('fish_lengths')}")
            print(f"Fish Species: {data.get('fish_species')}")
            
            if data.get('fish_species'):
                print("✅ Fish species found!")
                for i, species in enumerate(data['fish_species']):
                    print(f"  {i+1}. {species}")
            else:
                print("❌ No fish species in response")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error message: {response.text}")
            
    except FileNotFoundError:
        print(f"❌ ERROR: Test image {test_image} not found")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API. Make sure the server is running:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_api_response()
