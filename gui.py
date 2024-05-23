import customtkinter as ctk
from tkinter import filedialog
from pixel_sorting import pixel_sort, SortMethod
from utils import load_image, save_image


class PixlR(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.title("PixlR")
        self.geometry("1000x600")

        # Configure the layout
        self.grid_columnconfigure(0, weight=0)  # Options column
        self.grid_columnconfigure(1, weight=1)  # Image column
        self.grid_columnconfigure(2, weight=0)  # Controls column
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)

        # Options tab
        self.options_frame = ctk.CTkFrame(self, width=200)
        self.options_frame.grid(row=0, column=0, rowspan=5, sticky="nsw", padx=10, pady=10)
        self.create_options_tab()

        # Image display
        self.image_frame = ctk.CTkFrame(self)
        self.image_frame.grid(row=0, column=1, rowspan=5, sticky="nsew", padx=10, pady=10)
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.image_frame.grid_rowconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(self.image_frame, text="Click here to add image")
        self.image_label.grid(row=0, column=0)

        # Controls frame
        self.controls_frame = ctk.CTkFrame(self, width=200)
        self.controls_frame.grid(row=0, column=2, rowspan=5, sticky="nse", padx=10, pady=10)
        self.create_controls_tab()

        # Bind image click
        self.image_label.bind("<Button-1>", self.load_image)

        # Initialize instance attributes
        self.image = None
        self.processed_image = None
        self.photo = None
        self.threshold = 0
        self.sort_method = SortMethod.LUMINOSITY
        self.sort_direction = 1  # 1 for x-axis, 0 for y-axis

        # Disable controls initially
        self.enable_controls(False)

    def create_options_tab(self):
        # Sorting method buttons
        ctk.CTkLabel(self.options_frame, text="Sorting Method:").grid(row=0, column=0, pady=10)
        self.method_buttons = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.method_buttons.grid(row=1, column=0, pady=10)
        methods = ["Luminosity", "Hue", "Saturation"]
        self.method_button_objects = []
        for i, method in enumerate(methods):
            button = ctk.CTkButton(self.method_buttons, text=method, command=lambda m=method: self.set_sort_method(m))
            button.grid(row=i, column=0, pady=5, padx=5, sticky="ew")
            self.method_button_objects.append(button)

        # Sorting direction buttons
        ctk.CTkLabel(self.options_frame, text="Sorting Direction:").grid(row=2, column=0, pady=10)
        self.direction_buttons = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.direction_buttons.grid(row=3, column=0, pady=10)
        directions = ["X Axis", "Y Axis"]
        self.direction_button_objects = []
        for i, direction in enumerate(directions):
            button = ctk.CTkButton(self.direction_buttons, text=direction, command=lambda d=direction: self.set_sort_direction(d))
            button.grid(row=i, column=0, pady=5, padx=5, sticky="ew")
            self.direction_button_objects.append(button)

    def create_controls_tab(self):
        # Threshold slider
        ctk.CTkLabel(self.controls_frame, text="Sort Intensity").grid(row=0, column=0, pady=10)
        self.threshold_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=255, command=self.update_threshold, orientation="vertical")
        self.threshold_slider.set(0)
        self.threshold_slider.grid(row=1, column=0, pady=10, padx=10, sticky="ns")

        # Threshold buttons
        self.button_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, pady=10, sticky="nsew")
        self.button_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.threshold_button_objects = []
        self.create_threshold_buttons()

        # Save button
        self.save_button = ctk.CTkButton(self.controls_frame, text="Save Image", command=self.save_image)
        self.save_button.grid(row=3, column=0, pady=10)

    def enable_controls(self, enable):
        state = "normal" if enable else "disabled"
        fg_color = "grey" if not enable else "#2fa572"
        hover_color = "darkgrey" if not enable else "#106A43"
        for button in self.method_button_objects:
            button.configure(state=state, fg_color=fg_color, hover_color=hover_color)
        for button in self.direction_button_objects:
            button.configure(state=state, fg_color=fg_color, hover_color=hover_color)
        for button in self.threshold_button_objects:
            button.configure(state=state, fg_color=fg_color, hover_color=hover_color)
        self.threshold_slider.configure(state=state)
        self.save_button.configure(state=state, fg_color=fg_color, hover_color=hover_color)

    def set_sort_method(self, method):
        method_map = {
            "Luminosity": SortMethod.LUMINOSITY,
            "Hue": SortMethod.HUE,
            "Saturation": SortMethod.SATURATION
        }
        self.sort_method = method_map[method]
        self.update_threshold(self.threshold_slider.get())

    def set_sort_direction(self, direction):
        self.sort_direction = 1 if direction == "X Axis" else 0
        self.update_threshold(self.threshold_slider.get())

    def create_threshold_buttons(self):
        percentages = [0, 25, 50, 75, 100]
        for i, pct in enumerate(percentages):
            button = ctk.CTkButton(self.button_frame, text=f"{pct}%", command=lambda p=pct: self.set_threshold(p))
            button.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            self.threshold_button_objects.append(button)

    def set_threshold(self, pct):
        self.threshold_slider.set(pct * 2.55)  # Convert percentage to 0-255 range
        self.update_threshold(pct * 2.55)

    def update_threshold(self, value):
        self.threshold = int(value)
        if self.image is not None:
            self.processed_image = pixel_sort(self.image, self.threshold, self.sort_method, self.sort_direction)
            self.display_image(self.processed_image)

    def load_image(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image = load_image(file_path)
            self.processed_image = self.image
            self.display_image(self.image)
            self.resize_window_to_image(self.image)
            self.enable_controls(True)

    def display_image(self, img):
        img.thumbnail((800, 600))
        self.photo = ctk.CTkImage(light_image=img, size=(img.width, img.height))
        self.image_label.configure(image=self.photo, text="")
        self.image_label.grid(row=0, column=0)
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.image_frame.grid_rowconfigure(0, weight=1)

    def resize_window_to_image(self, img):
        width, height = img.size
        self.geometry(f"{width + 440}x{height + 200}")  # Additional space for options and controls

    def save_image(self):
        if self.processed_image is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if save_path:
                save_image(self.processed_image, save_path)


if __name__ == "__main__":
    app = PixlR()
    app.mainloop()
