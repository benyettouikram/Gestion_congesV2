import tkinter as tk
from Frontend.Components.Navbar import Navbar
from Frontend.Views.HomePage import HomePage
from Frontend.Views.Employes.EmployeHome import EmployesPage
from Frontend.Views.Conges.Dou.Dou import ResidenceDou
from Frontend.Views.Conges.Mai19.mai19 import Residence19mai
from Frontend.Views.Conges.Novembre.nov1954 import ResidenceNov1954
from Frontend.Views.Conges.heni.heni import ResidenceHeni
from Frontend.Views.Conges.Touil.Touil import ResidenceTouil
from Frontend.Views.Conges.ouled_fares_03.ouled_fares_03 import ResidenceOuledFares03
from Frontend.Views.Conges.ouled_fares_04.ouled_fares_04 import ResidenceOuledFares04
from Frontend.Views.Conges.tens_500.tens_500 import ResidenceTens500      
from Frontend.Views.Conges.hassania_1500.hassania_1500 import ResidenceHassania1500
from Frontend.Views.Conges.hassania_2000.hassania_2000 import ResidenceHassania2000  
from Bakend.models.Conges.GenericResidence import debug_residences
debug_residences()  # ✅ Affiche les résidences disponibles dans la console pour vérification
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
            "mai19": Residence19mai(self.container),
            "nov1954": ResidenceNov1954(self.container),  # Placeholder, à remplacer par la classe réelle de cette résidence
            "heni": ResidenceHeni(self.container),      # Placeholder, à remplacer par la classe réelle de cette résidence
            "Touil": ResidenceTouil(self.container),    # Placeholder, à remplacer par la classe réelle de cette résidence
            "ouled_fares_03": ResidenceOuledFares03(self.container),  # Placeholder, à remplacer par la classe réelle de cette résidence
            "ouled_fares_04": ResidenceOuledFares04(self.container),  # Placeholder, à remplacer par la classe réelle de cette résidence
            "hassania_1500": ResidenceHassania1500(self.container),   # Placeholder, à remplacer par la classe réelle de cette résidence
            "hassania_2000": ResidenceHassania2000(self.container),   # Placeholder, à remplacer par la classe réelle de cette résidence
            "tens_500": ResidenceTens500(self.container),        # Placeholder, à remplacer par la classe réelle de cette résidence 
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