import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os
from Frontend.Theme.colors import PRIMARY_COLOR, TEXT_COLOR, Heading_table_color
from Frontend.Components.Button.CustomButton import CustomButton  # ✅ import CustomButton

class Navbar(tk.Frame):
    def __init__(self, parent, on_navigate=None):
        super().__init__(parent, bg=PRIMARY_COLOR, height=110)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.current_language = "arabic"

        # === Build logo path ===
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, "Frontend", "Assets", "logo.jpg")

        # === RIGHT SIDE: Logo + Titles ===
        right_frame = tk.Frame(self, bg=PRIMARY_COLOR)
        right_frame.pack(side="right", fill="y", padx=35, pady=10)

        content_frame = tk.Frame(right_frame, bg=PRIMARY_COLOR)
        content_frame.pack(side="right", anchor="e")

        logo_frame = tk.Frame(content_frame, bg=PRIMARY_COLOR)
        logo_frame.pack(side="right", padx=(0, 12))

        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                logo_img = self.create_circular_image(logo_img, 75)
                self.logo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(logo_frame, image=self.logo, bg=PRIMARY_COLOR, borderwidth=0)
                logo_label.pack()
            except Exception as e:
                print("⚠️ Error loading logo:", e)
                self.create_fallback_logo(logo_frame)
        else:
            print("⚠️ Logo not found at:", logo_path)
            self.create_fallback_logo(logo_frame)

        # === TEXT TITLES ===
        text_frame = tk.Frame(content_frame, bg=PRIMARY_COLOR)
        text_frame.pack(side="right", anchor="e")

        title_label = tk.Label(
            text_frame,
            text="مديرية الخدمات الجامعية شلف",
            font=("Segoe UI Semibold", 22),
            fg="white",
            bg=PRIMARY_COLOR,
            anchor="e",
            justify="right"
        )
        title_label.pack(anchor="e")

        subtitle_label = tk.Label(
            text_frame,
            text="نظام إدارة عطـل الموظفين",
            font=("Tahoma", 15),
            fg="white",
            bg=PRIMARY_COLOR,
            anchor="e",
            justify="right"
        )
        subtitle_label.pack(anchor="e", pady=(2, 0))

        # === LEFT SIDE: NAV BUTTONS ===
        left_frame = tk.Frame(self, bg=PRIMARY_COLOR)
        left_frame.pack(side="left", padx=10, pady=15)

        # === LANGUAGE BUTTON ===
        self.lang_btn = CustomButton(
            parent=left_frame,
            text="العربية / Français",
            color="#2E7D32",
            command=self.toggle_language
        )

        # === OTHER NAVIGATION BUTTONS ===
        buttons_data = [
            ("السجل", "historique"),
            ("الإجازات", "home"),
            ("الموظفون", "employers")
        ]

        self.nav_buttons = {}
        for text, page_name in buttons_data:
            btn = CustomButton(
                parent=left_frame,
                text=text,
                color="#2E7D32",
                command=lambda pg=page_name: self.navigate(pg)
            )
            self.nav_buttons[page_name] = btn

        self.pack(fill="x")

    # === Navigation ===
    def navigate(self, page_name):
        if self.on_navigate:
            self.on_navigate(page_name)

    # === Language Toggle ===
    def toggle_language(self):
        if self.current_language == "arabic":
            self.current_language = "french"
            self.lang_btn.config(text="Français / العربية")
            self.nav_buttons["employers"].config(text="Employés")
            self.nav_buttons["conges"].config(text="Congés")
            self.nav_buttons["historique"].config(text="Historique")
        else:
            self.current_language = "arabic"
            self.lang_btn.config(text="العربية / Français")
            self.nav_buttons["employers"].config(text="الموظفون")
            self.nav_buttons["conges"].config(text="الإجازات")
            self.nav_buttons["historique"].config(text="السجل")

    # === Logo helpers ===
    def create_circular_image(self, image, size):
        image = image.resize((size, size), Image.Resampling.LANCZOS)
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(image, (0, 0))
        output.putalpha(mask)
        return output

    def create_fallback_logo(self, parent):
        canvas = tk.Canvas(parent, width=75, height=75, bg=PRIMARY_COLOR,
                           highlightthickness=0, borderwidth=0)
        canvas.pack()
        canvas.create_oval(5, 5, 70, 70, fill=PRIMARY_COLOR, outline="white", width=2)
        canvas.create_text(37, 37, text="LOGO", fill=TEXT_COLOR, font=("Arial", 10, "bold"))
