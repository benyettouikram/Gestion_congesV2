import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from Bakend.models.Employer.Add_employer import add_employe
from Frontend.Theme.colors import Heading_table_color
from Frontend.Utils.event_bus import publish


class AddEmployePage(tk.Frame):
    def __init__(self, parent, on_success=None):
        super().__init__(parent, bg="#F8F9FA")
        self.on_success = on_success
        self.create_widgets()

    def create_widgets(self):
        main_container = tk.Frame(self, bg="#F8F9FA")
        main_container.pack(fill="both", expand=True, padx=40, pady=30)

        # 🟦 Header
        header = tk.Label(
            main_container,
            text="إضافة موظف جديد",
            font=("Arial", 20, "bold"),
            bg=Heading_table_color,
            fg="white",
            pady=15
        )
        header.pack(fill="x", pady=(0, 25))

        # 📋 Form container
        form_frame = tk.Frame(main_container, bg="white", padx=30, pady=25)
        form_frame.pack(fill="both", expand=True)

        # 🏠 Résidence (now selectable)
        self.residence_var = tk.StringVar()
        self.residence_var.trace_add("write", self.on_residence_change)

        # 🔹 Labels
        tk.Label(
            form_frame,
            text="Select Résidence (French)",
            font=("Arial", 10, "bold"),
            bg="white",
            anchor="center"
        ).grid(row=0, column=0, pady=(5, 5), sticky="ew")

        tk.Label(
            form_frame,
            text="اختر مكان الإقامة",
            font=("Arial", 10, "bold"),
            bg="white",
            anchor="center"
        ).grid(row=0, column=1, pady=(5, 5), sticky="ew")

        # 🔹 Residence fields (mapping Arabic → French)
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

        # French text field (read-only, auto-filled)
        self.residenceF_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=30,
            relief="solid",
            bd=1,
            bg="#F5F5F5",
            justify="center",
            state="readonly"  # ✅ FIX 2: Make it readonly since it auto-fills
        )
        self.residenceF_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Arabic dropdown selection
        self.residence_combo = ttk.Combobox(
            form_frame,
            textvariable=self.residence_var,
            values=residence_options,
            font=("Arial", 11),
            state="readonly",
            justify="center",
            width=30
        )
        self.residence_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # 🏢 Département (Arabic only, hidden by default)
        self.dept_frame = tk.Frame(form_frame, bg="white")
        self.dept_frame.grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")

        tk.Label(
            self.dept_frame,
            text="القسم",
            font=("Arial", 10, "bold"),
            bg="white",
            anchor="center"
        ).pack(side="top", fill="x")

        self.departement_entry = tk.Entry(
            self.dept_frame,
            font=("Arial", 11),
            width=30,
            relief="solid",
            bd=1,
            bg="#F5F5F5",
            justify="center"
        )
        self.departement_entry.pack(side="top", pady=(5, 0))
        self.dept_frame.grid_remove()  # hidden at start

        # 👤 Nom & Prénom
        # ✅ FIX 3: Field order corrected - Arabic label matches Arabic entry
        self.nom_entry, self.NomF_entry = self._create_field_pair(
            form_frame, "اللقب", "Nom", 3
        )
        self.prenom_entry, self.PrenomF_entry = self._create_field_pair(
            form_frame, "الاسم", "Prénom", 4
        )

        # 🎂 Date de naissance
        date_frame = tk.Frame(form_frame, bg="white")
        date_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

        tk.Label(
            date_frame, text="تاريخ الميلاد",
            font=("Arial", 10, "bold"), bg="white", anchor="center"
        ).pack(side="top", fill="x", pady=(0, 5))

        self.date_naissance_entry = DateEntry(
            date_frame,
            width=20,
            background='darkblue',
            foreground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.date_naissance_entry.set_date(date.today())
        self.date_naissance_entry.pack(side="top", pady=(5, 0))

        # 💼 Grade
        self.grade_entry, self.gradeF_entry = self._create_field_pair(
            form_frame, "الرتبة", "Grade", 6
        )

        # 🏛️ Poste supérieur
        self.poste_entry, self.posteF_entry = self._create_field_pair(
            form_frame, "المنصب الأعلى", "Poste supérieur", 7
        )

        # ⏱ Ancien congé
        self._create_single_field(form_frame, "العطلة القديمة (بالأيام)", 8)

        # 🎯 Buttons
        self.create_buttons(form_frame)

    # 🧠 When residence changes → fill French automatically + toggle dept
    def on_residence_change(self, *args):
        residence_ar = self.residence_var.get().strip()

        # 1️⃣ Auto-fill French translation
        french_value = self.residence_map.get(residence_ar, "")
        
        # ✅ FIX 4: Properly update readonly field
        self.residenceF_entry.config(state="normal")
        self.residenceF_entry.delete(0, tk.END)
        self.residenceF_entry.insert(0, french_value)
        self.residenceF_entry.config(state="readonly")

        # 2️⃣ Show/hide department field if needed
        if residence_ar == "مديرية الخدمات الجامعية":
            self.dept_frame.grid()
        else:
            self.dept_frame.grid_remove()
            self.departement_entry.delete(0, tk.END)

    # 🧱 Field pair helper (Arabic + French)
    def _create_field_pair(self, parent, label_ar, label_fr, row, textvariable=None):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")

        # 🇫🇷 French field (LEFT side)
        left = tk.Frame(frame, bg="white")
        left.pack(side="left", fill="x", expand=True, padx=(0, 30))
        tk.Label(
            left, 
            text=label_fr, 
            font=("Arial", 10, "bold"), 
            bg="white", 
            anchor="w"
        ).pack(side="top", fill="x")
        entry_fr = tk.Entry(
            left, 
            font=("Arial", 11), 
            width=25, 
            relief="solid", 
            bd=1, 
            bg="#F5F5F5"
        )
        entry_fr.pack(side="top", fill="x", pady=(5, 0))

        # 🇸🇦 Arabic field (RIGHT side)
        right = tk.Frame(frame, bg="white")
        right.pack(side="right", fill="x", expand=True, padx=(30, 0))
        tk.Label(
            right, 
            text=label_ar, 
            font=("Arial", 10, "bold"), 
            bg="white", 
            anchor="e"
        ).pack(side="top", fill="x")
        args = {
            "font": ("Arial", 11), 
            "width": 25, 
            "relief": "solid", 
            "bd": 1, 
            "bg": "#F5F5F5"
        }
        if textvariable:
            args["textvariable"] = textvariable
        entry_ar = tk.Entry(right, **args)
        entry_ar.pack(side="top", fill="x", pady=(5, 0))

        return entry_ar, entry_fr

    # 🧱 Arabic-only field
    def _create_single_field(self, parent, label_ar, row):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")

        tk.Label(
            frame, 
            text=label_ar, 
            font=("Arial", 10, "bold"), 
            bg="white"
        ).pack(side="top", fill="x")
        self.ancien_entry = tk.Entry(
            frame, 
            font=("Arial", 11), 
            width=30, 
            relief="solid", 
            bd=1, 
            bg="#F5F5F5", 
            justify="center"
        )
        self.ancien_entry.pack(side="top", pady=(5, 0))

    # 🧱 Buttons
    def create_buttons(self, parent):
        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.grid(row=9, column=0, columnspan=2, pady=25)

        tk.Button(
            btn_frame, 
            text="إضافة", 
            command=self.add_employe_action,
            bg="#4CAF50", 
            fg="white", 
            font=("Arial", 12, "bold"),
            padx=25, 
            pady=10, 
            relief="flat", 
            cursor="hand2", 
            width=15
        ).pack(side="left", padx=15)

        tk.Button(
            btn_frame, 
            text="مسح", 
            command=self.clear_fields,
            bg="#757575", 
            fg="white", 
            font=("Arial", 12, "bold"),
            padx=25, 
            pady=10, 
            relief="flat", 
            cursor="hand2", 
            width=15
        ).pack(side="left", padx=15)

    # ✅ Validation - FIX 5: Check correct field names
    def validate_fields(self, data):
        errors = []
        
        if not data["residence"] or not data["residenceF"]:
            errors.append("يرجى اختيار مكان الإقامة")
        
        if data["residence"] == "مديرية الخدمات الجامعية" and not data["departement"]:
            errors.append("الرجاء إدخال القسم")
        
        if not data["nom"]:
            errors.append("الرجاء إدخال اللقب (عربي)")
        
        if not data["NomF"]:
            errors.append("الرجاء إدخال اللقب (فرنسي) - Nom")
        
        if not data["prenom"]:
            errors.append("الرجاء إدخال الاسم (عربي)")
        
        if not data["prenomF"]:
            errors.append("الرجاء إدخال الاسم (فرنسي) - Prénom")
        
        return errors

    # ✅ Add employee - FIX 6: Correct field mapping
    def add_employe_action(self):
        date_value = self.date_naissance_entry.get_date()

        if not date_value:
            messagebox.showerror("خطأ / Erreur", "الرجاء إدخال تاريخ الميلاد")
            return

        data = {
            "residence": self.residence_var.get().strip(),
            "residenceF": self.residenceF_entry.get().strip(),
            "departement": self.departement_entry.get().strip(),
            "nom": self.nom_entry.get().strip(),
            "prenom": self.prenom_entry.get().strip(),
            "NomF": self.NomF_entry.get().strip(),
            "prenomF": self.PrenomF_entry.get().strip(),  # ✅ FIX 7: Correct spelling
            "date_naissance": date_value.strftime("%Y-%m-%d"),
            "grade": self.grade_entry.get().strip(),
            "gradeF": self.gradeF_entry.get().strip(),
            "poste_superieur": self.poste_entry.get().strip(),
            "poste_superieurF": self.posteF_entry.get().strip(),
            "ancien_conges": self.ancien_entry.get().strip()
        }

        errors = self.validate_fields(data)
        if errors:
            messagebox.showwarning("تحذير / Attention", "\n".join(errors))
            return

        # ✅ FIX 8: Better number validation
        try:
            if data["ancien_conges"]:
                data["ancien_conges"] = int(data["ancien_conges"])
            else:
                data["ancien_conges"] = 0
        except ValueError:
            messagebox.showwarning(
                "تحذير / Attention", 
                "يجب أن يكون عدد أيام العطلة القديمة رقماً صحيحاً"
            )
            return

        try:
            success = add_employe(**data)
            if success:
                messagebox.showinfo("نجاح / Succès", "✓ تمت إضافة الموظف بنجاح")
                self.clear_fields()
                
                # ✅ FIX 9: Call on_success callback if provided
                if self.on_success:
                    self.on_success()
                
                # ✅ FIX 10: Publish event (with error handling)
                try:
                    publish("employe_added")
                except Exception as e:
                    print(f"Warning: Could not publish event: {e}")
            else:
                messagebox.showerror("خطأ / Erreur", "✗ فشل في إضافة الموظف")
        except Exception as e:
            messagebox.showerror("خطأ / Erreur", f"حدث خطأ غير متوقع: {str(e)}")

    # 🧹 Clear all inputs - FIX 11: Also clear combobox properly
    def clear_fields(self):
        """Clear all form fields"""
        # Clear residence fields
        self.residence_combo.set("")
        self.residenceF_entry.config(state="normal")
        self.residenceF_entry.delete(0, tk.END)
        self.residenceF_entry.config(state="readonly")
        
        # Clear department
        self.departement_entry.delete(0, tk.END)
        self.dept_frame.grid_remove()
        
        # Clear other entries
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                self.clear_frame_entries(widget)
        
        # Reset date
        self.date_naissance_entry.set_date(date.today())

    def clear_frame_entries(self, frame):
        """Recursively clear entries in frame"""
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Entry):
                # Skip readonly entries (they're managed separately)
                if str(widget.cget("state")) != "readonly":
                    widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
            elif isinstance(widget, tk.Frame):
                self.clear_frame_entries(widget)