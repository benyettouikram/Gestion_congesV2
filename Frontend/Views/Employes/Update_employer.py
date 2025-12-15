import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date, datetime
from Bakend.models.Employer.Update.Update_employe import update_employe
from Frontend.Theme.colors import Heading_table_color


class UpdateEmployePage(tk.Frame):
    """
    Page to update an existing employee.
    `employe_data` must be a dict with employee info including 'id'.
    """

    def __init__(self, parent, employe_data, on_success=None):
        super().__init__(parent, bg="#F8F9FA")
        self.parent_window = parent  # Store reference to parent window
        self.on_success = on_success
        self.employe_data = employe_data
        self.create_widgets()
        self.prefill_fields()

    def create_widgets(self):
        main_container = tk.Frame(self, bg="#F8F9FA")
        main_container.pack(fill="both", expand=True, padx=40, pady=30)

        # 🟦 Header
        header = tk.Label(
            main_container,
            text="تحديث بيانات الموظف",
            font=("Arial", 20, "bold"),
            bg=Heading_table_color,
            fg="white",
            pady=15
        )
        header.pack(fill="x", pady=(0, 25))

        # 📋 Form container
        form_frame = tk.Frame(main_container, bg="white", padx=30, pady=25)
        form_frame.pack(fill="both", expand=True)

        # 🏠 Résidence
        self.residence_var = tk.StringVar()
        self.residence_var.trace_add("write", self.on_residence_change)

        tk.Label(form_frame, text="Select Résidence (French)", font=("Arial", 10, "bold"),
                 bg="white", anchor="center").grid(row=0, column=0, pady=(5, 5), sticky="ew")
        tk.Label(form_frame, text="اختر مكان الإقامة", font=("Arial", 10, "bold"),
                 bg="white", anchor="center").grid(row=0, column=1, pady=(5, 5), sticky="ew")

        self.residence_map = {
            "مديرية الخدمات الجامعية": "Les Œuvres Universitaires",
            "الإقامة الجامعية 19 ماي 1956": "Résidence Universitaire 19 Mai 1956",
            "الإقامة الجامعية 1 نوفمبر 1954": "Résidence Universitaire 1er Novembre 1954",
            "الإقامة الجامعية هني صالح": "Résidence Universitaire Heni Salah",
            "الإقامة الجامعية طويل عبد القادر": "Résidence Universitaire Touil Abdelkader",
            "الإقامة الجامعية أولاد فارس 03 ": "Résidence Universitaire Ouled Farès 03",
            "الإقامة الجامعية أولاد فارس 04 ": "Résidence Universitaire Ouled Farès 04",
            "الإقامة الجامعية الحسنية 1500 سرير   ": "Résidence Universitaire Hassania 1500 lits",
            "الإقامة الجامعية الحسنية 2000 سرير  ": "Résidence Universitaire Hassania 2000 lits",
            "الإقامة الجامعية تنس 500 سرير ": "Résidence Universitaire Tenès 500 lits",
        }

        residence_options = list(self.residence_map.keys())

        self.residenceF_entry = tk.Entry(form_frame, font=("Arial", 11), width=30,
                                         relief="solid", bd=1, bg="#F5F5F5", justify="center")
        self.residenceF_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.residence_combo = ttk.Combobox(form_frame, textvariable=self.residence_var,
                                            values=residence_options, font=("Arial", 11),
                                            state="readonly", justify="center", width=30)
        self.residence_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Département
        self.dept_frame = tk.Frame(form_frame, bg="white")
        self.dept_frame.grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")
        tk.Label(self.dept_frame, text="القسم", font=("Arial", 10, "bold"), bg="white",
                 anchor="center").pack(side="top", fill="x")
        self.departement_entry = tk.Entry(self.dept_frame, font=("Arial", 11), width=30,
                                          relief="solid", bd=1, bg="#F5F5F5", justify="center")
        self.departement_entry.pack(side="top", pady=(5, 0))
        self.dept_frame.grid_remove()

        # Nom & Prénom
        self.nom_entry, self.nomF_entry = self._create_field_pair(form_frame, "اللقب", "Nom", 3)
        self.prenom_entry, self.prenomF_entry = self._create_field_pair(form_frame, "الاسم", "Prénom", 4)

        # Date de naissance
        date_frame = tk.Frame(form_frame, bg="white")
        date_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        tk.Label(date_frame, text="تاريخ الميلاد", font=("Arial", 10, "bold"), bg="white",
                 anchor="center").pack(side="top", fill="x", pady=(0, 5))
        self.date_naissance_entry = DateEntry(date_frame, width=20, background='darkblue',
                                              foreground='white', date_pattern='yyyy-mm-dd')
        self.date_naissance_entry.pack(side="top", pady=(5, 0))

        # Grade & Poste
        self.grade_entry, self.gradeF_entry = self._create_field_pair(form_frame, "الرتبة", "Grade", 6)
        self.poste_entry, self.posteF_entry = self._create_field_pair(form_frame, "المنصب الأعلى", "Poste supérieur", 7)

        # Ancien congé
        self._create_single_field(form_frame, "العطلة القديمة (بالأيام)", 8)

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=9, column=0, columnspan=2, pady=25)

        tk.Button(
            btn_frame, text="تحديث", command=self.update_employe_action,
            bg="#2196F3", fg="white", font=("Arial", 12, "bold"),
            padx=25, pady=10, relief="flat", cursor="hand2", width=15
        ).pack(side="left", padx=15)

        tk.Button(
            btn_frame, text="مسح", command=self.clear_fields,
            bg="#757575", fg="white", font=("Arial", 12, "bold"),
            padx=25, pady=10, relief="flat", cursor="hand2", width=15
        ).pack(side="left", padx=15)

    # --- Field helpers ---
    def _create_field_pair(self, parent, label_ar, label_fr, row):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")

        # French
        left = tk.Frame(frame, bg="white")
        left.pack(side="left", fill="x", expand=True, padx=(0, 30))
        tk.Label(left, text=label_fr, font=("Arial", 10, "bold"), bg="white", anchor="w").pack(side="top", fill="x")
        entry_fr = tk.Entry(left, font=("Arial", 11), width=25, relief="solid", bd=1, bg="#F5F5F5")
        entry_fr.pack(side="top", fill="x", pady=(5, 0))

        # Arabic
        right = tk.Frame(frame, bg="white")
        right.pack(side="right", fill="x", expand=True, padx=(30, 0))
        tk.Label(right, text=label_ar, font=("Arial", 10, "bold"), bg="white", anchor="e").pack(side="top", fill="x")
        entry_ar = tk.Entry(right, font=("Arial", 11), width=25, relief="solid", bd=1, bg="#F5F5F5")
        entry_ar.pack(side="top", fill="x", pady=(5, 0))

        return entry_ar, entry_fr

    def _create_single_field(self, parent, label_ar, row):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        tk.Label(frame, text=label_ar, font=("Arial", 10, "bold"), bg="white").pack(side="top", fill="x")
        self.ancien_entry = tk.Entry(frame, font=("Arial", 11), width=30, relief="solid", bd=1, bg="#F5F5F5", justify="center")
        self.ancien_entry.pack(side="top", pady=(5, 0))

    # --- Prefill ---
    def prefill_fields(self):
        """✅ FIXED: Now properly fills all fields with correct data"""
        data = self.employe_data
        
        # Residence
        self.residence_var.set(data.get("residence", ""))
        self.residenceF_entry.delete(0, tk.END)
        self.residenceF_entry.insert(0, data.get("residenceF", ""))
        
        # Departement
        self.departement_entry.delete(0, tk.END)
        self.departement_entry.insert(0, data.get("departement", ""))
        
        # Nom (Arabic and French)
        self.nom_entry.delete(0, tk.END)
        self.nom_entry.insert(0, data.get("nom", ""))
        self.nomF_entry.delete(0, tk.END)
        self.nomF_entry.insert(0, data.get("NomF", ""))
        
        # Prenom (Arabic and French)
        self.prenom_entry.delete(0, tk.END)
        self.prenom_entry.insert(0, data.get("prenom", ""))
        self.prenomF_entry.delete(0, tk.END)
        self.prenomF_entry.insert(0, data.get("prenomF", ""))

        # Date
        date_str = data.get("date_naissance")
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                try:
                    dt = datetime.strptime(date_str, "%d/%m/%Y").date()
                except ValueError:
                    dt = date.today()
        else:
            dt = date.today()
        self.date_naissance_entry.set_date(dt)

        # Grade (Arabic and French)
        self.grade_entry.delete(0, tk.END)
        self.grade_entry.insert(0, data.get("grade", ""))
        self.gradeF_entry.delete(0, tk.END)
        self.gradeF_entry.insert(0, data.get("gradeF", ""))
        
        # Poste (Arabic and French)
        self.poste_entry.delete(0, tk.END)
        self.poste_entry.insert(0, data.get("poste_superieur", ""))
        self.posteF_entry.delete(0, tk.END)
        self.posteF_entry.insert(0, data.get("poste_superieurF", ""))
        
        # Ancien conges
        self.ancien_entry.delete(0, tk.END)
        self.ancien_entry.insert(0, str(data.get("ancien_conges", 0)))

    # --- Residence change ---
    def on_residence_change(self, *args):
        residence_ar = self.residence_var.get().strip()
        french_value = self.residence_map.get(residence_ar, "")
        self.residenceF_entry.delete(0, tk.END)
        self.residenceF_entry.insert(0, french_value)
        if residence_ar == "مديرية الخدمات الجامعية":
            self.dept_frame.grid()
        else:
            self.dept_frame.grid_remove()
            self.departement_entry.delete(0, tk.END)

    # --- Update action ---
    def update_employe_action(self):
        data = {
            "residence": self.residence_var.get().strip(),
            "residenceF": self.residenceF_entry.get().strip(),
            "departement": self.departement_entry.get().strip(),
            "nom": self.nom_entry.get().strip(),
            "prenom": self.prenom_entry.get().strip(),
            "NomF": self.nomF_entry.get().strip(),
            "prenomF": self.prenomF_entry.get().strip(),
            "date_naissance": self.date_naissance_entry.get_date().strftime("%Y-%m-%d"),
            "grade": self.grade_entry.get().strip(),
            "gradeF": self.gradeF_entry.get().strip(),
            "poste_superieur": self.poste_entry.get().strip(),
            "poste_superieurF": self.posteF_entry.get().strip(),
            "ancien_conges": self.ancien_entry.get().strip()
        }

        try:
            data["ancien_conges"] = int(data["ancien_conges"]) if data["ancien_conges"] else 0
        except ValueError:
            messagebox.showwarning("تحذير / Attention", "يجب أن يكون عدد أيام العطلة القديمة رقماً صحيحاً")
            return

        try:
            success = update_employe(
                employe_id=self.employe_data["id"],
                residence=data["residence"],
                residenceF=data["residenceF"],
                departement=data["departement"],
                nom=data["nom"],
                prenom=data["prenom"],
                NomF=data["NomF"],
                prenomF=data["prenomF"],
                date_naissance=data["date_naissance"],
                grade=data["grade"],
                gradeF=data["gradeF"],
                poste_superieur=data["poste_superieur"],
                poste_superieurF=data["poste_superieurF"],
                ancien_conges=data["ancien_conges"]
            )
            
            if success:
                messagebox.showinfo("نجاح / Succès", "✓ تم تحديث الموظف بنجاح")
                # Close the update window
                if isinstance(self.parent_window, tk.Toplevel):
                    self.parent_window.destroy()
                # Call success callback
                if self.on_success:
                    self.on_success()
            else:
                messagebox.showerror("خطأ / Erreur", "✗ فشل في تحديث الموظف")
        except Exception as e:
            messagebox.showerror("خطأ / Erreur", f"حدث خطأ غير متوقع: {str(e)}")

    # --- Clear ---
    def clear_fields(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                self.clear_frame_entries(widget)

    def clear_frame_entries(self, frame):
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
            elif isinstance(widget, tk.Frame):
                self.clear_frame_entries(widget)