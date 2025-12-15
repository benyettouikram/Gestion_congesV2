import tkinter as tk
from Frontend.Theme.colors import TEXT_COLOR, Heading_table_color

class CustomButton(tk.Button):
    def __init__(self, parent, text, color, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            bg=color,
            fg=TEXT_COLOR,
            activebackground=Heading_table_color,
            activeforeground="#000",
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            width=15,   # ✅ consistent width
            height=1,   # ✅ consistent height
            bd=0,
            **kwargs
        )
        if command:
            self.configure(command=command)

        # Pack style (you can override when calling)
        self.pack(side="left", padx=8, pady=5)

        # Hover effect
        self.bind("<Enter>", lambda e: self.config(bg=Heading_table_color, fg="#000"))
        self.bind("<Leave>", lambda e: self.config(bg=color, fg=TEXT_COLOR))
