# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os


class ImageNumberingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Numbering")
        self.root.iconbitmap("./favicon.ico")

        
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.open_button = tk.Button(self.top_frame, text="Open Image", command=self.open_image)
        self.open_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.top_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(side=tk.LEFT)

        self.increase_button = tk.Button(self.top_frame, text="Increase Circle Size (+)", command=self.increase_font_size)
        self.increase_button.pack(side=tk.LEFT)

        self.decrease_button = tk.Button(self.top_frame, text="Decrease Circle Size (-)", command=self.decrease_font_size)
        self.decrease_button.pack(side=tk.LEFT)
        
        self.clear_button = tk.Button(self.top_frame, text="Clear All", command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(root, highlightthickness=2, highlightbackground="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status_frame = tk.Frame(root, bg="#444444")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.size_label = tk.Label(self.status_frame, text="Circle Size: 15", bg="#444444", fg="white")
        self.size_label.pack(side=tk.RIGHT, padx=5)

        self.image = None
        self.tk_image = None
        self.original_image = None
        self.zoom_factor = 1.0
        self.numbers = []
        self.current_number = 1
        self.font_size = 16
        self.radius = 15
        self.preview_circle = None

        self.canvas.bind("<Button-1>", self.add_number)
        self.canvas.bind("<Motion>", self.update_preview_circle)
        self.canvas.bind("<Control-MouseWheel>", self.adjust_circle_size)
        self.root.bind('<Configure>', self.center_image)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.zoom_factor = 1.0
            self.update_image()
            self.clear_all_numbers()
            self.root.title(self.shorten_file_name(os.path.basename(file_path)))
            if self.preview_circle:
                self.canvas.delete(self.preview_circle)
            self.preview_circle = None
            self.adjust_window_size()

    def shorten_file_name(self, file_name, max_length=30):
        if len(file_name) > max_length:
            return file_name[:10] + "..." + file_name[-10:]
        return file_name

    def adjust_window_size(self):
        if self.tk_image:
            image_width = self.tk_image.width()
            image_height = self.tk_image.height()
            top_frame_height = self.top_frame.winfo_height()

            # Set the minimum width to prevent shrinking below the top frame size
            min_width = self.top_frame.winfo_reqwidth()
            window_width = max(image_width, min_width)
            window_height = image_height + top_frame_height

            self.root.geometry(f"{window_width}x{window_height}")
            self.root.minsize(min_width, window_height)

    def update_image(self):
        width, height = self.original_image.size
        new_size = (int(width * self.zoom_factor), int(height * self.zoom_factor))
        resized_image = self.original_image.resize(new_size, Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)
        self.center_image()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.update_image()

    def clear_all_numbers(self):
        self.canvas.delete("all")
        self.numbers = []
        self.current_number = 1
        if self.tk_image:
            self.center_image()

    def center_image(self, event=None):
        if self.tk_image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            image_width = self.tk_image.width()
            image_height = self.tk_image.height()
            x = (canvas_width - image_width) // 2
            y = (canvas_height - image_height) // 2
            self.canvas.delete("all")
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_image)
            for number, x_pos, y_pos, radius, font_size, oval, number_text in self.numbers:
                new_x = x + int(x_pos * self.zoom_factor)
                new_y = y + int(y_pos * self.zoom_factor)
                self.canvas.create_oval(new_x - radius, new_y - radius, new_x + radius, new_y + radius, outline="red", width=2)
                self.canvas.create_text(new_x, new_y, text=str(number), fill="red", font=("Helvetica", font_size))

    def add_number(self, event, record_action=True):
        if self.tk_image:
            x, y = event.x, event.y
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            image_width = self.tk_image.width()
            image_height = self.tk_image.height()
            image_x = (canvas_width - image_width) // 2
            image_y = (canvas_height - image_height) // 2
            x -= image_x
            y -= image_y
            x = int(x / self.zoom_factor)
            y = int(y / self.zoom_factor)

            oval = self.canvas.create_oval(event.x - self.radius, event.y - self.radius, event.x + self.radius, event.y + self.radius, outline="red", width=2)
            number_text = self.canvas.create_text(event.x, event.y, text=str(self.current_number), fill="red", font=("Helvetica", self.font_size))
            self.numbers.append((self.current_number, x, y, self.radius, self.font_size, oval, number_text))
            self.current_number += 1

    def save_image(self):
        if self.original_image:
            draw = ImageDraw.Draw(self.original_image)
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
            except IOError:
                font = ImageFont.load_default()

            for number, x, y, radius, font_size, oval, number_text in self.numbers:
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="red", width=2)
                bbox = draw.textbbox((x, y), str(number), font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                draw.text((x - text_width / 2, y - text_height / 2), str(number), fill="red", font=font)
            
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.original_image.save(file_path)
    
    def increase_font_size(self):
        self.font_size += 2
        self.radius += 2
        self.size_label.config(text=f"Circle Size: {self.radius}")

    def decrease_font_size(self):
        if self.font_size > 8:  # Minimum font size limit
            self.font_size -= 2
            self.radius -= 2
            self.size_label.config(text=f"Circle Size: {self.radius}")

    def adjust_circle_size(self, event):
        if event.state & 0x0004:  # Check if the Control key is held down
            if event.delta > 0:
                self.increase_font_size()
            else:
                self.decrease_font_size()

    def clear_all(self):
        self.clear_all_numbers()

    def update_preview_circle(self, event):
        if self.preview_circle:
            self.canvas.delete(self.preview_circle)
        self.preview_circle = self.canvas.create_oval(event.x - self.radius, event.y - self.radius, event.x + self.radius, event.y + self.radius, outline="blue", width=1, dash=(3, 5))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageNumberingApp(root)
    root.mainloop()
