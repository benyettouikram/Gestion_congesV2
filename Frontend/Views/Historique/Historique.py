"""
Frontend/Pages/Historique.py
"""

import tkinter as tk
from tkinter import messagebox

from Frontend.Components.DataTable import DataTable
from Frontend.Components.SearchBar import SearchBar

from Bakend.models.Conges.Generichistorique import (
    get_historique_data,
    search_historique,
    delete_historique,
    init_db,
)


COLUMNS = (
    "Action",
    "nouveau_reste",
    "annee",
    "nb_jours",
    "grade",
    "date_naissance",
    "nom_prenom",
    "id_employe",
    "id_historique",
)

HEADERS = [
    ("Action",         "الإجراء",         120),
    ("nouveau_reste",  "الرصيد المتبقي",  130),
    ("annee",          "السنة",            80),
    ("nb_jours",       "عدد الأيام",      100),
    ("grade",          "الرتبة",          120),
    ("date_naissance", "تاريخ الميلاد",   130),
    ("nom_prenom",     "الاسم و اللقب",   200),
    ("id_employe",     "",                  0),
    ("id_historique",  "",                  0),
]


class Historique(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F2F4F7")

        # ── Ensure triggers exist every time this page opens ───────────────
        init_db()

        # ── Title ──────────────────────────────────────────────────────────
        tk.Label(
            self,
            text="السجل",
            font=("Segoe UI Semibold", 18),
            bg="#F5F6FA",
            fg="#2E7D32",
        ).pack(pady=10)

        # ── Top bar ────────────────────────────────────────────────────────
        top_frame = tk.Frame(self, bg="#F5F6FA")
        top_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.search_bar = SearchBar(top_frame, on_search=self.filter_data)
        self.search_bar.pack(side="left", fill="x", expand=True)

        tk.Button(
            top_frame,
            text="↻ تحديث",
            font=("Segoe UI", 10),
            bg="#2E7D32",
            fg="white",
            relief="flat",
            padx=10,
            command=self.refresh,
        ).pack(side="right", padx=(10, 0))

        # ── DataTable ──────────────────────────────────────────────────────
        self.table = DataTable(
            self,
            COLUMNS,
            get_historique_data(),
            on_delete=self.delete_row,
        )
        self.table.pack(fill="both", expand=True, padx=20, pady=10)

        for col, title_text, width in HEADERS:
            self.table.tree.heading(col, text=title_text, anchor="e")
            self.table.tree.column(
                col,
                anchor="e",
                width=width,
                minwidth=0 if width == 0 else 20,
                stretch=width != 0,
            )

    # ── public methods ─────────────────────────────────────────────────────

    def refresh(self):
        self.table.update_data(get_historique_data())

    def filter_data(self, search_text=None):
        if search_text and search_text.strip():
            self.table.update_data(search_historique(search_text))
        else:
            self.table.update_data(get_historique_data())

    def delete_row(self, row):
        if not row:
            return

        try:
            id_hist = int(row[8])
        except (ValueError, IndexError):
            messagebox.showerror("خطأ", f"لم يتم العثور على معرف السجل.\n{row}")
            return

        confirm = messagebox.askyesno(
            "تأكيد الحذف",
            f"هل تريد حذف سجل الموظف:\n{row[6]}؟"
        )
        if not confirm:
            return

        delete_historique(id_hist)
        self.refresh()