import tkinter as tk
from tkinter import ttk
from datetime import datetime

class AddCongeInterface(tk.Toplevel):
    def __init__(self, parent, employe=None):
        super().__init__(parent)
        self.title("➕ Nouveau Congé")
        self.geometry("500x650")
        self.configure(bg="#FAFAFA")
        self.resizable(False, False)
        
        # Variables
        self.employe = employe or {}
        
        # Configuration des polices
        self.font_bold = ("Segoe UI", 14, "bold")
        self.font_normal = ("Segoe UI", 11)
        self.font_small = ("Segoe UI", 10)
        
        # Couleurs modernes
        self.colors = {
            "primary": "#7C3AED",      # Violet
            "surface": "#FFFFFF",      # Blanc
            "background": "#FAFAFA",   # Gris très clair
            "text": "#1F2937",         # Gris foncé
            "text_light": "#6B7280",   # Gris moyen
            "border": "#E5E7EB",       # Gris clair
            "error": "#EF4444",        # Rouge
            "success": "#10B981"       # Vert
        }
        
        # Construction
        self._create_layout()
        self._center_window()
        
        # Bind Enter pour validation
        self.bind('<Return>', lambda e: self._save())
        
    def _create_layout(self):
        """Crée l'interface minimaliste"""
        
        # ────────── HEADER ──────────
        header_frame = tk.Frame(self, bg=self.colors["surface"], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Titre avec ligne décorative
        title_container = tk.Frame(header_frame, bg=self.colors["surface"])
        title_container.pack(expand=True)
        
        tk.Label(title_container,
                text="إضافة عطلة",
                font=("Segoe UI", 20, "bold"),
                bg=self.colors["surface"],
                fg=self.colors["text"]).pack()
        
        tk.Label(title_container,
                text="للموظف: " + self.employe.get("nom", "غير محدد"),
                font=self.font_small,
                bg=self.colors["surface"],
                fg=self.colors["text_light"]).pack(pady=(5, 0))
        
        # ────────── CONTENT ──────────
        content_frame = tk.Frame(self, bg=self.colors["background"])
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Section Employé (minimal)
        emp_info = tk.Frame(content_frame, bg=self.colors["background"])
        emp_info.pack(fill="x", pady=(0, 20))
        
        # Nom et grade sur une ligne
        name_frame = tk.Frame(emp_info, bg=self.colors["surface"], 
                             relief="flat", bd=0)
        name_frame.pack(fill="x", pady=(0, 5))
        
        # Badge nom
        name_badge = tk.Label(name_frame,
                            text=self.employe.get("nom", "غير محدد"),
                            font=("Segoe UI", 12, "bold"),
                            bg="#F3E8FF",  # Violet très clair
                            fg=self.colors["primary"],
                            padx=15,
                            pady=8)
        name_badge.pack(side="right")
        
        # Badge grade
        grade_badge = tk.Label(name_frame,
                             text=self.employe.get("grade", "غير محدد"),
                             font=self.font_small,
                             bg=self.colors["border"],
                             fg=self.colors["text"],
                             padx=12,
                             pady=6)
        grade_badge.pack(side="right", padx=(5, 0))
        
        # ────────── FORM ──────────
        form_frame = tk.Frame(content_frame, bg=self.colors["background"])
        form_frame.pack(fill="both", expand=True)
        
        # Année
        self.annee_var = tk.StringVar()
        self._create_form_field(form_frame, "السنة", "2024", var=self.annee_var)
        
        # Type
        self.type_var = tk.StringVar(value="سنوية")
        self._create_combo_field(form_frame, "نوع العطلة", 
                                ["سنوية", "مرضية", "أمومة", "استثنائية"], 
                                var=self.type_var)
        
        # Dates
        dates_frame = tk.Frame(form_frame, bg=self.colors["background"])
        dates_frame.pack(fill="x", pady=10)
        
        self.debut_var = tk.StringVar()
        self._create_form_field(dates_frame, "من", "01/01/2024", 
                               var=self.debut_var, width=20)
        
        self.fin_var = tk.StringVar()
        self._create_form_field(dates_frame, "إلى", "15/01/2024", 
                               var=self.fin_var, width=20, padx=(10, 0))
        
        # Jours
        self.jours_var = tk.StringVar()
        self._create_form_field(form_frame, "عدد الأيام", "15", 
                               var=self.jours_var)
        
        # Lieu
        self.lieu_var = tk.StringVar()
        self._create_form_field(form_frame, "المكان", "الجزائر", 
                               var=self.lieu_var)
        
        # ────────── ACTIONS ──────────
        actions_frame = tk.Frame(content_frame, bg=self.colors["background"])
        actions_frame.pack(fill="x", pady=(30, 0))
        
        # Bouton Annuler (transparent)
        cancel_btn = tk.Button(actions_frame,
                             text="إلغاء",
                             font=self.font_normal,
                             bg="transparent",
                             fg=self.colors["text_light"],
                             bd=0,
                             padx=30,
                             pady=12,
                             cursor="hand2",
                             command=self.destroy)
        cancel_btn.pack(side="right")
        
        # Effet hover pour annuler
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(fg=self.colors["error"]))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(fg=self.colors["text_light"]))
        
        # Bouton Enregistrer (plein)
        save_btn = tk.Button(actions_frame,
                           text="تأكيد الإضافة",
                           font=self.font_normal,
                           bg=self.colors["primary"],
                           fg="white",
                           bd=0,
                           padx=40,
                           pady=12,
                           cursor="hand2",
                           command=self._save)
        save_btn.pack(side="right", padx=(10, 0))
        
        # Effet hover pour enregistrer
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#6D28D9"))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=self.colors["primary"]))
        
    def _create_form_field(self, parent, label, placeholder, var=None, width=None, **kwargs):
        """Crée un champ de formulaire minimaliste"""
        frame = tk.Frame(parent, bg=self.colors["background"])
        frame.pack(fill="x", pady=8)
        
        # Label discret
        tk.Label(frame,
                text=label,
                font=self.font_small,
                bg=self.colors["background"],
                fg=self.colors["text_light"]).pack(anchor="e")
        
        # Input avec effet de focus
        entry = tk.Entry(frame,
                        font=self.font_normal,
                        bg=self.colors["surface"],
                        fg=self.colors["text"],
                        relief="flat",
                        bd=1,
                        highlightthickness=1,
                        highlightcolor=self.colors["border"],
                        highlightbackground=self.colors["border"],
                        insertbackground=self.colors["primary"])
        
        if width:
            entry.config(width=width)
        
        entry.pack(fill="x", ipady=10, **kwargs)
        
        if var:
            entry.config(textvariable=var)
        
        # Placeholder
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=self.colors["text_light"])
            
            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=self.colors["text"])
            
            def on_focus_out(e):
                if entry.get() == "":
                    entry.insert(0, placeholder)
                    entry.config(fg=self.colors["text_light"])
            
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        
        # Animation de focus
        def set_focus_color(color):
            entry.config(highlightcolor=color)
        
        entry.bind("<FocusIn>", lambda e: set_focus_color(self.colors["primary"]))
        entry.bind("<FocusOut>", lambda e: set_focus_color(self.colors["border"]))
        
        return entry
    
    def _create_combo_field(self, parent, label, options, var=None):
        """Crée une liste déroulante minimaliste"""
        frame = tk.Frame(parent, bg=self.colors["background"])
        frame.pack(fill="x", pady=8)
        
        # Label
        tk.Label(frame,
                text=label,
                font=self.font_small,
                bg=self.colors["background"],
                fg=self.colors["text_light"]).pack(anchor="e")
        
        # Combobox stylisée
        combo = ttk.Combobox(frame,
                           values=options,
                           font=self.font_normal,
                           state="readonly",
                           height=10)
        
        # Style personnalisé
        combo.pack(fill="x", ipady=8)
        
        if var:
            combo.config(textvariable=var)
            if options:
                var.set(options[0])
        
        return combo
    
    def _center_window(self):
        """Centre la fenêtre"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
    
    def _save(self):
        """Enregistre le congé avec validation"""
        # Validation simple
        if not self.annee_var.get() or self.annee_var.get() == "2024":
            self._show_error("يرجى إدخال السنة")
            return
        
        if not self.jours_var.get() or self.jours_var.get() == "15":
            self._show_error("يرجى إدخال عدد الأيام")
            return
        
        # Données
        data = {
            "employe_nom": self.employe.get("nom", ""),
            "employe_grade": self.employe.get("grade", ""),
            "annee": self.annee_var.get(),
            "type": self.type_var.get(),
            "date_debut": self.debut_var.get(),
            "date_fin": self.fin_var.get(),
            "jours": self.jours_var.get(),
            "lieu": self.lieu_var.get(),
            "date_creation": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        # Simuler sauvegarde
        print("📝 Congé enregistré:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        
        # Message de succès
        self._show_success()
        
    def _show_error(self, message):
        """Affiche un message d'erreur discret"""
        if hasattr(self, 'error_label'):
            self.error_label.destroy()
        
        self.error_label = tk.Label(self,
                                  text=message,
                                  font=self.font_small,
                                  bg=self.colors["background"],
                                  fg=self.colors["error"])
        self.error_label.place(relx=0.5, rely=0.95, anchor="center")
        
        # Disparaît après 3 secondes
        self.after(3000, lambda: self.error_label.destroy() if hasattr(self, 'error_label') else None)
    
    def _show_success(self):
        """Affiche un message de succès et ferme"""
        success_frame = tk.Frame(self, bg=self.colors["success"])
        success_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(success_frame,
                text="✓ تمت الإضافة بنجاح",
                font=self.font_bold,
                bg=self.colors["success"],
                fg="white",
                padx=30,
                pady=15).pack()
        
        # Fermer après 1 seconde
        self.after(1000, self.destroy)