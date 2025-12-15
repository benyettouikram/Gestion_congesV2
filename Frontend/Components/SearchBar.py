# 📄 Frontend/Components/SearchBar.py
import tkinter as tk
from tkinter import ttk

class SearchBar(tk.Frame):
    def __init__(self, parent, on_search=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_search = on_search

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_change)

        # Champ de recherche
        self.entry = ttk.Entry(self, textvariable=self.search_var, width=30)
        self.entry.pack(side="left", padx=6, pady=5)

        # Bouton rechercher
        self.button = ttk.Button(self, text="🔍 بحث", command=self._call_search)
        self.button.pack(side="left", padx=5)

    def _on_change(self, *args):
        """Détection automatique quand le texte change (facultatif)"""
        if self.on_search:
            self.on_search(self.search_var.get())

    def _call_search(self):
        """Exécuté quand on clique sur le bouton"""
        if self.on_search:
            self.on_search(self.search_var.get())
