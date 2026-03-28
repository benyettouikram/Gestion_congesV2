"""
Frontend/Views/Conges/ResidenceBase.py
──────────────────────────────────────
Generic base class for every residence page.

Subclasses only need to supply three values:

    class Residence19mai(ResidenceBase):
        def __init__(self, parent):
            super().__init__(
                parent,
                title         = "الإقامة الجامعية 19 ماي 1956",
                subtitle      = "مرحبا بك في صفحة إقامة 19 ماي.",
                residence_key = "mai1956",
            )

Available residence keys
────────────────────────
    dou        heni       tawil
    mai1956    nov1954
    oulad03    oulad04
    hasna1500  hasna2000  tenes500
"""

import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
from typing import List, Dict

from Frontend.Components.DataTable import DataTable
from Frontend.Components.SearchBar import SearchBar
from Frontend.Components.Button.UpdateButton import Update_button
from Frontend.Components.Button.AddButton import AddButton
from Frontend.Utils.event_bus import subscribe

# ── Generic backend (read) ─────────────────────────────────────────────────────
from Bakend.models.Conges.GenericResidence import (
    get_employes_data,
    get_employe_by_id,
    get_conge_by_employe_id,
    get_multiple_employees_pdf_Ar_data,
    get_multiple_employees_pdf_fr_data,
    resolve_residence_ar,           # short key → Arabic string
)

# ── Generic backend (write) ────────────────────────────────────────────────────
from Bakend.models.Conges.GenericConge import clear_conge_data

# ── Generic Add/Update dialog (shared by all residences) ──────────────────────
from Frontend.Views.Conges.GenericAddConge import GenericAddConge

# ── PDF generators ─────────────────────────────────────────────────────────────
from Frontend.Views.Pdf_Template.Pdf_AR import generate_conge_pdf_by_residence as generate_pdf_ar
from Frontend.Views.Pdf_Template.Pdf_Fr import generate_conge_pdf_fr_by_residence as generate_pdf_fr


