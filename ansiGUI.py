import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import numpy as np
import threading

generated_art = None

# ANSI Art Generation Functions
def generate_ansi_art(image_path, num_layers, scale, font_size):
    image = Image.open(image_path).convert('RGB')
    new_width = int(image.width * scale)
    new_height = int(image.height * scale)
    image = image.resize((new_width, new_height), Image.NEAREST)
    color_data = np.array(image)

    output_width = new_width * font_size
    output_height = new_height * font_size
    final_output = Image.new("RGBA", (output_width, output_height), color=(0, 0, 0, 0))

    for layer in range(num_layers):
        layer_output = render_layer_to_png(image, color_data, layer, num_layers, font_size)
        final_output = Image.alpha_composite(final_output, layer_output)

    return final_output

def render_layer_to_png(image, color_data, layer, num_layers, font_size):
    layer_width, layer_height = image.size
    layer_output = Image.new("RGBA", (layer_width * font_size, layer_height * font_size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(layer_output)
    font = ImageFont.truetype("arial.ttf", font_size)

    min_brightness, max_brightness = (256 // num_layers) * layer, (256 // num_layers) * (layer + 1)

    for y in range(layer_height):
        for x in range(layer_width):
            pixel = image.getpixel((x, y))
            brightness = int(sum(pixel) / 3)
            if min_brightness <= brightness < max_brightness:
                char = map_brightness_to_char(brightness)
                color = tuple(color_data[y, x])
                draw.text((x * font_size, y * font_size), char, fill=color, font=font)

    return layer_output

def map_brightness_to_char(brightness):
    chars = "@%#*+=-:. "
    return chars[brightness * len(chars) // 256]

# Tkinter GUI Functions
def load_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            image = Image.open(file_path)
            image.thumbnail((preview_box_size, preview_box_size))
            photo = ImageTk.PhotoImage(image)
            preview_label.config(image=photo)
            preview_label.image = photo
            preview_label.file_path = file_path
        except Exception as e:
            messagebox.showerror("Oopsie Daisy!", "Couldn't load the image. It might be camera shy!")

def generate_preview():
    try:
        num_layers = int(num_layers_entry.get())
        scale = float(scale_entry.get())
        font_size = int(font_size_entry.get())
        if hasattr(preview_label, 'file_path'):
            image_path = preview_label.file_path
            thread = threading.Thread(target=lambda: threaded_preview(image_path, num_layers, scale, font_size))
            thread.start()
    except ValueError:
        messagebox.showerror("Whoops!", "Numbers, please! The machine gods hunger for digits.")
    except Exception as e:
        messagebox.showerror("Uh-oh!", "Something went wonky in the matrix.")

def threaded_preview(image_path, num_layers, scale, font_size):
    try:
        global generated_art
        generated_art = generate_ansi_art(image_path, num_layers, scale, font_size)
        final_art_thumbnail = generated_art.copy()
        final_art_thumbnail.thumbnail((preview_box_size, preview_box_size))
        photo = ImageTk.PhotoImage(final_art_thumbnail)
        def update_preview():
            preview_label.config(image=photo)
            preview_label.image = photo  # ImageTk.PhotoImage reference
        root.after(0, update_preview)
    except Exception as e:
        messagebox.showerror("Yikes!", f"The art-o-matic broke: {e}")

def save_image():
    global generated_art
    if generated_art:
        file_path = filedialog.asksaveasfilename(defaultextension='.png',
                                                 filetypes=[("PNG files", "*.png"), ("All Files", "*.*")])
        if file_path:
            try:
                generated_art.save(file_path)
                messagebox.showinfo("Success!", "Your masterpiece is saved!")
            except Exception as e:
                messagebox.showerror("Oops!", f"Failed to save the image: {e}")
    else:
        messagebox.showerror("Hold Up!", "Generate some art first, then think about saving it!")

# Main Window Setup
root = tk.Tk()
root.title("cANSIr")
root.geometry('600x600')

# Styling for Buttons
style = ttk.Style()
style.configure('TButton', font=('Arial', 10), borderwidth='4')
style.map('TButton', foreground=[('!active', 'black'), ('active', 'blue')], background=[('!active', 'white'), ('active', 'lightblue')])

# Constants
preview_box_size = 250

# Load Image Button
load_button = ttk.Button(root, text="Load Image", command=load_image)
load_button.pack(pady=10)

# Number of Layers Input
num_layers_label = tk.Label(root, text="Number of Layers:")
num_layers_label.pack()
num_layers_entry = tk.Entry(root)
num_layers_entry.pack()
num_layers_entry.insert(0, "10")

# Scale Input
scale_label = tk.Label(root, text="Scale:")
scale_label.pack()
scale_entry = tk.Entry(root)
scale_entry.pack()
scale_entry.insert(0, "0.1")

# Font Size Input
font_size_label = tk.Label(root, text="Font Size:")
font_size_label.pack()
font_size_entry = tk.Entry(root)
font_size_entry.pack()
font_size_entry.insert(0, "10")

# Generate Preview Button
generate_button = ttk.Button(root, text="Generate Preview", command=generate_preview)
generate_button.pack(pady=10)

save_button = ttk.Button(root, text="Save Image", command=save_image)
save_button.pack(pady=10)


# Preview Label
preview_label = tk.Label(root)
preview_label.pack(pady=10)

# Start the Application
root.mainloop()
