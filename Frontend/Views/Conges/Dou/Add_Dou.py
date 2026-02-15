import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from Frontend.Theme.colors import PRIMARY_COLOR
from Bakend.models.Conges.add_dou_conge import insert_conge, get_conge_periodes
from datetime import datetime, timedelta
from Bakend.models.Conges.update_dou import update_conge
from Bakend.models.Conges.conge_validations import (
    check_employe_has_conge_en_cours,
    validate_conge_solde
)
from Frontend.Utils.event_bus import publish

class AddCongeInterface(tk.Toplevel):
    # ✅ Variable de classe pour stocker l'instance actuelle
    _current_instance = None
    
    def __init__(self, parent, employe=None, conge_data=None, on_save_callback=None):
        # ✅ Vérifier s'il existe déjà une instance ouverte
        if AddCongeInterface._current_instance is not None:
            try:
                # Essayer de récupérer la fenêtre existante et la ramener au premier plan
                AddCongeInterface._current_instance.lift()
                AddCongeInterface._current_instance.focus()
                return
            except tk.TclError:
                # La fenêtre n'existe plus, on peut créer une nouvelle instance
                pass
        
        super().__init__(parent)
        
        # ✅ Enregistrer cette instance comme la seule instance active
        AddCongeInterface._current_instance = self

        self.is_update_mode = conge_data is not None
        self.conge_data = conge_data or {}        
        self.geometry("750x850")
        self.resizable(False, False)
        
        # ✅ Nettoyer la référence quand la fenêtre se ferme
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.employe = employe or {}
        self.id_employe = self.employe.get("id_employe", None)
        self.id_conge = self.conge_data.get("id_conge", None) 
        self.on_save_callback = on_save_callback 
        self.nom_var = tk.StringVar(value=self.employe.get("nom", "غير معروف"))
        self.prenom_var = tk.StringVar(value=self.employe.get("prenom", "غير معروف"))
        self.grade_var = tk.StringVar(value=self.employe.get("grade", "غير معروف"))

        self.type_conge_var = tk.StringVar(value=self.conge_data.get("type_conge", "سنوية"))
        self.nbr_jours_var = tk.StringVar(value=str(self.conge_data.get("nb_jours", "")))
        self.lieu_var = tk.StringVar(value=self.conge_data.get("lieu", ""))

        self.periodes_conge = []

        # ================= COLORS =================
        self.colors = {
            "bg": "#f5f6fa",
            "card": "#FFFFFF",
            "header": PRIMARY_COLOR,
            "header_text": "#FFFFFF",
            "submit": PRIMARY_COLOR,
            "cancel": "#e74c3c",
            "border": "#e0e0e0"
        }
        self.periodes_frame = None
        self.periode_listbox = None
        self.delete_button = None
        
        # ✅ VALIDATION: Vérifier si l'employé a déjà un congé (MODE INSERT uniquement)
        if not self.is_update_mode:
            has_conge, conge_info = check_employe_has_conge_en_cours(self.id_employe)
            if has_conge:
                self.destroy()
                response = messagebox.askyesno(
                    "تنبيه",
                    f"""هذا الموظف لديه عطلة بالفعل!

نوع العطلة: {conge_info['type_conge']}
تاريخ البداية: {conge_info['date_debut']}
تاريخ النهاية: {conge_info['date_fin']}
عدد الأيام: {conge_info['nb_jours']}
الحالة: {conge_info['statut']}

هل تريد تعديل العطلة الموجودة؟"""
                )
                
                if response:
                    messagebox.showinfo("معلومات", "يرجى استخدام زر 'تعديل' لتحديث العطلة الموجودة")
                return
        
        self._style()
        self._build_ui()
        
        # ✅ Charger les périodes APRÈS la création de l'UI
        if self.is_update_mode and self.id_conge:
            self._load_existing_periodes()
        
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

        # ✅ Button styles
        style.configure(
            "Submit.TButton",
            font=("Arial", 11, "bold"),
            background=self.colors["submit"],
            foreground="#fff"
        )
        style.map(
            "Submit.TButton",
            background=[("active", self.colors["submit"])],
            foreground=[("active", "#fff")]
        )

        style.configure(
            "Cancel.TButton",
            font=("Arial", 11, "bold"),
            background=self.colors["cancel"],
            foreground="#fff"
        )
        style.map(
            "Cancel.TButton",
            background=[("active", self.colors["cancel"])],
            foreground=[("active", "#fff")]
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
        title = "تعديل عطلة" if self.is_update_mode else "إضافة عطلة"
        ttk.Label(header, text=title, style="Header.TLabel").pack(pady=15)

    # ================= CARD EMPLOYEE =================
    def _card_employee(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["card"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        card.pack(fill=tk.X, pady=(0, 15))

        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill=tk.BOTH, padx=20, pady=15)

        for i in range(4):
            content.columnconfigure(i, weight=1)

        ttk.Label(
            content,
            text="معلومات الموظف",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=4, sticky="e", pady=(0, 15))

        ttk.Label(content, text="اللقب", style="Label.TLabel").grid(
            row=1, column=3, sticky="e", padx=5, pady=8
        )
        ttk.Entry(
            content,
            textvariable=self.nom_var,
            state="readonly",
            justify="right",
            width=22
        ).grid(row=1, column=2, sticky="e", padx=(5, 20), pady=8)

        ttk.Label(content, text="الإسم", style="Label.TLabel").grid(
            row=1, column=1, sticky="e", padx=5, pady=8
        )
        ttk.Entry(
            content,
            textvariable=self.prenom_var,
            state="readonly",
            justify="right",
            width=22
        ).grid(row=1, column=0, sticky="e", padx=(5, 20), pady=8)

        ttk.Label(content, text="الرتبة", style="Label.TLabel").grid(
            row=2, column=3, sticky="e", padx=5, pady=8
        )
        ttk.Entry(
            content,
            textvariable=self.grade_var,
            state="readonly",
            justify="right",
            width=22
        ).grid(row=2, column=2, sticky="e", padx=(5, 20), pady=8)

    # ================= CARD CONGE =================
    def _card_conge(self, parent):
        card = tk.Frame(
            parent,
            bg=self.colors["card"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        card.pack(fill=tk.X)

        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill=tk.BOTH, padx=20, pady=15)

        for i in range(4):
            content.columnconfigure(i, weight=1)

        ttk.Label(
            content,
            text="تفاصيل العطلة",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=4, sticky="e", pady=(0, 15))

        ttk.Label(content, text="نوع العطلة", style="Label.TLabel").grid(
            row=1, column=3, sticky="e", padx=5, pady=8
        )
        ttk.Combobox(
            content,
            textvariable=self.type_conge_var,
            values=["سنوية", "مرضية", "استثنائية"],
            state="readonly",
            justify="right",
            width=22
        ).grid(row=1, column=2, sticky="e", padx=(5, 20), pady=8)

        ttk.Label(content, text="تاريخ البداية", style="Label.TLabel").grid(
            row=2, column=3, sticky="e", padx=5, pady=8
        )
        self.date_debut = DateEntry(content, width=22, date_pattern="dd/mm/yyyy")
        self.date_debut.grid(row=2, column=2, sticky="e", padx=(5, 20), pady=8)

        ttk.Label(content, text="عدد الأيام", style="Label.TLabel").grid(
            row=2, column=1, sticky="e", padx=5, pady=8
        )
        ttk.Entry(
            content,
            textvariable=self.nbr_jours_var,
            justify="right",
            width=22
        ).grid(row=2, column=0, sticky="e", padx=(5, 20), pady=8)

        ttk.Label(content, text="تاريخ النهاية", style="Label.TLabel").grid(
            row=3, column=3, sticky="e", padx=5, pady=8
        )
        self.date_fin = DateEntry(content, width=22, date_pattern="dd/mm/yyyy")
        self.date_fin.grid(row=3, column=2, sticky="e", padx=(5, 20), pady=8)

        ttk.Label(content, text="المكان", style="Label.TLabel").grid(
            row=3, column=1, sticky="e", padx=5, pady=8
        )
        ttk.Combobox(
            content,
            textvariable=self.lieu_var,
            values=["داخل التراب الوطني", "خارج التراب الوطني"],
            state="readonly",
            justify="right",
            width=22
        ).grid(row=3, column=0, sticky="e", padx=(5, 20), pady=8)

        ttk.Button(
            content,
            text="➕ إضافة فترة عطلة",
            command=self._add_periode
        ).grid(row=4, column=0, columnspan=4, pady=15)

        # Frame for displaying added periods
        self.periodes_frame = tk.Frame(content, bg=self.colors["card"])
        self.periodes_frame.grid(row=5, column=0, columnspan=4, sticky="ew")
        self.periode_listbox = tk.Listbox(self.periodes_frame, width=50, justify="right")
        self.periode_listbox.pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_button = ttk.Button(self.periodes_frame, text="حذف الفترة", command=self._remove_periode)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        self.periodes_frame.grid_remove()  # hide initially

        self.nbr_jours_var.trace_add("write", self._calculate_date_fin)
        self.date_debut.bind("<<DateEntrySelected>>", self._calculate_date_fin)

    def _calculate_date_fin(self, *args):
        try:
            debut = self.date_debut.get_date()
            nb_jours = int(self.nbr_jours_var.get())
            if nb_jours > 0:
                self.date_fin.set_date(debut + timedelta(days=nb_jours - 1))
        except Exception:
            pass

    # ================= BUTTONS =================
    def _buttons(self, parent):
        btns = tk.Frame(parent, bg=self.colors["bg"])
        btns.pack(pady=20)

        ttk.Button(
            btns,
            text="إلغاء",
            style="Cancel.TButton",
            command=self.destroy
        ).grid(row=0, column=0, padx=10, ipadx=20, ipady=8)

        ttk.Button(
            btns,
            text="تأكيد",
            style="Submit.TButton",
            command=self._save
        ).grid(row=0, column=1, padx=10, ipadx=20, ipady=8)

    # ================= LOGIC =================
    def _add_periode(self):
        debut = self.date_debut.get_date()
        fin = self.date_fin.get_date()
        if fin < debut:
            messagebox.showerror("خطأ", "تاريخ النهاية يجب أن يكون بعد تاريخ البداية")
            return

        self.periodes_conge.append((debut, fin))
        self._show_periodes_widgets()
        self.periode_listbox.insert(
            tk.END,
            f"{debut.strftime('%d/%m/%Y')} → {fin.strftime('%d/%m/%Y')}"
        )
        self._update_total_days()

    def _load_existing_periodes(self):
        """
        ✅ Charger les périodes depuis la base de données
        """
        try:
            # ✅ Récupérer les périodes depuis la base de données
            periodes_db = get_conge_periodes(self.id_conge)
            
            if not periodes_db:
                print(f"⚠️ Aucune période trouvée pour id_conge={self.id_conge}")
                return
            
            print(f"✅ Chargement de {len(periodes_db)} période(s)")
            
            for periode in periodes_db:
                date_debut_str = periode[0]  # Format: "YYYY-MM-DD"
                date_fin_str = periode[1]    # Format: "YYYY-MM-DD"
                
                # ✅ Convertir les strings en datetime.date
                debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
                fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()
                
                # ✅ Ajouter à la liste
                self.periodes_conge.append((debut, fin))
                
                # ✅ Afficher dans le listbox
                self.periode_listbox.insert(
                    tk.END,
                    f"{debut.strftime('%d/%m/%Y')} → {fin.strftime('%d/%m/%Y')}"
                )
            
            # ✅ Afficher le frame des périodes
            if len(self.periodes_conge) > 0:
                self._show_periodes_widgets()
                self._update_total_days()
                
                # ✅ Définir les dates d'entrée à la première période uniquement
                # (après _update_total_days pour éviter que _calculate_date_fin les écrase)
                first_debut = self.periodes_conge[0][0]
                first_fin = self.periodes_conge[0][1]
                
                self.date_debut.set_date(first_debut)
                self.date_fin.set_date(first_fin)
                
        except Exception as e:
            print(f"❌ Erreur lors du chargement des périodes: {e}")
            messagebox.showerror("خطأ", f"خطأ في تحميل الفترات: {str(e)}")

    def _remove_periode(self):
        sel = self.periode_listbox.curselection()
        if sel:
            self.periode_listbox.delete(sel[0])
            self.periodes_conge.pop(sel[0])
            self._update_total_days()
            if len(self.periodes_conge) == 0:
                self.periodes_frame.grid_remove()

    def _show_periodes_widgets(self):
        self.periodes_frame.grid()  # show the frame

    def _update_total_days(self):
        total = sum((fin - debut).days + 1 for debut, fin in self.periodes_conge)
        self.nbr_jours_var.set(str(total))

    def _save(self):
        """
        ✅ Enregistrer ou mettre à jour le congé avec VALIDATIONS
        """
        # ✅ Validation de base
        if not self.id_employe:
            messagebox.showerror("خطأ", "الموظف غير معروف")
            return

        if not self.lieu_var.get():
            messagebox.showerror("خطأ", "يجب اختيار مكان العطلة")
            return

        # ✅ Préparer les périodes
        if len(self.periodes_conge) == 0:
            try:
                debut = self.date_debut.get_date()
                fin = self.date_fin.get_date()
                
                if fin < debut:
                    messagebox.showerror("خطأ", "تاريخ النهاية يجب أن يكون بعد تاريخ البداية")
                    return
                
                periodes_to_save = [(debut, fin)]
                
            except Exception as e:
                messagebox.showerror("خطأ", "يرجى التحقق من التواريخ")
                return
        else:
            periodes_to_save = self.periodes_conge

        # ✅ Calculer le nombre total de jours
        total_jours = sum((fin - debut).days + 1 for debut, fin in periodes_to_save)

        # ✅ VALIDATION DU SOLDE
        id_conge_to_exclude = self.id_conge if self.is_update_mode else None
        is_valid, message, solde_info = validate_conge_solde(
            self.id_employe, 
            total_jours,
            id_conge_to_exclude
        )
        
        if not is_valid:
            messagebox.showerror("⚠️ رصيد غير كافٍ", message)
            return

        # ✅ Afficher un message de confirmation avec le solde
        confirm = messagebox.askyesno(
            "تأكيد العطلة",
            f"""{message}

هل تريد المتابعة؟"""
        )
        
        if not confirm:
            return

        # ✅ MODE UPDATE
        if self.is_update_mode:
            if not self.id_conge:
                messagebox.showerror("خطأ", "معرّف العطلة غير صالح")
                return
            
            print(f"🔄 Mise à jour du congé id_conge={self.id_conge}, id_employe={self.id_employe}")
            
            success, msg = update_conge(
                id_conge=self.id_conge,
                id_employe=self.id_employe,
                type_conge=self.type_conge_var.get(),
                periodes=periodes_to_save,
                lieu=self.lieu_var.get()
            )
        
        # ✅ MODE INSERT
        else:
            print(f"➕ Insertion d'un nouveau congé pour id_employe={self.id_employe}")
            
            success, msg = insert_conge(
                id_employe=self.id_employe,
                type_conge=self.type_conge_var.get(),
                periodes=periodes_to_save,
                lieu=self.lieu_var.get()
            )

        # ✅ Gestion du résultat
        if not success:
            messagebox.showerror("خطأ", msg)
            return

        messagebox.showinfo("نجاح", msg)
        
        # ✅ Appeler le callback AVANT de fermer la fenêtre
        if self.on_save_callback:
            self.on_save_callback()
        # Notify other views that a congé was created/updated
        try:
            publish("conge_saved", id_conge=(self.id_conge if self.id_conge else None), id_employe=self.id_employe)
        except Exception:
            pass
        
        # ✅ Fermer la fenêtre après un court délai pour laisser le temps à la mise à jour
        self.after(500, self._on_closing)

    # ================= CENTER WINDOW =================
    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _on_closing(self):
        """
        ✅ Nettoyer la référence quand la fenêtre se ferme
        """
        AddCongeInterface._current_instance = None
        self.destroy()