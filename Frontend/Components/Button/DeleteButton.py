import tkinter as tk

class DeleteButton(tk.Button):
    def __init__(self, parent, text="❌", command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=self._on_click,
            bg="#E74C3C",       # Normal color
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=10,
            pady=3,
            activebackground="#C0392B",  # Temporary press color
            cursor="hand2",
            **kwargs
        )

        self.default_bg = "#E74C3C"
        self.clicked_bg = "#B03A2E"
        self.is_clicked = False
        self.user_command = command

    def _on_click(self):
        """Toggle background color when clicked."""
        if not self.is_clicked:
            self.configure(bg=self.clicked_bg)
            self.is_clicked = True
        else:
            self.configure(bg=self.default_bg)
            self.is_clicked = False

        # Execute original command if provided
        if self.user_command:
            self.user_command()
