"""
Frontend/Pages/Historique.py
─────────────────────────────
السجل screen — columns now match the RTL DataTable display order.

Column order (left→right on screen):
    المعرف | الاسم و اللقب | الرتبة | تاريخ الميلاد | عدد الأيام | السنة | الإجراء

Tuple index mapping:
    0 → id_employe       (المعرف)
    1 → employe_complet  (الاسم و اللقب)
    2 → grade            (الرتبة)
    3 → date_naissance   (تاريخ الميلاد)
    4 → nb_jours         (عدد الأيام)
    5 → annee            (السنة)
    6 → action           (الإجراء)
"""

import tkinter as tk
from tkinter import messagebox

from Frontend.Components.DataTable import DataTable
from Frontend.Components.SearchBar import SearchBar

from Bakend.models.Conges.Generichistorique import (
    get_historique_data,
    search_historique,
)


class Historique(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F2F4F7")

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

        # ── Columns — order matches screen left→right ──────────────────────
        self.columns = (
            "id",            # 0 → المعرف
            "الاسم و اللقب", # 1
            "الرتبة",        # 2
            "تاريخ الميلاد", # 3
            "عدد الأيام",    # 4
            "السنة",         # 5
            "Action",        # 6 → الإجراء
        )

        # ── DataTable ──────────────────────────────────────────────────────
        self.table = DataTable(
            self,
            self.columns,
            get_historique_data(),
            on_delete=self.view_details,
        )
        self.table.pack(fill="both", expand=True, padx=20, pady=10)

        # ── Column headers & widths ────────────────────────────────────────
        headers = [
            ("id",           "المعرف",         80),
            ("الاسم و اللقب", "الاسم و اللقب",  200),
            ("الرتبة",        "الرتبة",         120),
            ("تاريخ الميلاد", "تاريخ الميلاد",  130),
            ("عدد الأيام",    "عدد الأيام",     100),
            ("السنة",         "السنة",          80),
            ("Action",       "الإجراء",        120),
        ]
        for col, title_text, width in headers:
            self.table.tree.heading(col, text=title_text, anchor="e")
            self.table.tree.column(col, anchor="e", width=width)

    # ── public methods ─────────────────────────────────────────────────────

    def refresh(self):
        """Reload from DB — call after any congé insert/update/delete."""
        self.table.update_data(get_historique_data())

    def filter_data(self, search_text=None):
        if search_text and search_text.strip():
            self.table.update_data(search_historique(search_text))
        else:
            self.table.update_data(get_historique_data())

    def view_details(self, row):
        if not row:
            return
        messagebox.showinfo("تفاصيل السجل", (
            f"تفاصيل السجل\n"
            f"───────────────\n"
            f"المعرف: {row[0]}\n"
            f"الموظف: {row[1]}\n"
            f"الرتبة: {row[2]}\n"
            f"تاريخ الميلاد: {row[3]}\n"
            f"عدد الأيام: {row[4]}\n"
            f"السنة: {row[5]}\n"
            f"الإجراء: {row[6]}"
        ))