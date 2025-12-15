import tkinter as tk

class HomePage(tk.Frame):
    def __init__(self, parent, on_open_page=None):
        super().__init__(parent, bg="#F2F4F7")
        self.on_open_page = on_open_page

        # ---- Page Title ----
        title = tk.Label(
            self,
            text="إخـتـر الإقـامـة",
            font=("Arial", 28, "bold"),
            bg="#F2F4F7",
            fg="#2C3E50"
        )
        title.pack(pady=30)

        container = tk.Frame(self, bg="#F2F4F7")
        container.pack(expand=True)

        residences = [
            "مديرية الخدمات الجامعية",
            "الإقامة الجامعية 19 ماي 1956",
            "الإقامة الجامعية 1 نوفمبر 1954",
            "الإقامة الجامعية هني صالح",
            "الإقامة الجامعية طويل عبد القادر",
            "الإقامة الجامعية أولاد فارس 03 ",
            "الإقامة الجامعية أولاد فارس 04 ",
            "الإقامة الجامعية الحسنية 1500 سرير",
            "الإقامة الجامعية الحسنية 2000 سرير",
            "الإقامة الجامعية تنس 500 سرير ",
        
        ]

        index = 0
        for r in range(2):
            for c in range(5):
                name = residences[index]
                card = self.create_card(container, name)
                card.grid(row=r, column=c, padx=20, pady=20)
                index += 1

    # -------------------------------------------
    def create_card(self, parent, title_text):
        frame = tk.Frame(parent, bg="white", width=240, height=160)
        frame.pack_propagate(False)

        # simple shadow
        frame.config(highlightbackground="#D0D3D4", highlightthickness=1)

        # Hover
        frame.bind("<Enter>", lambda e: frame.config(bg="#E8F6F3"))
        frame.bind("<Leave>", lambda e: frame.config(bg="white"))

        # Click
        frame.bind("<Button-1>", lambda e: self.open_residence(title_text))

        icon = tk.Label(frame, text="🏢", font=("Arial", 40), bg="white")
        icon.pack(pady=10)
        icon.bind("<Button-1>", lambda e: self.open_residence(title_text))

        label = tk.Label(frame, text=title_text, font=("Arial", 14, "bold"), bg="white")
        label.pack()
        label.bind("<Button-1>", lambda e: self.open_residence(title_text))

        return frame

    # -------------------------------------------
    def open_residence(self, residence_name):
        print("Opening:", residence_name)

        if self.on_open_page:
            # ---- Redirections possibles ----
            if residence_name == "مديرية الخدمات الجامعية":
                self.on_open_page("Dou")          # Page spéciale 1
            elif residence_name == "الإقامة الجامعية 19 ماي 1956":
                self.on_open_page("mai19")        # Page spéciale 2
            else:
                self.on_open_page("home")         # Page par défaut
    