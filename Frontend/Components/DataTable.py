import tkinter as tk
from tkinter import ttk, messagebox

from Frontend.Theme.colors import (
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    CARD_BACKGROUND,
    BORDER_COLOR,
    HIGHLIGHT_COLOR,
    Heading_table_color,
)

class DataTable(ttk.Frame):
    def __init__(self, parent, columns, data=None, on_delete=None, on_update=None, enable_checkboxes=False):
        """
        DataTable avec support optionnel des checkboxes
        
        Args:
            enable_checkboxes (bool): Si True, ajoute une colonne de checkboxes
        """
        super().__init__(parent)

        self.original_columns = list(columns)  # ✅ Store original columns
        self.columns = list(columns)
        self.data = data or []
        self.on_delete = on_delete
        self.on_update = on_update
        self.enable_checkboxes = enable_checkboxes
        
        # ✅ Dictionnaire pour stocker l'état des checkboxes
        self.checked_items = {}  # {row_id: True/False}

        self.style = ttk.Style()
        self._configure_style()

        # Container
        container = ttk.Frame(self, style="Card.TFrame")
        container.pack(fill="both", expand=True)

        # ✅ Ajouter une colonne checkbox si activé (à la fin)
        if self.enable_checkboxes:
            self.columns = self.columns + ["☑"]

        # Treeview
        self.tree = ttk.Treeview(
            container,
            columns=self.columns,
            show="headings",
            style="Modern.Treeview",
            selectmode="browse",
        )
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Columns configuration
        for col in self.columns:
            if col == "☑":
                self.tree.heading(col, text="☑", anchor="center", command=self._toggle_all)
                self.tree.column(col, anchor="center", width=50, stretch=False)
            else:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=130)

        # Load data
        self.load_data(self.data)

        # Bind events
        self.tree.bind("<Button-1>", self._handle_click)
        self.tree.bind("<Double-1>", self._handle_double_click)

    def _configure_style(self):
        self.style.theme_use("clam")
        self.style.configure("Card.TFrame", background=CARD_BACKGROUND, relief="groove", borderwidth=1)
        self.style.configure(
            "Modern.Treeview",
            background=CARD_BACKGROUND,
            foreground="#333",
            rowheight=32,
            fieldbackground=CARD_BACKGROUND,
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "Modern.Treeview.Heading",
            background=Heading_table_color,
            foreground="#000",
            font=("Segoe UI Semibold", 10)
        )
        self.style.map("Modern.Treeview", background=[("selected", HIGHLIGHT_COLOR)])

    def load_data(self, data):
        """Charge les données dans le tableau"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.checked_items.clear()

        for item in data:
            item = list(item)
            
            # Ajouter la colonne Action si elle existe
            if "Action" in self.columns:
                action_index = self.columns.index("Action")
                item.insert(action_index, "❌")
            else:
                item.append("❌")
            
            # ✅ Ajouter checkbox non cochée si activé (à la fin)
            if self.enable_checkboxes:
                item.append("☐")
            
            row_id = self.tree.insert("", "end", values=item)
            self.checked_items[row_id] = False

    def _handle_click(self, event):
        """Gère les clics sur le tableau"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            col_index = int(self.tree.identify_column(event.x).replace("#", "")) - 1
            row_id = self.tree.identify_row(event.y)
            
            if not row_id:
                return
            
            # ✅ IMPORTANT: Get the column name from self.columns
            clicked_column = self.columns[col_index]
            
            # ✅ Gérer le clic sur checkbox
            if self.enable_checkboxes and clicked_column == "☑":
                self._toggle_checkbox(row_id)
                return
            
            # ✅ Gérer le clic sur Action (delete button)
            if clicked_column == "Action":
                if self.on_delete:
                    values = list(self.tree.item(row_id, "values"))
                    # ✅ Remove checkbox value before passing to delete callback
                    if self.enable_checkboxes:
                        values = values[:-1]  # Remove the checkbox (last element)
                    self.on_delete(values)

    def _toggle_checkbox(self, row_id):
        """Basculer l'état d'une checkbox"""
        values = list(self.tree.item(row_id, "values"))
        current_state = self.checked_items.get(row_id, False)
        new_state = not current_state
        
        self.checked_items[row_id] = new_state
        values[-1] = "☑" if new_state else "☐"
        self.tree.item(row_id, values=values)

    def _toggle_all(self):
        """Basculer toutes les checkboxes (Select All / Deselect All)"""
        if not self.enable_checkboxes:
            return
        
        # Vérifier si au moins une case est cochée
        any_checked = any(self.checked_items.values())
        new_state = not any_checked
        
        for row_id in self.tree.get_children():
            values = list(self.tree.item(row_id, "values"))
            self.checked_items[row_id] = new_state
            values[-1] = "☑" if new_state else "☐"
            self.tree.item(row_id, values=values)

    def get_selected_rows(self):
        """
        Retourne les données des lignes cochées
        Returns:
            list: Liste des valeurs des lignes cochées (sans la colonne checkbox)
        """
        selected = []
        for row_id in self.tree.get_children():
            if self.checked_items.get(row_id, False):
                values = list(self.tree.item(row_id, "values"))
                # Retirer la checkbox de la liste des valeurs (elle est à la fin)
                if self.enable_checkboxes:
                    values = values[:-1]
                selected.append(values)
        return selected

    def get_selected_count(self):
        """Retourne le nombre de lignes cochées"""
        return sum(1 for checked in self.checked_items.values() if checked)

    def _handle_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        values = list(self.tree.item(row_id, "values"))
        
        # Retirer la checkbox si présente (elle est à la fin)
        if self.enable_checkboxes:
            values = values[:-1]
        
        id_index = -1
        nom_prenom_index = 5
        
        employe_id = values[id_index]
        nom_prenom = values[nom_prenom_index] if len(values) > nom_prenom_index else "غير معروف"

        confirm = messagebox.askokcancel(
            "تحديث معلومات الموظف",
            f"هل تريد تعديل معلومات الموظف:\n\n👤 الاسم واللقب: {nom_prenom}\n🆔 المعرف: {employe_id}"
        )

        if confirm and self.on_update:
            self.on_update(values)

    def update_data(self, new_data):
        """Met à jour les données du tableau"""
        self.load_data(new_data)