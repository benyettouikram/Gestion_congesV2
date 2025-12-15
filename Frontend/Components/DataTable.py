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
    def __init__(self, parent, columns, data=None, on_delete=None, on_update=None):
        super().__init__(parent)

        self.columns = list(columns)
        self.data = data or []
        self.on_delete = on_delete
        self.on_update = on_update

        self.style = ttk.Style()
        self._configure_style()

        # Container
        container = ttk.Frame(self, style="Card.TFrame")
        container.pack(fill="both", expand=True)

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

        # Columns
        for col in self.columns:
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
        for row in self.tree.get_children():
            self.tree.delete(row)

        for item in data:
            item = list(item)
            if "Action" in self.columns:
                action_index = self.columns.index("Action")
                item.insert(action_index, "❌")
            else:
                item.append("❌")
            self.tree.insert("", "end", values=item)

    def _handle_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            col_index = int(self.tree.identify_column(event.x).replace("#", "")) - 1
            if self.columns[col_index] == "Action":
                row_id = self.tree.identify_row(event.y)
                if row_id and self.on_delete:
                    values = self.tree.item(row_id, "values")
                    self.on_delete(values)

    def _handle_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        values = self.tree.item(row_id, "values")
        employe_id = values[-1]
        nom_prenom = values[5] if len(values) > 5 else "غير معروف"

        confirm = messagebox.askokcancel(
            "تحديث معلومات الموظف",
            f"هل تريد تعديل معلومات الموظف:\n\n👤 الاسم واللقب: {nom_prenom}\n🆔 المعرف: {employe_id}"
        )

        if confirm and self.on_update:
            self.on_update(values)

    def update_data(self, new_data):
        self.load_data(new_data)
