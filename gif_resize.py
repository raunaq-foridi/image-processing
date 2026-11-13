#Raunaq Foridi 2026
#A tool to resize gifs
#Preserves transparency, fits image to square without stretching

from PIL import Image, ImageSequence
from pathlib import Path

# ------------- SETTINGS --------------- #

INPUT_DIR = Path("input_gifs")
OUTPUT_DIR = Path("output_gifs")

OUTPUT_SIZE = 512

RESAMPLING = Image.Resampling.NEAREST       #NEAREST is best for pixel art
                                            #BOX, BILINEAR, HAMMING, BICUBIC, LANCZOS

#SETUP
if not INPUT_DIR.exists() or not INPUT_DIR.is_dir():
    print("ERROR: Input folder not found")


OUTPUT_DIR.mkdir(exist_ok=True)
gif_files = list(INPUT_DIR.glob("*.gif"))
print(f"Found {len(gif_files)} GIFs.")



# ------------- CONVERSION -------------- #

for gif_path in gif_files:
    print(f"Processing: {gif_path.name}")
    
    try:
        gif = Image.open(gif_path)
        frames = []
        durations = []
        
        for frame in ImageSequence.Iterator(gif):

            #Preserve original frame duration
            duration = frame.info.get("duration",gif.info.get("duration", 100))

            durations.append(duration)

            #Convert to RGBA
            frame = frame.convert("RGBA")
            original_width, original_height = frame.size
            
            #Calculate uniform scaling factor
            scale = min(OUTPUT_SIZE / original_width, OUTPUT_SIZE / original_height)

            new_width = round(original_width * scale)
            new_height = round(original_height * scale)

            #Resize using nearest-neighbour
            frame = frame.resize((new_width, new_height), RESAMPLING)

            #Create transparent canvas
            canvas = Image.new("RGBA",(OUTPUT_SIZE, OUTPUT_SIZE),(0, 0, 0, 0))

            # Centre the image
            x = (OUTPUT_SIZE - new_width) // 2
            y = (OUTPUT_SIZE - new_height) // 2

            canvas.alpha_composite(frame, (x, y))

            # ---- CONVERT TO GIF PALETTE ---- #

            alpha = canvas.getchannel("A")
            #Convert RGB data to a palette with 255 colours
            paletted = canvas.convert("RGB").quantize(colors=255,method=Image.Quantize.FASTOCTREE)

            #Ensure the palette has exactly 256 entries
            palette = paletted.getpalette()

            palette = palette[:768]
            palette += [0] * (768 - len(palette))

            paletted.putpalette(palette)

            #Reserve palette index 255 for transparency
            transparent_mask = alpha.point(lambda a: 255 if a < 128 else 0)
            paletted.paste(255, mask=transparent_mask)

            #Store the completed frame
            frames.append(paletted)

        # --------- SAVE GIF --------- #

        output_path = OUTPUT_DIR / gif_path.name

        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=gif.info.get("loop", 0),
            disposal=2,
            transparency=255,
            background=255,
            optimize=False
        )
        print(f"  Saved: {output_path.name}")

    except Exception as e:
        print(f"  ERROR: {e}")

print("Batch conversion complete!")
