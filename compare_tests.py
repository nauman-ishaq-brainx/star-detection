#!/usr/bin/env python3
"""
Compare direct fish recognition vs API call
"""
import requests
from fish_recognition import recognize_fish_from_image

def test_direct_vs_api():
    """Compare direct fish recognition with API call"""
    
    print("Comparing Direct Fish Recognition vs API Call")
    print("=" * 50)
    
    test_image = "ç.jpg"  # Your test image
    
    # Test 1: Direct fish recognition
    print("1. Testing DIRECT fish recognition...")
    try:
        with open(test_image, 'rb') as f:
            image_data = f.read()
        
        species_direct = recognize_fish_from_image(image_data, test_image)
        print(f"   Direct result: {species_direct}")
        
        if species_direct:
            print("   ✅ Direct recognition found species:")
            for i, fish in enumerate(species_direct):
                print(f"     {i+1}. {fish['name']} (accuracy: {fish['accuracy']})")
        else:
            print("   ❌ Direct recognition found no species")
            
    except Exception as e:
        print(f"   ❌ Direct recognition error: {e}")
    
    print()
    
    # Test 2: API call
    print("2. Testing API call...")
    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post('http://localhost:5000/fish-length', files=files)
        
        if response.status_code == 200:
            data = response.json()
            species_api = data.get('fish_species', [])
            print(f"   API result: {species_api}")
            
            if species_api:
                print("   ✅ API found species:")
                for i, fish in enumerate(species_api):
                    print(f"     {i+1}. {fish['name']} (accuracy: {fish['accuracy']})")
            else:
                print("   ❌ API found no species")
                
            print(f"   Full API response: {data}")
        else:
            print(f"   ❌ API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ API call error: {e}")
    
    print()
    
    # Compare results
    print("3. Comparison:")
    if species_direct and species_api:
        print("   ✅ Both methods found species")
        print(f"   Direct: {len(species_direct)} species")
        print(f"   API: {len(species_api)} species")
    elif species_direct and not species_api:
        print("   ❌ Direct works but API doesn't - there's a bug in the API")
    elif not species_direct and species_api:
        print("   ❌ API works but direct doesn't - unexpected")
    else:
        print("   ❌ Neither method found species")

if __name__ == "__main__":
    test_direct_vs_api()
