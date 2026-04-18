"""
Frontend/Pages/Historique.py
─────────────────────────────
السجل screen — corrected version.

Changes vs original
───────────────────
1. Import fixed — uses GenericHistorique, not GenericConge.
2. view_details() indices corrected to match DataTable column order.
3. refresh() added so the caller (main window / notebook) can reload
   the table whenever a congé is added, updated, or deleted from
   another tab. Call:
       historique_frame.refresh()
"""

import tkinter as tk
from tkinter import messagebox

from Frontend.Components.DataTable import DataTable
from Frontend.Components.SearchBar import SearchBar

# ✅ correct import
from Bakend.models.Conges.Generichistorique import (
    get_historique_data,
    search_historique,
)


class Historique(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F2F4F7")

        # ── Title ──────────────────────────────────────────────────────────
        title = tk.Label(
            self,
            text="السجل",
            font=("Segoe UI Semibold", 18),
            bg="#F5F6FA",
            fg="#2E7D32",
        )
        title.pack(pady=10)

        # ── Top frame — search bar ─────────────────────────────────────────
        top_frame = tk.Frame(self, bg="#F5F6FA")
        top_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.search_bar = SearchBar(top_frame, on_search=self.filter_data)
        self.search_bar.pack(side="left", fill="x", expand=True)

        # ── Refresh button (manual reload) ─────────────────────────────────
        refresh_btn = tk.Button(
            top_frame,
            text="↻ تحديث",
            font=("Segoe UI", 10),
            bg="#2E7D32",
            fg="white",
            relief="flat",
            padx=10,
            command=self.refresh,
        )
        refresh_btn.pack(side="right", padx=(10, 0))

        # ── Column definitions — ORDER MUST MATCH backend tuple ────────────
        #   index 0 → action          (الإجراء)
        #   index 1 → annee           (السنة)
        #   index 2 → nb_jours        (عدد الأيام)
        #   index 3 → date_naissance  (تاريخ الميلاد)
        #   index 4 → grade           (الرتبة)
        #   index 5 → employe_complet (الاسم و اللقب)
        #   index 6 → id_employe      (المعرف)
        self.columns = (
            "Action",
            "السنة",
            "عدد الأيام",
            "تاريخ الميلاد",
            "الرتبة",
            "الاسم و اللقب",
            "id",
        )

        # ── Initial data load ──────────────────────────────────────────────
        self.all_data = get_historique_data()

        # ── DataTable ──────────────────────────────────────────────────────
        self.table = DataTable(
            self,
            self.columns,
            self.all_data,
            on_delete=self.view_details,
        )
        self.table.pack(fill="both", expand=True, padx=20, pady=10)

        # ── Column headers & widths ────────────────────────────────────────
        headers = [
            ("Action",       "الإجراء",       100),
            ("السنة",         "السنة",          80),
            ("عدد الأيام",    "عدد الأيام",     100),
            ("تاريخ الميلاد", "تاريخ الميلاد",  130),
            ("الرتبة",        "الرتبة",         100),
            ("الاسم و اللقب", "الاسم و اللقب",  200),
            ("id",           "المعرف",          80),
        ]
        for col, title_text, width in headers:
            self.table.tree.heading(col, text=title_text, anchor="e")
            self.table.tree.column(col, anchor="e", width=width)

    # ── refresh ────────────────────────────────────────────────────────────

    def refresh(self):
        """
        Reload all historique data from the database.
        Call this from any other tab after insert / update / delete:

            self.historique_tab.refresh()
        """
        data = get_historique_data()
        self.table.update_data(data)

    # ── filter_data ────────────────────────────────────────────────────────

    def filter_data(self, search_text=None):
        """Filter rows based on search text."""
        if search_text and search_text.strip():
            data = search_historique(search_text)
        else:
            data = get_historique_data()
        self.table.update_data(data)

    # ── view_details ───────────────────────────────────────────────────────

    def view_details(self, row):
        """
        Show a details popup for the selected historique row.

        ✅ Indices match the DataTable column order defined above:
            row[0] → action
            row[1] → annee
            row[2] → nb_jours
            row[3] → date_naissance
            row[4] → grade
            row[5] → employe_complet
            row[6] → id_employe
        """
        if not row:
            return

        action          = row[0]
        annee           = row[1]
        nb_jours        = row[2]
        date_naissance  = row[3]
        grade           = row[4]
        employe_complet = row[5]
        id_employe      = row[6]

        details_msg = (
            f"تفاصيل السجل\n"
            f"───────────────\n"
            f"الموظف: {employe_complet}\n"
            f"الرتبة: {grade}\n"
            f"تاريخ الميلاد: {date_naissance}\n"
            f"الإجراء: {action}\n"
            f"عدد الأيام: {nb_jours}\n"
            f"السنة: {annee}\n"
            f"المعرف: {id_employe}"
        )
        messagebox.showinfo("تفاصيل السجل", details_msg)