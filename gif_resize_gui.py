import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from PIL import Image, ImageSequence
from pathlib import Path

OUTPUT_SIZE=512   #no longer used


RESAMPLING_OPTIONS = {
    "NEAREST": Image.Resampling.NEAREST,
    "BOX": Image.Resampling.BOX,
    "BILINEAR": Image.Resampling.BILINEAR,
    "HAMMING": Image.Resampling.HAMMING,
    "BICUBIC": Image.Resampling.BICUBIC,
    "LANCZOS": Image.Resampling.LANCZOS,
}

input_files = []
output_dir = None

def select_input_folder():

    global input_files

    folder = filedialog.askdirectory(title="Select Input Folder")
    if folder:
        folder = Path(folder)

        input_files = sorted(
            p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".gif"
        )

        input_label.config(text=f"{len(input_files)} GIFs found in {folder.name}")

def select_input_files():

    global input_files

    files = filedialog.askopenfilenames(
        title="Select GIF files",
        filetypes=[("GIF files","*.gif"),("All files","*.*")]
    )
    if files:
        input_files = [
            Path(f) for f in files if Path(f).suffix.lower() == ".gif"
        ]

        input_label.config(text=f"{len(input_files)} GIFs selected")

def select_output_folder():

    global output_dir

    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        output_dir = Path(folder)

        output_label.config(text=str(output_dir))

def run_processing():

    #global output_dir
    
    if not input_files:
        messagebox.showerror("Error","Please select GIFs to resize")
        return

    '''if output_dir is None:
        output_dir = Path("output_gifs")
        output_dir.mkdir(exist_ok=True)
        #return'''

    selected_resampling = RESAMPLING_OPTIONS[resampling_var.get()]
    status_label.config(text="Processing...")
    run_button.config(state="disabled")

    files_to_process = list(input_files)
    destination = output_dir

    try:
        selected_size = int(size_var.get())

        if selected_size <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror("Invalid Size","Please enter a positive whole number.")
        return

    
    #Threading processing off from the GUI
    def worker():
        try:
            process_gifs(
                files_to_process,
                destination,
                selected_resampling,
                selected_size
            )
            root.after(0, processing_complete)

        except Exception as e:
            root.after(0, lambda error=str(e) : processing_error(error))


    threading.Thread(target=worker, daemon=True).start()

def processing_complete():
    run_button.config(state="normal")
    status_label.config(text="Finished")

    messagebox.showinfo("Complete","All GIFs have been processed")

def processing_error(error):
    run_button.config(state="normal")
    status_label.config(text="An Error occurred")

    messagebox.showerror("Processing Error",error)


# ---- Processing ---- #

def process_gifs(input_files, output_dir, resampling,selected_size):

    if output_dir is None:
        output_dir = Path("output_gifs")
        output_dir.mkdir(exist_ok=True)

    for gif_path in input_files:
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
                scale = min(selected_size / original_width, selected_size / original_height)

                new_width = round(original_width * scale)
                new_height = round(original_height * scale)

                #Resize using nearest-neighbour
                frame = frame.resize((new_width, new_height), resampling)

                #Create transparent canvas
                canvas = Image.new("RGBA",(selected_size, selected_size),(0, 0, 0, 0))

                # Centre the image
                x = (selected_size - new_width) // 2
                y = (selected_size - new_height) // 2

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

            output_path = output_dir / gif_path.name

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


# ------ GUI ------ #

root = tk.Tk()
root.title("GIF Resizer")
root.geometry("500x550")
root.resizable(False,False)

size_var = tk.StringVar(master=root, value="512")

tk.Label(root,text="GIF Resizer",font=("Arial",22,"bold")).pack(pady=20)

#INPUT

tk.Label(root,text="INPUT",font=("Arial",10,"bold")).pack()

tk.Button(root,text="Select Input Folder",command=select_input_folder,width=20).pack(pady=3)
tk.Button(root,text="Select Files",command=select_input_files,width=20).pack(pady=3)

input_label = tk.Label(root, text="No Input Selected", fg="gray")
input_label.pack(pady=5)

#OUTPUT
tk.Label(root,text="OUTPUT",font=("Arial",10,"bold")).pack(pady=(15,3))
tk.Button(root,text="Select Output Folder",command=select_output_folder,width=20).pack()

output_label = tk.Label(root, text="Default /output_gifs", fg="gray", wraplength=450)
output_label.pack(pady=5)

#SIZE

tk.Label(root, text="OUTPUT SIZE").pack(pady=(15, 3))
size_entry = tk.Entry(root,textvariable=size_var,width=10,justify="center")

size_entry.pack()

#RESAMPLING

tk.Label(root,text="RESAMPLING METHOD",font=("Arial",10,"bold")).pack(pady=(15,3))
resampling_var = tk.StringVar(value="NEAREST")

resampling_dropdown = ttk.Combobox(
    root,
    textvariable=resampling_var,
    values=list(RESAMPLING_OPTIONS.keys()),
    state="readonly",
    width=18
)
resampling_dropdown.pack()

#RUN
run_button = tk.Button(root, text="RUN",command=run_processing,bg="lightgreen",font=("Arial",12,"bold"),width=20)
run_button.pack(pady=20)

status_label = tk.Label(root,text="Ready")
status_label.pack()

root.mainloop()

