# 📄 Frontend/Components/AddButton.py
import tkinter as tk
from tkinter import ttk
from Frontend.Theme.colors import PRIMARY_COLOR
class Update_button(ttk.Frame):
    def __init__(self, parent, text="✏️", command=None, **kwargs):
        super().__init__(parent, **kwargs)

        style = ttk.Style()
        style.configure(
            "update.TButton",
            foreground="white",
            background= PRIMARY_COLOR,
            font=("Segoe UI", 10, "bold"),
            padding=4
        )

        style.map("update.TButton", background=[("active", "#388E3C")])

        self.button = ttk.Button(
            self,
            text=text,
            command=command,
            style="update.TButton",
            width=20  # petit bouton
        )
        self.button.pack()
