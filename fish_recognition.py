#!/usr/bin/env python3
"""
Fish Recognition Integration Module
Integrates with the Fishial API to recognize fish species
"""
import os
import sys
import json
import requests
import hashlib
import base64
import mimetypes
import urllib3
import logging
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Disable warnings about insecure HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)

class FishRecognition:
    def __init__(self):
        self.api_key = os.getenv('FISHIAL_API_KEY')
        self.secret_key = os.getenv('FISHIAL_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("FISHIAL_API_KEY and FISHIAL_SECRET_KEY must be set in config.env")
    
    def get_file_metadata(self, image_data, filename="fish.jpg"):
        """
        Compute file metadata from image data
        """
        mime = "image/jpeg"  # Default to JPEG
        size = len(image_data)
        hasher = hashlib.md5()
        hasher.update(image_data)
        checksum = base64.b64encode(hasher.digest()).decode("utf-8")
        return filename, mime, size, checksum
    
    def recognize_fish_species(self, image_data, filename="fish.jpg"):
        """
        Recognize fish species from image data
        Returns list of fish species with accuracy scores
        """
        try:
            # Get file metadata
            name, mime, size, checksum = self.get_file_metadata(image_data, filename)
            
            # Step 1: Obtain auth token
            auth_url = "https://api-users.fishial.ai/v1/auth/token"
            auth_payload = {"client_id": self.api_key, "client_secret": self.secret_key}
            
            auth_response = requests.post(
                auth_url,
                json=auth_payload,
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            auth_response.raise_for_status()
            auth_data = auth_response.json()
            auth_token = auth_data.get("access_token")
            
            if not auth_token:
                raise Exception("Failed to obtain access token")
            
            auth_header = {"Authorization": f"Bearer {auth_token}"}
            
            # Step 2: Obtain upload URL
            upload_url_api = "https://api.fishial.ai/v1/recognition/upload"
            upload_payload = {
                "blob": {
                    "filename": name,
                    "content_type": mime,
                    "byte_size": size,
                    "checksum": checksum,
                }
            }
            headers = auth_header.copy()
            headers.update({"Content-Type": "application/json", "Accept": "application/json"})
            
            upload_response = requests.post(
                upload_url_api, json=upload_payload, headers=headers, verify=False
            )
            upload_response.raise_for_status()
            upload_data = upload_response.json()
            
            signed_id = upload_data.get("signed-id")
            direct_upload = upload_data.get("direct-upload", {})
            direct_upload_url = direct_upload.get("url")
            direct_upload_headers = direct_upload.get("headers", {})
            content_disposition = direct_upload_headers.get("Content-Disposition")
            
            if not (signed_id and direct_upload_url and content_disposition):
                raise Exception("Missing upload information in response")
            
            # Step 3: Upload file
            put_headers = {
                "Content-Disposition": content_disposition,
                "Content-Md5": checksum,
                "Content-Type": "",
            }
            
            upload_response = requests.put(
                direct_upload_url, data=image_data, headers=put_headers, verify=False
            )
            upload_response.raise_for_status()
            
            # Step 4: Run recognition
            recognition_url = f"https://api.fishial.ai/v1/recognition/image?q={signed_id}"
            recognition_response = requests.get(recognition_url, headers=auth_header, verify=False)
            recognition_response.raise_for_status()
            recognition_data = recognition_response.json()
            
            # Extract results
            results = recognition_data.get("results", [])
            fish_species = []
            
            for fish in results:
                species_list = fish.get("species", [])
                for species in species_list:
                    species_name = species.get("name", "Unknown")
                    accuracy = species.get("accuracy", 0)
                    fish_species.append({
                        "name": species_name,
                        "accuracy": accuracy
                    })
            
            return fish_species
            
        except Exception as e:
            logging.error(f"Error in fish recognition: {e}")
            return []

def recognize_fish_from_image(image_data, filename="fish.jpg"):
    """
    Convenience function to recognize fish species from image data
    """
    try:
        recognizer = FishRecognition()
        return recognizer.recognize_fish_species(image_data, filename)
    except Exception as e:
        logging.error(f"Failed to initialize fish recognition: {e}")
        return []
