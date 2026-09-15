import requests, json, os, cv2, numpy as np, sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = 'http://127.0.0.1:8000'
API_URL = f'{BASE_URL}/api/analyze/'

print('=======================================================')
print('1. REAL END-TO-END TEST: VALID IMAGE WITH Rs. 10 COIN')
print('=======================================================')
valid_img_path = 'media/uploads/test_valid_10.png'
with open(valid_img_path, 'rb') as f:
    resp = requests.post(API_URL, files={'image': ('test_valid_10.png', f, 'image/png')})

print(f'HTTP STATUS: {resp.status_code}')
try:
    data = resp.json()
    print('RESPONSE JSON:')
    print(json.dumps(data, indent=2))
except Exception as e:
    print('Failed to parse JSON:', e, resp.text)
    data = {}

# Verifications
assert resp.status_code == 200, f'Expected 200, got {resp.status_code}'
assert data.get('success') is True, 'Expected success: True'
assert data.get('coin_detected') is True, 'Expected coin_detected: True'
assert 'landmark_count' in data, 'Missing landmark_count'
assert 'processed_image_url' in data, 'Missing processed_image_url'
assert isinstance(data.get('measurements'), list), 'Missing measurements list'
assert len(data['measurements']) > 0, 'Measurements list is empty'

for i, m in enumerate(data['measurements']):
    for field in ['finger', 'recommended_size', 'width_mm', 'height_mm', 'raw_width', 'raw_height']:
        assert field in m, f'Measurement {i} missing field {field}'

print('\n-> All JSON fields verified successfully!')

print('\n=======================================================')
print('2. VERIFY PROCESSED IMAGE URL ACCESSIBILITY & VISUALS')
print('=======================================================')
proc_url = data['processed_image_url']
print(f'Fetching: {proc_url}')
img_resp = requests.get(proc_url)
print(f'Processed Image HTTP Status: {img_resp.status_code}')
assert img_resp.status_code == 200, 'Processed image URL not accessible'
assert len(img_resp.content) > 1000, 'Processed image content empty'

# Decode image to inspect annotations
img_array = np.frombuffer(img_resp.content, np.uint8)
img = cv2.imdecode(img_array, cv2.IMREAD_COLOR) # BGR
h, w, c = img.shape
print(f'Processed image decoded: {w}x{h}, {c} channels')

# Check for blue pixels (Rs. 10 coin outline in BGR: high B, low G, low R)
blue_mask = (img[:, :, 0] > 180) & (img[:, :, 1] < 80) & (img[:, :, 2] < 80)
blue_pixels = np.sum(blue_mask)
print(f'Blue coin circle/label pixels: {blue_pixels}')
assert blue_pixels > 50, f'Blue outline not found (count={blue_pixels})'

# Check for green pixels (nail polygon outline in BGR: low B, high G, low R)
green_mask = (img[:, :, 0] < 80) & (img[:, :, 1] > 180) & (img[:, :, 2] < 80)
green_pixels = np.sum(green_mask)
print(f'Green nail outline pixels: {green_pixels}')
assert green_pixels > 50, f'Green outline not found (count={green_pixels})'

# Check for red pixels (measurement text in BGR: low B, low G, high R)
red_mask = (img[:, :, 0] < 80) & (img[:, :, 1] < 80) & (img[:, :, 2] > 180)
red_pixels = np.sum(red_mask)
print(f'Red measurement text pixels: {red_pixels}')
assert red_pixels > 50, f'Red measurement labels not found (count={red_pixels})'

print('\n-> Visual annotations (Blue coin, Green nails, Red text) CONFIRMED!')

print('\n=======================================================')
print('3. TEST FAILURE CASE: IMAGE WITHOUT Rs. 10 COIN')
print('=======================================================')
no_coin_path = 'media/uploads/test_hand_0002801.jpg'
with open(no_coin_path, 'rb') as f:
    resp_no_coin = requests.post(API_URL, files={'image': ('no_coin.jpg', f, 'image/jpeg')})
print(f'HTTP STATUS: {resp_no_coin.status_code}')
data_no_coin = resp_no_coin.json()
print('RESPONSE JSON:', json.dumps(data_no_coin, indent=2))
assert resp_no_coin.status_code == 422, f'Expected 422, got {resp_no_coin.status_code}'
assert data_no_coin['success'] is False, 'Expected success: False'
assert data_no_coin['coin_detected'] is False, 'Expected coin_detected: False'
assert data_no_coin['error'] == 'Please upload an image with a clearly visible verified ₹10 coin.'
print('-> Rejection of image without verified Rs. 10 coin CONFIRMED!')

print('\n=======================================================')
print('4. TEST MISSING IMAGE FIELD')
print('=======================================================')
resp_missing = requests.post(API_URL, data={})
print(f'HTTP STATUS: {resp_missing.status_code}')
data_missing = resp_missing.json()
print('RESPONSE JSON:', json.dumps(data_missing, indent=2))
assert resp_missing.status_code == 400, f'Expected 400, got {resp_missing.status_code}'
assert data_missing['success'] is False
assert 'error' in data_missing
print('-> Missing image field rejection CONFIRMED!')

print('\n=======================================================')
print('5. TEST UNSUPPORTED FILE (PDF)')
print('=======================================================')
fake_pdf = b'%PDF-1.4\n%Fake PDF file for testing'
resp_pdf = requests.post(API_URL, files={'image': ('document.pdf', fake_pdf, 'application/pdf')})
print(f'HTTP STATUS: {resp_pdf.status_code}')
data_pdf = resp_pdf.json()
print('RESPONSE JSON:', json.dumps(data_pdf, indent=2))
assert resp_pdf.status_code == 400, f'Expected 400, got {resp_pdf.status_code}'
assert data_pdf['success'] is False
assert data_pdf['error'] == 'Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image.'
print('-> Unsupported file rejection CONFIRMED!')

print('\nALL LIVE END-TO-END API TESTS PASSED!')
