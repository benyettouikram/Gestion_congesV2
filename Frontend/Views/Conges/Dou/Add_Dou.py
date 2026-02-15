import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from Frontend.Theme.colors import PRIMARY_COLOR, Heading_table_color


class AddCongeInterface(tk.Toplevel):
    def __init__(self, parent, employe=None):
        super().__init__(parent)

        self.title("إضافة عطلة")
        self.geometry("750x800")
        self.resizable(False, False)

        self.employe = employe or {
            "nom": "محمد",
            "prenom": "أحمد",
            "grade": "موظف إداري"
        }

        # ================= VARIABLES =================
        self.nom_var = tk.StringVar(value=self.employe['nom'])
        self.prenom_var = tk.StringVar(value=self.employe['prenom'])
        self.grade_var = tk.StringVar(value=self.employe['grade'])
        self.type_conge_var = tk.StringVar(value="سنوية")
        self.lieu_var = tk.StringVar(value="داخل التراب الوطني")
        self.nbr_jours_var = tk.StringVar(value="0")

        self.periodes_conge = []
        
        # Variables pour les widgets dynamiques
        self.periode_listbox = None
        self.delete_button = None
        self.periodes_frame = None

        # ================= COLORS =================
        self.colors = {
            "bg": "#f5f6fa",
            "card": "#FFFFFF",
            "header": PRIMARY_COLOR,
            "header_text": "#FFFFFF",
            "submit": Heading_table_color,
            "cancel": "#e74c3c",
            "border": "#e0e0e0",
            "delete": "#e67e22"
        }

        self._style()
        self._build_ui()
        self._center()

    # ================= STYLES =================
    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Header.TFrame", background=self.colors["header"])
        style.configure(
            "Header.TLabel",
            background=self.colors["header"],
            foreground=self.colors["header_text"],
            font=("Arial", 18, "bold")
        )

        style.configure("Card.TFrame", background=self.colors["card"])
        style.configure(
            "CardTitle.TLabel",
            background=self.colors["card"],
            foreground="#000",
            font=("Arial", 14, "bold")
        )

        style.configure(
            "Label.TLabel",
            background=self.colors["card"],
            foreground="#000",
            font=("Segoe UI Semibold", 11)
        )

        style.configure(
            "Submit.TButton",
            font=("Arial", 11, "bold"),
            background=self.colors["submit"],
            foreground="black"
        )

        style.configure(
            "Cancel.TButton",
            font=("Arial", 11, "bold"),
            background=self.colors["cancel"],
            foreground="black"
        )

        style.configure(
            "Delete.TButton",
            font=("Arial", 10, "bold"),
            background=self.colors["delete"],
            foreground="white"
        )

    # ================= UI =================
    def _build_ui(self):
        self.configure(bg=self.colors["bg"])
        self._header()

        container = tk.Frame(self, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        self._card_employee(container)
        self._card_conge(container)
        self._buttons(container)

    def _header(self):
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill=tk.X)
        ttk.Label(header, text="إضافة عطلة", style="Header.TLabel").pack(pady=15)

    # ================= CARD EMPLOYEE =================
    def _card_employee(self, parent):
        card = tk.Frame(parent, bg=self.colors["card"],
                        highlightbackground=self.colors["border"],
                        highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 15))

        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill=tk.BOTH, padx=20, pady=15)

        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="معلومات الموظف",
                  style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky=tk.E, pady=(0, 15))

        ttk.Label(content, text="اللقب", style="Label.TLabel").grid(
            row=1, column=1, sticky="ne", pady=(5, 0))
        ttk.Entry(content, width=25, justify="right",
                  state="readonly", textvariable=self.nom_var).grid(
            row=2, column=1, padx=(30, 5), pady=(3, 12))

        ttk.Label(content, text="الإسم", style="Label.TLabel").grid(
            row=1, column=0, sticky="ne", pady=(5, 0))
        ttk.Entry(content, width=25, justify="right",
                  state="readonly", textvariable=self.prenom_var).grid(
            row=2, column=0, padx=(30, 5), pady=(3, 12))

        ttk.Label(content, text="الرتبة", style="Label.TLabel").grid(
            row=3, column=1, sticky="ne", pady=(5, 0))
        ttk.Entry(content, width=25, justify="right",
                  state="readonly", textvariable=self.grade_var).grid(
            row=4, column=1, padx=(30, 5), pady=(3, 12))

    # ================= CARD CONGE =================
    def _card_conge(self, parent):
        card = tk.Frame(parent, bg=self.colors["card"],
                        highlightbackground=self.colors["border"],
                        highlightthickness=1)
        card.pack(fill=tk.X)

        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill=tk.BOTH, padx=20, pady=15)

        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="تفاصيل العطلة",
                  style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky=tk.E, pady=(0, 15))

        ttk.Label(content, text="نوع العطلة", style="Label.TLabel").grid(
            row=1, column=1, sticky="ne", pady=(5, 0))
        ttk.Combobox(content, textvariable=self.type_conge_var,
                     values=["سنوية", "مرضية", "استثنائية"],
                     state="readonly", width=23, justify="right").grid(
            row=2, column=1, padx=(30, 5), pady=(3, 15))

        # ✅ ADDED: Number of days next to type of leave
        ttk.Label(content, text="عدد الأيام", style="Label.TLabel").grid(
            row=1, column=0, sticky="ne", pady=(5, 0))

        
        days_frame = ttk.Frame(content, style="Card.TFrame")
        days_frame.grid(row=2, column=0, padx=(30, 5), pady=(3, 15))
        ttk.Entry(
            days_frame,
            textvariable=self.nbr_jours_var,
            state="normal",
            width=10,
            justify="right"
        ).pack(side=tk.RIGHT)

        
        ttk.Label(content, text="تاريخ البداية", style="Label.TLabel").grid(
            row=3, column=1, sticky="ne", pady=(5, 0))
        self.date_debut = DateEntry(content, width=22, date_pattern="dd/mm/yyyy")
        self.date_debut.grid(row=4, column=1, padx=(30, 5), pady=(3, 12))

        ttk.Label(content, text="تاريخ النهاية", style="Label.TLabel").grid(
            row=3, column=0, sticky="ne", pady=(5, 0))
        self.date_fin = DateEntry(content, width=22, date_pattern="dd/mm/yyyy")
        self.date_fin.grid(row=4, column=0, padx=(30, 5), pady=(3, 12))

        ttk.Button(content, text="➕ إضافة فترة عطلة",
                   command=self._add_periode).grid(
            row=5, column=0, columnspan=2, pady=10)

        # ✅ Stocker le parent pour créer le frame plus tard
        self.conge_content = content

    # ================= BUTTONS =================
    def _buttons(self, parent):
        btns = tk.Frame(parent, bg=self.colors["bg"])
        btns.pack(pady=20)

        ttk.Button(btns, text="تأكيد",
                   style="Submit.TButton",
                   command=self._save).grid(
            row=0, column=1, padx=10, ipadx=20, ipady=8)

        ttk.Button(btns, text="إلغاء",
                   style="Cancel.TButton",
                   command=self.destroy).grid(
            row=0, column=0, padx=10, ipadx=20, ipady=8)

    # ================= LOGIC =================
    def _show_periodes_widgets(self):
        """Afficher le Listbox et le bouton de suppression"""
        if self.periode_listbox is None:
            # ✅ Créer le frame seulement maintenant
            self.periodes_frame = ttk.Frame(self.conge_content, style="Card.TFrame")
            self.periodes_frame.grid(row=6, column=0, columnspan=2, sticky="we", pady=(10, 0))
            
            # Créer le Listbox
            self.periode_listbox = tk.Listbox(self.periodes_frame, height=5)
            self.periode_listbox.pack(fill=tk.BOTH, padx=10, pady=(0, 10))
            
            # Créer le bouton de suppression
            self.delete_button = ttk.Button(
                self.periodes_frame, 
                text="🗑️ حذف الفترة المحددة",
                style="Delete.TButton",
                command=self._remove_periode
            )
            self.delete_button.pack(pady=(0, 10))

    def _add_periode(self):
        debut = self.date_debut.get_date()
        fin = self.date_fin.get_date()

        if fin < debut:
            messagebox.showerror("خطأ", "تاريخ النهاية يجب أن يكون بعد تاريخ البداية")
            return

        # Ajouter la période
        self.periodes_conge.append((debut, fin))
        
        # ✅ Afficher les widgets s'ils ne sont pas encore visibles
        self._show_periodes_widgets()
        
        # Ajouter à la liste
        self.periode_listbox.insert(
            tk.END,
            f"{debut.strftime('%d/%m/%Y')} → {fin.strftime('%d/%m/%Y')}"
        )
        
        # ✅ Update total days
        self._update_total_days()

    def _remove_periode(self):
        sel = self.periode_listbox.curselection()
        if sel:
            self.periode_listbox.delete(sel[0])
            self.periodes_conge.pop(sel[0])
            
            # ✅ Update total days
            self._update_total_days()
            
            # ✅ Si toutes les périodes sont supprimées, cacher les widgets
            if len(self.periodes_conge) == 0:
                self.periodes_frame.grid_forget()
                self.periode_listbox = None
                self.delete_button = None

    def _update_total_days(self):
        """Calculate and update total number of days"""
        total = sum((fin - debut).days + 1 for debut, fin in self.periodes_conge)
        self.nbr_jours_var.set(str(total))

    def _save(self):
        if not self.periodes_conge:
            messagebox.showerror("خطأ", "يجب إضافة فترة واحدة على الأقل")
            return
            
        messagebox.showinfo("نجاح", "تم حفظ العطلة بنجاح")
        self.destroy()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")