import tkinter as tk
from Frontend.Components.Navbar import Navbar
from Frontend.Views.HomePage import HomePage
from Frontend.Views.Employes.EmployeHome import EmployesPage
from Frontend.Views.Conges.Dou.Dou import ResidenceDou
from Frontend.Views.Conges.Mai19.mai19 import Residence19mai
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("1000x600")
        self.title("Gestion de Congé")
        self.configure(bg="#F5F6FA")

        # === Navbar ===
        self.navbar = Navbar(self, on_navigate=self.show_page)
        self.navbar.pack(fill="x")

        # === Main container for all pages ===
        self.container = tk.Frame(self, bg="#F5F6FA")
        self.container.pack(fill="both", expand=True)

        # === Pages ===
        # ✅ CORRECTION: Passer self.show_page à HomePage
        self.pages = {
            "home": HomePage(self.container, on_open_page=self.show_page),
            "employers": EmployesPage(self.container),
            "Dou": ResidenceDou(self.container),
            "mai19": Residence19mai(self.container)
        }

        # Place all pages in the same location
        for page in self.pages.values():
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        # ✅ Show HomePage first by default
        self.show_page("home")

    def show_page(self, page_name):
        """Bring the selected page to the front."""
        page = self.pages.get(page_name)
        if page:
            page.tkraise()
        else:
            print(f"⚠️ Page '{page_name}' n'existe pas!")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()