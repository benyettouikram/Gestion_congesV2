import tkinter as tk
from tkinter import messagebox, Toplevel

from Frontend.Components.DataTable import DataTable
from Frontend.Components.SearchBar import SearchBar
from Frontend.Components.Button.AddButton import AddButton
from Frontend.Views.Employes.Add_employer import AddEmployePage
from Bakend.models.Employer.get_employer import get_employes_data
from Bakend.models.Employer.Search import search_employes
from Bakend.models.Employer.Delete_employer import delete_employe_by_id
#from Bakend.models.Employer.Update.Update_employe import update_employe
from Frontend.Views.Employes.Update_employer import UpdateEmployePage
from Bakend.models.Employer.Update.Get_employer_by_id import get_employe_by_id
class EmployesPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F5F6FA")

        title = tk.Label(self, text="قائمة الموظفين", font=("Segoe UI Semibold", 18), bg="#F5F6FA", fg="#2E7D32")
        title.pack(pady=10)

        top_frame = tk.Frame(self, bg="#F5F6FA")
        top_frame.pack(fill="x", padx=20, pady=(0,10))

        self.search_bar = SearchBar(top_frame, on_search=self.filter_data)
        self.search_bar.pack(side="left", fill="x", expand=True)

        self.add_button = AddButton(top_frame, text="إضافة موظف ➕", command=self.open_add_form)
        self.add_button.pack(side="right", padx=5)

        self.columns = ("Action","ancien_conges","poste_superieur","grade","date_naissance",
                        "nom_prenom","departement","residence","id")
        self.all_data = get_employes_data()

        self.table = DataTable(self, self.columns, self.all_data, on_delete=self.delete_employe, on_update=self.update_employe)
        self.table.pack(fill="both", expand=True, padx=20, pady=10)

        headers = [
            ("Action", "الإجراء", 100),
            ("ancien_conges", "العطلة القديمة", 130),
            ("poste_superieur", "المنصب الأعلى", 150),
            ("grade", "الرتبة", 120),
            ("date_naissance", "تاريخ الميلاد", 130),
            ("nom_prenom", "الاسم و اللقب", 200),
            ("departement", "القسم", 150),
            ("residence", "مكان الإقامة", 150),
            ("id", "المعرف", 80)
        ]

        for col, title_text, width in headers:
            self.table.tree.heading(col, text=title_text, anchor="e")
            self.table.tree.column(col, anchor="e", width=width)

    def filter_data(self, search_text=None):
        data = search_employes(search_text or "")
        self.table.update_data(data)

    def open_add_form(self):
        add_window = Toplevel(self)
        add_window.title("إضافة موظف جديد / Ajouter un employé")
        add_window.geometry("700x800")
        add_window.configure(bg="#F5F6FA")
        form = AddEmployePage(add_window, on_success=self.refresh_data)
        form.pack(fill="both", expand=True)

    def refresh_data(self):
        self.all_data = get_employes_data()
        self.table.update_data(self.all_data)

    def delete_employe(self, row):
        employe_id = row[-1]
        confirm = messagebox.askyesno("تأكيد الحذف", f"هل تريد حذف الموظف رقم {employe_id}؟")
        if confirm:
            delete_employe_by_id(employe_id)
            self.refresh_data()

    def update_employe(self, row):
        """
        ✅ FIXED: Get employee ID from row, then fetch COMPLETE data from database
        """
        employe_id = row[-1]  # Get the ID from the last column
        
        # ✅ Fetch complete data from database
        employe_data = get_employe_by_id(employe_id)
        
        if not employe_data:
            messagebox.showerror("خطأ / Erreur", f"لم يتم العثور على الموظف رقم {employe_id}")
            return

        # Open a new Toplevel window
        update_window = Toplevel(self)
        update_window.title("تحديث بيانات الموظف")
        update_window.geometry("700x800")
        update_window.configure(bg="#F5F6FA")

        # Use the standalone UpdateEmployePage with COMPLETE data from DB
        form = UpdateEmployePage(update_window, employe_data=employe_data, on_success=self.on_update_success)
        form.pack(fill="both", expand=True)

    def on_update_success(self):
        """Called after successful update to refresh and close window"""
        self.refresh_data()