import tkinter as tk
from tkinter import messagebox
from Frontend.Components.DataTable import DataTable
from Frontend.Components.SearchBar import SearchBar
from Frontend.Components.Button.UpdateButton import Update_button
from Frontend.Components.Button.AddButton import AddButton

# ── DB helpers ───────────────────────────────────────────────────────────────
from Bakend.models.Conges.Dou import (
    get_employes_data,
    get_employe_by_id,
    get_conge_by_employe_id,
    get_multiple_employees_pdf_Ar_data,   # Arabic  data fetcher
    get_multiple_employees_pdf_fr_data,   # French  data fetcher
)

# ── PDF generators ────────────────────────────────────────────────────────────
from Frontend.Views.Pdf_Template.Pdf_AR import generate_conge_pdf_by_residence as generate_pdf_ar
from Frontend.Views.Pdf_Template.Pdf_Fr import generate_conge_pdf_fr_by_residence as generate_pdf_fr

# ── Other imports ─────────────────────────────────────────────────────────────
from Frontend.Views.Conges.Dou.Add_Dou import AddCongeInterface
from Bakend.models.Conges.Delet_dou_conge import clear_conge_data
from Frontend.Utils.event_bus import subscribe
from typing import List, Dict
from collections import defaultdict


class ResidenceDou(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        self.current_filter_query = ""
        self.print_language = tk.StringVar(value="ar")   # "ar" | "fr"

        # ── Page title ────────────────────────────────────────────────────────
        tk.Label(self, text="مديرية الخدمات الجامعية",
                 font=("Arial", 28, "bold"),
                 bg="white", fg="#2C3E50").pack(pady=20)
        tk.Label(self,
                 text="مرحبا بك في صفحة مديرية الخدمات الجامعية. يمكنك إدارة الموظفين من هنا.",
                 font=("Arial", 16), bg="white", fg="#555").pack(pady=5)

        # ── Top bar ───────────────────────────────────────────────────────────
        top_frame = tk.Frame(self, bg="#F5F6FA")
        top_frame.pack(fill="x", padx=20, pady=(0, 5))

        self.search_bar = SearchBar(top_frame, on_search=self.filter_table)
        self.search_bar.pack(side="left", fill="x", expand=True)

        buttons_frame = tk.Frame(top_frame, bg="#F5F6FA")
        buttons_frame.pack(side="right")

        # ── Language selector ─────────────────────────────────────────────────
        lang_frame = tk.Frame(buttons_frame, bg="#F5F6FA")
        lang_frame.pack(side="left", padx=10)

        tk.Label(lang_frame, text="اللغة:", font=("Arial", 11),
                 bg="#F5F6FA").pack(side="left", padx=2)

        lang_selector = tk.Frame(lang_frame, bg="white", relief="solid", borderwidth=1)
        lang_selector.pack(side="left")

        tk.Radiobutton(lang_selector, text="AR",
                       variable=self.print_language, value="ar",
                       font=("Arial", 10), bg="white",
                       activebackground="#E8F4F8",
                       selectcolor="#EAF5EA").pack(side="left", padx=7)

        tk.Radiobutton(lang_selector, text="FR",
                       variable=self.print_language, value="fr",
                       font=("Arial", 10), bg="white",
                       activebackground="#E8F4F8",
                       selectcolor="#FDFEFD").pack(side="left", padx=7)

        # ── Action buttons ────────────────────────────────────────────────────
        self.print_btn = AddButton(buttons_frame, text=" طباعة 🖨️",
                                   command=self.print_selected)
        self.print_btn.pack(side="left", padx=5)

        self.add_btn = AddButton(buttons_frame, text=" إضافة عطلة➕",
                                 command=self.open_add_form)
        self.add_btn.pack(side="left", padx=5)

        self.update_btn = Update_button(buttons_frame, text=" تعديل ✏️",
                                        command=self.open_update_form)
        self.update_btn.pack(side="left", padx=5)

        # ── Table ─────────────────────────────────────────────────────────────
        table_container = tk.Frame(self, bg="white")
        table_container.pack(fill="both", expand=True, pady=5)

        self.columns = (
            "Action", "nouveau_reste", "jours_pris", "date_fin",
            "date_debut", "ancien_conges", "grade",
            "nom_prenom", "departement", "id_employe"
        )

        self.all_data = get_employes_data()

        self.table = DataTable(
            table_container,
            self.columns,
            self.all_data,
            on_delete=self.delete_employe,
            enable_checkboxes=True
        )
        self.table.pack(fill="both", expand=True)

        # Subscribe to global events
        for event in ("employe_added", "conge_saved"):
            try:
                subscribe(event, lambda *a, **k: self._on_external_employe_added())
            except Exception:
                pass

        # ── Column headers ────────────────────────────────────────────────────
        headers = [
            ("Action",        "الإجراء",         120),
            ("nouveau_reste", "الرصيد الجديد",   130),
            ("jours_pris",    "الأيام المأخوذة", 150),
            ("date_fin",      "نهاية آخر عطلة",  150),
            ("date_debut",    "بداية آخر عطلة",  150),
            ("ancien_conges", "العطلة القديمة",  200),
            ("grade",         "الرتبة",           150),
            ("nom_prenom",    "الاسم و اللقب",   150),
            ("departement",   "القسم",             80),
            ("id_employe",    "",                   0),
            ("☑",             "☑",                50),
        ]
        for col, title, width in headers:
            self.table.tree.heading(col, text=title, anchor="center")
            self.table.tree.column(col, anchor="center",
                                   width=width, stretch=(width != 0))

    # =========================================================================
    #  PRINT SELECTED  –  bilingual
    # =========================================================================

    def print_selected(self):
        """
        Generates leave PDFs for all checked employees.

        Language radio-button:
          AR → get_multiple_employees_pdf_Ar_data  → generate_pdf_ar  → Arabic PDF
          FR → get_multiple_employees_pdf_fr_data  → generate_pdf_fr  → French PDF

        id_employe is at index 9 in the reordered tuple from get_employes_data().
        """
        selected_rows = self.table.get_selected_rows()

        if not selected_rows:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف واحد على الأقل")
            return

        language  = self.print_language.get()          # "ar" or "fr"
        lang_text = "العربية" if language == "ar" else "الفرنسية"
        count     = len(selected_rows)

        confirm = messagebox.askyesno(
            "تأكيد الطباعة",
            f"سيتم طباعة {count} وثيقة باللغة {lang_text}\n\nهل تريد المتابعة؟"
        )
        if not confirm:
            return

        try:
            # id_employe is the LAST item in each row tuple (index 9)
            employee_ids = [row[9] for row in selected_rows]

            # ── Choose fetcher based on language ─────────────────────────────
            if language == "ar":
                employees_data = get_multiple_employees_pdf_Ar_data(employee_ids)
                generate_pdf   = generate_pdf_ar
            else:
                employees_data = get_multiple_employees_pdf_fr_data(employee_ids)
                generate_pdf   = generate_pdf_fr

            if not employees_data:
                messagebox.showwarning(
                    "تنبيه",
                    "لم يتم العثور على بيانات للموظفين المحددين"
                )
                return

            # ── Group by residence, one PDF per group ─────────────────────────
            grouped = self._group_by_residence(employees_data)
            print(f"📊 {len(grouped)} résidence(s) – langue : {language.upper()}")

            generated_pdfs = []

            for residence, employees in grouped.items():
                print(f"\n🏢 {residence}  ({len(employees)} employé(s))  [{language.upper()}]")

                pdf_path = generate_pdf(
                    employees_data = employees,
                    residence_name = residence,
                    output_dir     = None,    # Desktop by default
                    signature_path = None,    # auto-search
                    auto_open      = True,
                )

                if pdf_path:
                    generated_pdfs.append(pdf_path)

            # ── Summary ───────────────────────────────────────────────────────
            total_pages = len(employees_data)
            total_pdfs  = len(generated_pdfs)

            messagebox.showinfo(
                "نجح",
                f"تم إنشاء {total_pdfs} وثيقة PDF بنجاح\n"
                f"إجمالي الصفحات: {total_pages}\n"
                f"المقر: {', '.join(grouped.keys())}"
            )

            print(f"\n✅ Terminé — {total_pdfs} PDF(s), {total_pages} page(s)")

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إنشاء الوثائق:\n{e}")
            import traceback
            print(f"❌ {e}")
            traceback.print_exc()

    # =========================================================================
    #  HELPERS
    # =========================================================================

    def _group_by_residence(self, employees_data: List[Dict]) -> Dict[str, List[Dict]]:
        grouped = defaultdict(list)
        for emp in employees_data:
            grouped[emp.get("residence", "Non spécifié")].append(emp)
        return dict(grouped)

    def filter_table(self, query):
        query = query.strip().lower()
        self.current_filter_query = query
        if not query:
            self.table.update_data(self.all_data)
            return
        filtered = [
            row for row in self.all_data
            if query in " ".join(str(x).lower() for x in row)
        ]
        self.table.update_data(filtered)

    def clear_filter(self):
        self.current_filter_query = ""
        self.search_bar.clear()
        self.table.update_data(self.all_data)

    # ── Add / Update / Delete ─────────────────────────────────────────────────

    def open_add_form(self):
        selected = self.table.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف من الجدول أولا")
            return

        employe_id_str = self.table.tree.set(selected[0], "id_employe")
        try:
            employe_id = int(employe_id_str)
        except Exception:
            messagebox.showerror("خطأ", "معرّف الموظف غير صالح")
            return

        employe = get_employe_by_id(employe_id)
        if not employe:
            messagebox.showerror("خطأ", "الموظف غير موجود في قاعدة البيانات")
            return

        if isinstance(employe, tuple):
            employe = {
                "id_employe": employe_id,
                "nom":    employe[1] if len(employe) > 1 else "غير معروف",
                "prenom": employe[2] if len(employe) > 2 else "غير معروف",
                "grade":  employe[3] if len(employe) > 3 else "غير معروف",
            }
        else:
            employe["id_employe"] = employe_id

        AddCongeInterface(self, employe=employe, on_save_callback=self.refresh_data)

    def delete_employe(self, row):
        employe_id = row[9]   # id_employe at index 9
        confirm = messagebox.askyesno(
            "تأكيد الحذف",
            f"هل تريد حذف بيانات الإجازة للموظف رقم {employe_id}؟\n"
            "(الموظف سيبقى في القاعدة)"
        )
        if confirm:
            if clear_conge_data(employe_id):
                messagebox.showinfo("نجح", "تم حذف بيانات الإجازة بنجاح")
                self.refresh_data()
            else:
                messagebox.showerror("خطأ", "فشل حذف بيانات الإجازة")

    def open_update_form(self):
        selected = self.table.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف من الجدول أولا")
            return

        employe_id_str = self.table.tree.set(selected[0], "id_employe")
        try:
            employe_id = int(employe_id_str)
        except Exception:
            messagebox.showerror("خطأ", "معرّف الموظف غير صالح")
            return

        employe = get_employe_by_id(employe_id)
        if not employe:
            messagebox.showerror("خطأ", "الموظف غير موجود في قاعدة البيانات")
            return

        conge_data = get_conge_by_employe_id(employe_id)
        if not conge_data:
            messagebox.showwarning("تنبيه", "هذا الموظف ليس لديه عطلة لتعديلها")
            return

        if isinstance(employe, tuple):
            employe = {
                "id_employe": employe_id,
                "nom":    employe[1] if len(employe) > 1 else "غير معروف",
                "prenom": employe[2] if len(employe) > 2 else "غير معروف",
                "grade":  employe[3] if len(employe) > 3 else "غير معروف",
            }
        else:
            employe["id_employe"] = employe_id

        AddCongeInterface(self, employe=employe,
                          conge_data=conge_data,
                          on_save_callback=self.refresh_data)

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh_data(self):
        self.all_data = get_employes_data()
        if self.current_filter_query:
            self.filter_table(self.current_filter_query)
        else:
            self.table.update_data(self.all_data)

    def _on_external_employe_added(self):
        self.all_data = get_employes_data()
        if self.current_filter_query:
            self.filter_table(self.current_filter_query)
        else:
            self.table.update_data(self.all_data)