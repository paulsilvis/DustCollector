from PIL import Image

# Load the original JPEG
original = Image.open("harper.jpg")

# Crop to 2:1 aspect ratio (center crop)
width, height = original.size
target_aspect = 2.0
target_height = int(width / target_aspect)

if target_height > height:
    target_width = int(height * target_aspect)
    left = (width - target_width) // 2
    top = 0
    right = left + target_width
    bottom = height
else:
    left = 0
    top = (height - target_height) // 2
    right = width
    bottom = top + target_height

cropped = original.crop((left, top, right, bottom))

# Resize to OLED resolution
resized = cropped.resize((128, 64), Image.LANCZOS)

# Convert to 1-bit with dithering
bw = resized.convert("1")

# Save it as a black-and-white PNG
bw.save("harper_bw.png")
print("Saved harper_bw.png successfully.")
