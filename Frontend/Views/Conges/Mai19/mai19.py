import tkinter as tk

class Residence19mai(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        title = tk.Label(
            self,
            text="الإقامة الجامعية 01 - إقامة لادّو",
            font=("Arial", 28, "bold"),
            bg="white",
            fg="#2C3E50"
        )
        title.pack(pady=40)

        desc = tk.Label(
            self,
            text="مرحبا بك في صفحة إقامة لادّو. هنا يمكنك إدارة الموظفين.",
            font=("Arial", 16),
            bg="white",
            fg="#555"
        )
        desc.pack(pady=10)