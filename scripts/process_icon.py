import os
from PIL import Image
import io

input_path = 'symbol.png'
output_path = 'assets/icon.png'

if not os.path.exists(input_path):
    print(f"Error: {input_path} not found.")
    exit(1)

print(f"Processing {input_path}...")

success = False

# Try rembg first
try:
    print("Attempting to use rembg...")
    from rembg import remove
    with open(input_path, 'rb') as i:
        input_data = i.read()
        subject = remove(input_data)
        img = Image.open(io.BytesIO(subject))
        img.save(output_path)
        print(f"Saved transparent icon to {output_path} using rembg")
        success = True
except Exception as e:
    print(f"rembg failed: {e}")

# Fallback to simple white removal
if not success:
    try:
        print("Attempting fallback white background removal...")
        img = Image.open(input_path)
        img = img.convert("RGBA")
        datas = img.getdata()
        
        newData = []
        for item in datas:
            # Change all white (also shades of whites) to transparent
            # Adjust threshold as needed
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        
        img.putdata(newData)
        img.save(output_path)
        print(f"Saved fallback icon to {output_path}")
        success = True
    except Exception as e2:
        print(f"Fallback failed: {e2}")
        exit(1)
