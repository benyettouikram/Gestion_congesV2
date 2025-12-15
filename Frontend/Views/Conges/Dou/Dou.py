import tkinter as tk
from Frontend.Components.DataTable import DataTable
from Frontend.Components.SearchBar import SearchBar
from Frontend.Components.Button.UpdateButton import Update_button
from Frontend.Components.Button.AddButton import AddButton
from Bakend.models.Conges.Dou import get_employes_data   # فقط لجلب البيانات
from Frontend.Views.Conges.Dou.Add_Dou import AddCongeInterface
class ResidenceDou(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        # ───── Title ─────
        tk.Label(
            self,
            text="مديرية الخدمات الجامعية",
            font=("Arial", 28, "bold"),
            bg="white",
            fg="#2C3E50"
        ).pack(pady=20)

        tk.Label(
            self,
            text="مرحبا بك في صفحة مديرية الخدمات الجامعية. يمكنك إدارة الموظفين من هنا.",
            font=("Arial", 16),
            bg="white",
            fg="#555"
        ).pack(pady=5)

        # ───── Top Bar ─────
        top_frame = tk.Frame(self, bg="#F5F6FA")
        top_frame.pack(fill="x", padx=20, pady=(0, 5))

        # 🔎 Search
        self.search_bar = SearchBar(top_frame, on_search=self.filter_table)
        self.search_bar.pack(side="left", fill="x", expand=True)

        # 🔘 Buttons (right)
        buttons_frame = tk.Frame(top_frame, bg="#F5F6FA")
        buttons_frame.pack(side="right")

        # ➕ Ajouter Congé
        self.add_btn = AddButton(
            buttons_frame,
            text=" إضافة عطلة➕",
            command=self.open_add_form
        )
        self.add_btn.pack(side="left", padx=5)

        # ✏️ Modifier
        self.update_btn = Update_button(
            buttons_frame,
            text=" تعديل ✏️",
            command=self.open_update_form
        )
        self.update_btn.pack(side="left", padx=5)

        # ───── Table ─────
        table_container = tk.Frame(self, bg="white")
        table_container.pack(fill="both", expand=True, pady=5)

        self.columns = (
            "Action", "nouveau_reste", "jours_pris", "date_fin",
            "date_debut", "ancien_conges", "grade",
            "nom_prenom", "departement"
        )

        self.all_data = get_employes_data()

        self.table = DataTable(
            table_container,
            self.columns,
            self.all_data,
            on_delete=self.delete_employe,
            on_update=self.update_employe
        )
        self.table.pack(fill="both", expand=True)

        headers = [
            ("Action", "الإجراء", 120),
            ("nouveau_reste", "الرصيد الجديد", 130),
            ("jours_pris", "الأيام المأخوذة", 150),
            ("date_fin", "نهاية آخر عطلة", 150),
            ("date_debut", "بداية آخر عطلة", 150),
            ("ancien_conges", "العطلة القديمة", 200),
            ("grade", "الرتبة", 150),
            ("nom_prenom", "الاسم و اللقب", 150),
            ("departement", "القسم", 80)
        ]

        for col, title, width in headers:
            self.table.tree.heading(col, text=title, anchor="center")
            self.table.tree.column(col, anchor="center", width=width)

    # ───── Search ─────
    def filter_table(self, query):
        query = query.strip().lower()
        if not query:
            self.table.update_data(self.all_data)
            return

        filtered = []
        for row in self.all_data:
            if query in " ".join(str(x).lower() for x in row):
                filtered.append(row)

        self.table.update_data(filtered)

    # ───── Buttons actions ─────
    def open_add_form(self):
        AddCongeInterface(
            parent=self
        )

    def open_update_form(self):
        print("✏️ Modifier Congé cliqué")

    def delete_employe(self, row):
        print("🗑️ Delete:", row)

    def update_employe(self, row):
        print("📝 Update:", row)