class ResidenceBase(tk.Frame):
    """
    Base view shared by all 10 residences.
    Handles: display table, search, add, update, delete, PDF print.
    """

    COLUMNS = (
        "Action", "nouveau_reste", "jours_pris", "date_fin",
        "date_debut", "ancien_conges", "grade",
        "nom_prenom", "departement", "id_employe",
    )

    HEADERS = [
        ("Action",        "الإجراء",          120),
        ("nouveau_reste", "الرصيد الجديد",    130),
        ("jours_pris",    "الأيام المأخوذة",  150),
        ("date_fin",      "نهاية آخر عطلة",   150),
        ("date_debut",    "بداية آخر عطلة",   150),
        ("ancien_conges", "العطلة القديمة",   200),
        ("grade",         "الرتبة",            150),
        ("nom_prenom",    "الاسم و اللقب",    150),
        ("departement",   "القسم",              80),
        ("id_employe",    "",                    0),
        ("☑",             "☑",                 50),
    ]

    # =========================================================================

    def __init__(
        self,
        parent,
        title: str         = "الإقامة الجامعية",
        subtitle: str      = "مرحبا بك. يمكنك إدارة الموظفين من هنا.",
        residence_key: str = "dou",
    ):
        super().__init__(parent, bg="white")

        self.residence_key        = residence_key
        # ✅ Resolved once — used everywhere (add / update / delete)
        self.residence_ar         = resolve_residence_ar(residence_key)
        self.current_filter_query = ""
        self.print_language       = tk.StringVar(value="ar")

        # ── Page heading ──────────────────────────────────────────────────
        tk.Label(self, text=title, font=("Arial", 28, "bold"),
                 bg="white", fg="#2C3E50").pack(pady=20)
        tk.Label(self, text=subtitle, font=("Arial", 16),
                 bg="white", fg="#555").pack(pady=5)

        # ── Top bar ───────────────────────────────────────────────────────
        top_frame = tk.Frame(self, bg="#F5F6FA")
        top_frame.pack(fill="x", padx=20, pady=(0, 5))

        self.search_bar = SearchBar(top_frame, on_search=self.filter_table)
        self.search_bar.pack(side="left", fill="x", expand=True)

        buttons_frame = tk.Frame(top_frame, bg="#F5F6FA")
        buttons_frame.pack(side="right")

        # Language selector
        lang_frame = tk.Frame(buttons_frame, bg="#F5F6FA")
        lang_frame.pack(side="left", padx=10)
        tk.Label(lang_frame, text="اللغة:", font=("Arial", 11), bg="#F5F6FA").pack(side="left", padx=2)

        lang_selector = tk.Frame(lang_frame, bg="white", relief="solid", borderwidth=1)
        lang_selector.pack(side="left")
        tk.Radiobutton(lang_selector, text="AR", variable=self.print_language, value="ar",
                       font=("Arial", 10), bg="white",
                       activebackground="#E8F4F8", selectcolor="#EAF5EA").pack(side="left", padx=7)
        tk.Radiobutton(lang_selector, text="FR", variable=self.print_language, value="fr",
                       font=("Arial", 10), bg="white",
                       activebackground="#E8F4F8", selectcolor="#FDFEFD").pack(side="left", padx=7)

        # Action buttons
        AddButton(buttons_frame,    text=" طباعة 🖨️",      command=self.print_selected).pack(side="left", padx=5)
        AddButton(buttons_frame,    text=" إضافة عطلة➕",   command=self.open_add_form).pack(side="left", padx=5)
        Update_button(buttons_frame, text=" تعديل ✏️",      command=self.open_update_form).pack(side="left", padx=5)

        # ── Table ─────────────────────────────────────────────────────────
        table_container = tk.Frame(self, bg="white")
        table_container.pack(fill="both", expand=True, pady=5)

        self.all_data = self._fetch_data()
        self.table = DataTable(
            table_container, self.COLUMNS, self.all_data,
            on_delete=self.delete_employe, enable_checkboxes=True,
        )
        self.table.pack(fill="both", expand=True)

        for col, heading, width in self.HEADERS:
            self.table.tree.heading(col, text=heading, anchor="center")
            self.table.tree.column(col, anchor="center", width=width, stretch=(width != 0))

        # ── Event bus ─────────────────────────────────────────────────────
        for event in ("employe_added", "conge_saved"):
            try:
                subscribe(event, lambda *a, **k: self._on_external_change())
            except Exception:
                pass

    # =========================================================================
    #  DATA
    # =========================================================================

    def _fetch_data(self):
        """Load employees filtered by this residence."""
        return get_employes_data(self.residence_key)

    # =========================================================================
    #  PRINT
    # =========================================================================

    def print_selected(self):
        selected_rows = self.table.get_selected_rows()

        if not selected_rows:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف واحد على الأقل")
            return

        language  = self.print_language.get()
        lang_text = "العربية" if language == "ar" else "الفرنسية"

        if not messagebox.askyesno(
            "تأكيد الطباعة",
            f"سيتم طباعة {len(selected_rows)} وثيقة باللغة {lang_text}\n\nهل تريد المتابعة؟"
        ):
            return

        try:
            # ✅ THE FIX: id_employe is hidden (width=0) so get_selected_rows()
            # does NOT include it. We must read it by column name from the treeview.
            # We iterate ALL treeview items, and only keep the ones that are checked.
            employee_ids = []
            for item in self.table.tree.get_children():
                # Check if this item's checkbox is ticked
                try:
                    check_val = self.table.tree.set(item, "☑")
                    if check_val != "☑":
                        continue
                except Exception:
                    continue

                # Read id_employe by column name — safe, never shifts
                try:
                    value = self.table.tree.set(item, "id_employe")
                    if value and str(value).strip() not in ("", "—", "-", "None"):
                        employee_ids.append(int(value))
                except (ValueError, TypeError):
                    continue

            print(f"🖨️ IDs سélectionnés: {employee_ids}")

            if not employee_ids:
                messagebox.showwarning("تنبيه", "لم يتم العثور على معرّف الموظفين")
                return

            if language == "ar":
                employees_data = get_multiple_employees_pdf_Ar_data(employee_ids, self.residence_key)
                generate_pdf   = generate_pdf_ar
            else:
                employees_data = get_multiple_employees_pdf_fr_data(employee_ids, self.residence_key)
                generate_pdf   = generate_pdf_fr

            if not employees_data:
                messagebox.showwarning("تنبيه", "لم يتم العثور على بيانات للموظفين المحددين")
                return

            grouped        = self._group_by_residence(employees_data)
            generated_pdfs = []

            for residence, employees in grouped.items():
                pdf_path = generate_pdf(
                    employees_data = employees,
                    residence_name = residence,
                    output_dir     = None,
                    signature_path = None,
                    auto_open      = True,
                )
                if pdf_path:
                    generated_pdfs.append(pdf_path)

            messagebox.showinfo(
                "نجح",
                f"تم إنشاء {len(generated_pdfs)} وثيقة PDF بنجاح\n"
                f"إجمالي الصفحات: {len(employees_data)}\n"
                f"المقر: {', '.join(grouped.keys())}"
            )

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إنشاء الوثائق:\n{e}")
            import traceback; traceback.print_exc()

    def _group_by_residence(self, employees_data: List[Dict]) -> Dict[str, List[Dict]]:
        grouped = defaultdict(list)
        for emp in employees_data:
            grouped[emp.get("residence", "Non spécifié")].append(emp)
        return dict(grouped)

    # =========================================================================
    #  FILTER
    # =========================================================================

    def filter_table(self, query: str):
        query = query.strip().lower()
        self.current_filter_query = query
        filtered = (self.all_data if not query
                    else [r for r in self.all_data
                          if query in " ".join(str(x).lower() for x in r)])
        self.table.update_data(filtered)

    def clear_filter(self):
        self.current_filter_query = ""
        self.search_bar.clear()
        self.table.update_data(self.all_data)

    # =========================================================================
    #  ADD / UPDATE / DELETE
    # =========================================================================

    def _resolve_employe(self, employe_id: int):
        employe = get_employe_by_id(employe_id, self.residence_key)
        if not employe:
            return None
        if isinstance(employe, tuple):
            return {
                "id_employe": employe_id,
                "nom":    employe[1] if len(employe) > 1 else "غير معروف",
                "prenom": employe[2] if len(employe) > 2 else "غير معروف",
                "grade":  employe[3] if len(employe) > 3 else "غير معروف",
            }
        employe["id_employe"] = employe_id
        return employe

    def _selected_employe_id(self):
        selected = self.table.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف من الجدول أولا")
            return None
        try:
            return int(self.table.tree.set(selected[0], "id_employe"))
        except Exception:
            messagebox.showerror("خطأ", "معرّف الموظف غير صالح")
            return None

    def open_add_form(self):
        employe_id = self._selected_employe_id()
        if employe_id is None:
            return
        employe = self._resolve_employe(employe_id)
        if not employe:
            messagebox.showerror("خطأ", "الموظف غير موجود في قاعدة البيانات")
            return
        # ✅ Pass the Arabic residence so insert_conge verifies the right residence
        GenericAddConge(
            self,
            employe            = employe,
            on_save_callback   = self.refresh_data,
            residence_required = self.residence_ar,   # ← dynamic
        )

    def open_update_form(self):
        employe_id = self._selected_employe_id()
        if employe_id is None:
            return
        employe = self._resolve_employe(employe_id)
        if not employe:
            messagebox.showerror("خطأ", "الموظف غير موجود في قاعدة البيانات")
            return
        conge_data = get_conge_by_employe_id(employe_id)
        if not conge_data:
            messagebox.showwarning("تنبيه", "هذا الموظف ليس لديه عطلة لتعديلها")
            return
        GenericAddConge(
            self,
            employe            = employe,
            conge_data         = conge_data,
            on_save_callback   = self.refresh_data,
            residence_required = self.residence_ar,   # ← dynamic
        )

    def delete_employe(self, row):
        """
        ✅ Reads id_employe by COLUMN NAME from the treeview.
        This bypasses any row tuple index confusion entirely.
        """
        # ── Get id_employe safely by column name ──────────────────────────
        selected = self.table.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف من الجدول أولا")
            return

        try:
            value = self.table.tree.set(selected[0], "id_employe")
            if not value or str(value).strip() in ("", "—", "-", "None"):
                messagebox.showerror("خطأ", "لم يتم العثور على معرّف الموظف")
                return
            employe_id = int(value)
        except (ValueError, TypeError) as e:
            messagebox.showerror("خطأ", f"معرّف الموظف غير صالح: {e}")
            return

        # ── Confirm ───────────────────────────────────────────────────────
        if not messagebox.askyesno(
            "تأكيد الحذف",
            f"هل تريد حذف بيانات الإجازة للموظف رقم {employe_id}؟\n"
            f"(الموظف سيبقى في القاعدة)"
        ):
            return

        # ✅ Pass self.residence_ar so the check works for ALL residences
        if clear_conge_data(employe_id, residence_required=self.residence_ar):
            messagebox.showinfo("نجح", "تم حذف بيانات الإجازة بنجاح")
            self.refresh_data()
        else:
            messagebox.showerror("خطأ", "فشل حذف بيانات الإجازة")

    # =========================================================================
    #  REFRESH
    # =========================================================================

    def refresh_data(self):
        self.all_data = self._fetch_data()
        self.filter_table(self.current_filter_query)

    def _on_external_change(self):
        self.refresh_data()