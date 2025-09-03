# Star Detection API

This API provides endpoints for detecting fish and stars in images using your trained YOLO models. It wraps your existing `finaly.py` functionality into a web service that can be accessed via HTTP requests.

## Features

- **Fish Detection**: Uses your `model.ts` TorchScript model
- **Star Detection**: Uses your `epoch162.pt` YOLO model
- **Length Calculation**: Calculates fish lengths using star references for scale
- **Image Processing**: Returns processed images with bounding boxes and measurements
- **Multiple Input Formats**: Supports both file uploads and base64 encoded images

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the required model files in your directory:
   - `model.ts` (fish detection model)
   - `epoch162.pt` (star detection model)

## Running the API

Start the Flask server:
```bash
python api.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Health Check
- **URL**: `GET /health`
- **Description**: Check if the API is running
- **Response**: JSON with status information

### 2. File Upload Detection
- **URL**: `POST /detect`
- **Description**: Upload an image file for processing
- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `image`: Image file (jpg, png, etc.)
- **Response**: JSON with detection results and base64 encoded processed image

### 3. Base64 Image Detection
- **URL**: `POST /detect_base64`
- **Description**: Send a base64 encoded image for processing
- **Content-Type**: `application/json`
- **Parameters**:
  - `image`: Base64 encoded image string
- **Response**: JSON with detection results and base64 encoded processed image

## Response Format

All endpoints return JSON responses with the following structure:

```json
{
  "success": true,
  "detections": {
    "fish_count": 2,
    "star_count": 1,
    "pixels_per_inch": 45.67,
    "fish_details": [
      {
        "fish_id": 1,
        "box": {"x1": 100, "y1": 150, "x2": 300, "y2": 250},
        "dimensions_px": {"width": 200, "height": 100},
        "length_inch": 4.38
      }
    ],
    "star_details": [
      {
        "star_id": 1,
        "box": {"x1": 50, "y1": 50, "x2": 100, "y2": 100},
        "confidence": 0.95,
        "dimensions_px": {"width": 50, "height": 50}
      }
    ]
  },
  "processed_image": "base64_encoded_image_string",
  "image_format": "jpg"
}
```

## Usage Examples

### Using cURL

**File Upload:**
```bash
curl -X POST -F "image=@4104.jpg" http://localhost:5000/detect
```

**Base64 Upload:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"image":"base64_string_here"}' \
  http://localhost:5000/detect_base64
```

### Using Python

**File Upload:**
```python
import requests

with open('4104.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/detect', files=files)

data = response.json()
print(f"Fish detected: {data['detections']['fish_count']}")
```

**Base64 Upload:**
```python
import requests
import base64

with open('4104.jpg', 'rb') as f:
    image_data = f.read()
    base64_data = base64.b64encode(image_data).decode('utf-8')

payload = {'image': base64_data}
response = requests.post('http://localhost:5000/detect_base64', json=payload)

data = response.json()
print(f"Fish detected: {data['detections']['fish_count']}")
```

### Using JavaScript/Fetch

**File Upload:**
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:5000/detect', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log(`Fish detected: ${data.detections.fish_count}`);
    
    // Display the processed image
    const img = document.createElement('img');
    img.src = 'data:image/jpeg;base64,' + data.processed_image;
    document.body.appendChild(img);
});
```

**Base64 Upload:**
```javascript
// Assuming you have a base64 string
const payload = {
    image: base64String
};

fetch('http://localhost:5000/detect_base64', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
})
.then(response => response.json())
.then(data => {
    console.log(`Fish detected: ${data.detections.fish_count}`);
});
```

## Testing

Use the provided test client to verify the API functionality:

```bash
python test_client.py
```

This will test both endpoints with a sample image and save the results.

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200`: Success
- `400`: Bad request (missing image, invalid format)
- `500`: Internal server error (processing failed)

## CORS Support

CORS is enabled for all routes, allowing cross-origin requests from web applications.

## Notes

- The API processes images in memory and returns base64 encoded results
- Large images may take longer to process
- The fish detector is initialized once when the server starts for better performance
- All measurements are calculated using the star reference for scale calibration

## Troubleshooting

1. **Model files not found**: Ensure `model.ts` and `epoch162.pt` are in the same directory as `api.py`
2. **Import errors**: Make sure all dependencies are installed from `requirements.txt`
3. **Port already in use**: Change the port in `api.py` or stop other services using port 5000
4. **Memory issues**: Large images may cause memory problems; consider resizing images before upload
