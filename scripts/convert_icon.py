from PIL import Image
import os

input_path = 'Image (1).webp'
output_path = 'assets/icon.png'

if not os.path.exists(input_path):
    print(f"Error: {input_path} not found.")
    exit(1)

print(f"Converting {input_path} to {output_path}...")

try:
    img = Image.open(input_path)
    img.save(output_path, 'PNG')
    print(f"Successfully converted and saved to {output_path}")

except Exception as e:
    print(f"Error converting image: {e}")
    exit(1)
