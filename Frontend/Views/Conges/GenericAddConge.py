"""
Frontend/Views/Conges/GenericAddConge.py
─────────────────────────────────────────
Single Add/Update dialog shared by ALL 10 residences.

Usage (from ResidenceBase)
──────────────────────────
    GenericAddConge(
        parent,
        employe            = employe_dict,
        residence_required = self.residence_ar,   # Arabic string
        on_save_callback   = self.refresh_data,
    )

    GenericAddConge(
        parent,
        employe            = employe_dict,
        conge_data         = conge_dict,           # triggers UPDATE mode
        residence_required = self.residence_ar,
        on_save_callback   = self.refresh_data,
    )
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta

from Frontend.Theme.colors import PRIMARY_COLOR
from Frontend.Utils.event_bus import publish

# ── Generic backend (write) ────────────────────────────────────────────────────
from Bakend.models.Conges.GenericConge import (
    insert_conge,
    update_conge,
    get_conge_periodes,
)
from Bakend.models.Conges.conge_validations import (
    check_employe_has_conge_en_cours,
    validate_conge_solde,
)
from Bakend.models.Conges.GenericResidence import (
    get_conge_by_employe_id,
)


class GenericAddConge(tk.Toplevel):
    """Add / Update congé dialog — works for all 10 residences."""

    # One instance at a time across the whole app
    _current_instance = None

    def __init__(
        self,
        parent,
        employe            = None,
        conge_data         = None,
        on_save_callback   = None,
        residence_required = None,   # Arabic string e.g. "الاقامة الجامعية 19 ماي 1956"
    ):
        # ── Singleton guard ────────────────────────────────────────────────
        if GenericAddConge._current_instance is not None:
            try:
                GenericAddConge._current_instance.lift()
                GenericAddConge._current_instance.focus()
                return
            except tk.TclError:
                pass   # previous window was destroyed

        super().__init__(parent)
        GenericAddConge._current_instance = self

        # ── State ──────────────────────────────────────────────────────────
        self.is_update_mode    = conge_data is not None
        self.conge_data        = conge_data or {}
        self.employe           = employe or {}
        self.id_employe        = self.employe.get("id_employe")
        self.id_conge          = self.conge_data.get("id_conge")
        self.on_save_callback  = on_save_callback
        self.residence_required = residence_required   # Arabic string used by insert_conge

        self.periodes_conge  = []
        self.periodes_frame  = None
        self.periode_listbox = None

        self.geometry("750x850")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.withdraw()  # hide window until position is fixed

        # ── Tk variables ───────────────────────────────────────────────────
        self.nom_var        = tk.StringVar(value=self.employe.get("nom",    "غير معروف"))
        self.prenom_var     = tk.StringVar(value=self.employe.get("prenom", "غير معروف"))
        self.grade_var      = tk.StringVar(value=self.employe.get("grade",  "غير معروف"))
        self.type_conge_var = tk.StringVar(value=self.conge_data.get("type_conge", "سنوية"))
        self.nbr_jours_var  = tk.StringVar(value=str(self.conge_data.get("nb_jours", "")))
        self.lieu_var       = tk.StringVar(value=self.conge_data.get("lieu", ""))

        self.colors = {
            "bg":          "#f5f6fa",
            "card":        "#FFFFFF",
            "header":      PRIMARY_COLOR,
            "header_text": "#FFFFFF",
            "submit":      PRIMARY_COLOR,
            "cancel":      "#e74c3c",
            "border":      "#e0e0e0",
        }

        # ⚡ BUILD UI IMMEDIATELY (before DB queries)
        self._apply_styles()
        self._build_ui()

        # ⚡ CENTER AFTER UI IS BUILT (with proper timing)
        self.after(10, self._center)  # Small delay to ensure UI is fully rendered

        # ⚡ RUN VALIDATIONS IN BACKGROUND (non-blocking)
        self.after(100, self._async_validate_and_load)

    # =========================================================================
    #  STYLES
    # =========================================================================

    def _apply_styles(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("Header.TFrame",  background=self.colors["header"])
        s.configure("Header.TLabel",  background=self.colors["header"],
                    foreground=self.colors["header_text"], font=("Arial", 18, "bold"))
        s.configure("Card.TFrame",    background=self.colors["card"])
        s.configure("CardTitle.TLabel", background=self.colors["card"],
                    foreground="#000", font=("Arial", 14, "bold"))
        s.configure("Label.TLabel",   background=self.colors["card"],
                    foreground="#000", font=("Segoe UI Semibold", 11))

        for name, color in (("Submit", self.colors["submit"]),
                            ("Cancel", self.colors["cancel"])):
            s.configure(f"{name}.TButton", font=("Arial", 11, "bold"),
                        background=color, foreground="#fff")
            s.map(f"{name}.TButton",
                  background=[("active", color)],
                  foreground=[("active", "#fff")])

    # =========================================================================
    #  UI BUILDING
    # =========================================================================

    def _build_ui(self):
        self.configure(bg=self.colors["bg"])
        self._build_header()
        container = tk.Frame(self, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        self._build_employee_card(container)
        self._build_conge_card(container)
        self._build_buttons(container)

    def _build_header(self):
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill=tk.X)
        title = "تعديل عطلة" if self.is_update_mode else "إضافة عطلة"
        ttk.Label(header, text=title, style="Header.TLabel").pack(pady=15)

    def _build_employee_card(self, parent):
        card = tk.Frame(parent, bg=self.colors["card"],
                        highlightbackground=self.colors["border"], highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 15))
        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill=tk.BOTH, padx=20, pady=15)
        for i in range(4):
            content.columnconfigure(i, weight=1)

        ttk.Label(content, text="معلومات الموظف", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="e", pady=(0, 15))

        # Row 1: nom / prenom
        ttk.Label(content, text="اللقب",  style="Label.TLabel").grid(row=1, column=3, sticky="e", padx=5, pady=8)
        ttk.Entry(content, textvariable=self.nom_var,    state="readonly", justify="right", width=22).grid(row=1, column=2, sticky="e", padx=(5, 20), pady=8)
        ttk.Label(content, text="الإسم",  style="Label.TLabel").grid(row=1, column=1, sticky="e", padx=5, pady=8)
        ttk.Entry(content, textvariable=self.prenom_var, state="readonly", justify="right", width=22).grid(row=1, column=0, sticky="e", padx=(5, 20), pady=8)

        # Row 2: grade
        ttk.Label(content, text="الرتبة", style="Label.TLabel").grid(row=2, column=3, sticky="e", padx=5, pady=8)
        ttk.Entry(content, textvariable=self.grade_var,  state="readonly", justify="right", width=22).grid(row=2, column=2, sticky="e", padx=(5, 20), pady=8)

    def _build_conge_card(self, parent):
        card = tk.Frame(parent, bg=self.colors["card"],
                        highlightbackground=self.colors["border"], highlightthickness=1)
        card.pack(fill=tk.X)
        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill=tk.BOTH, padx=20, pady=15)
        for i in range(4):
            content.columnconfigure(i, weight=1)

        ttk.Label(content, text="تفاصيل العطلة", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="e", pady=(0, 15))

        # Row 1: type
        ttk.Label(content, text="نوع العطلة", style="Label.TLabel").grid(row=1, column=3, sticky="e", padx=5, pady=8)
        ttk.Combobox(content, textvariable=self.type_conge_var,
                     values=["سنوية", "مرضية", "استثنائية"],
                     state="readonly", justify="right", width=22).grid(row=1, column=2, sticky="e", padx=(5, 20), pady=8)

        # Row 2: date_debut / nb_jours
        ttk.Label(content, text="تاريخ البداية", style="Label.TLabel").grid(row=2, column=3, sticky="e", padx=5, pady=8)
        self.date_debut = DateEntry(content, width=22, date_pattern="dd/mm/yyyy")
        self.date_debut.grid(row=2, column=2, sticky="e", padx=(5, 20), pady=8)

        ttk.Label(content, text="عدد الأيام", style="Label.TLabel").grid(row=2, column=1, sticky="e", padx=5, pady=8)
        ttk.Entry(content, textvariable=self.nbr_jours_var, justify="right", width=22).grid(row=2, column=0, sticky="e", padx=(5, 20), pady=8)

        # Row 3: date_fin / lieu
        ttk.Label(content, text="تاريخ النهاية", style="Label.TLabel").grid(row=3, column=3, sticky="e", padx=5, pady=8)
        self.date_fin = DateEntry(content, width=22, date_pattern="dd/mm/yyyy")
        self.date_fin.grid(row=3, column=2, sticky="e", padx=(5, 20), pady=8)

        ttk.Label(content, text="المكان", style="Label.TLabel").grid(row=3, column=1, sticky="e", padx=5, pady=8)
        ttk.Combobox(content, textvariable=self.lieu_var,
                     values=["داخل التراب الوطني", "خارج التراب الوطني"],
                     state="readonly", justify="right", width=22).grid(row=3, column=0, sticky="e", padx=(5, 20), pady=8)

        # Row 4: add period button
        ttk.Button(content, text="➕ إضافة فترة عطلة",
                   command=self._add_periode).grid(row=4, column=0, columnspan=4, pady=15)

        # Row 5: period list (hidden until a period is added)
        self.periodes_frame = tk.Frame(content, bg=self.colors["card"])
        self.periodes_frame.grid(row=5, column=0, columnspan=4, sticky="ew")
        self.periode_listbox = tk.Listbox(self.periodes_frame, width=50, justify="right")
        self.periode_listbox.pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.periodes_frame, text="حذف الفترة",
                   command=self._remove_periode).pack(side=tk.LEFT, padx=5)
        self.periodes_frame.grid_remove()   # hidden initially

        # Auto-calculate end date from start + days
        self.nbr_jours_var.trace_add("write", self._calculate_date_fin)
        self.date_debut.bind("<<DateEntrySelected>>", self._calculate_date_fin)

    def _build_buttons(self, parent):
        btns = tk.Frame(parent, bg=self.colors["bg"])
        btns.pack(pady=20)
        ttk.Button(btns, text="إلغاء", style="Cancel.TButton",
                   command=self.destroy).grid(row=0, column=0, padx=10, ipadx=20, ipady=8)
        ttk.Button(btns, text="تأكيد", style="Submit.TButton",
                   command=self._save).grid(row=0, column=1, padx=10, ipadx=20, ipady=8)

    # =========================================================================
    #  PERIOD MANAGEMENT
    # =========================================================================

    def _calculate_date_fin(self, *args):
        try:
            debut    = self.date_debut.get_date()
            nb_jours = int(self.nbr_jours_var.get())
            if nb_jours > 0:
                self.date_fin.set_date(debut + timedelta(days=nb_jours - 1))
        except Exception:
            pass

    def _add_periode(self):
        debut = self.date_debut.get_date()
        fin   = self.date_fin.get_date()
        if fin < debut:
            messagebox.showerror("خطأ", "تاريخ النهاية يجب أن يكون بعد تاريخ البداية")
            return
        self.periodes_conge.append((debut, fin))
        self.periodes_frame.grid()
        self.periode_listbox.insert(tk.END, f"{debut.strftime('%d/%m/%Y')} → {fin.strftime('%d/%m/%Y')}")
        self._update_total_days()

    def _load_existing_periodes(self):
        """Load periods from DB when opening in UPDATE mode."""
        try:
            periodes_db = get_conge_periodes(self.id_conge)
            if not periodes_db:
                print(f"⚠️ Aucune période pour id_conge={self.id_conge}")
                return
            for periode in periodes_db:
                debut = datetime.strptime(periode[0], "%Y-%m-%d").date()
                fin   = datetime.strptime(periode[1], "%Y-%m-%d").date()
                self.periodes_conge.append((debut, fin))
                self.periode_listbox.insert(tk.END, f"{debut.strftime('%d/%m/%Y')} → {fin.strftime('%d/%m/%Y')}")
            if self.periodes_conge:
                self.periodes_frame.grid()
                self._update_total_days()
                self.date_debut.set_date(self.periodes_conge[0][0])
                self.date_fin.set_date(self.periodes_conge[0][1])
        except Exception as e:
            print(f"❌ _load_existing_periodes: {e}")
            messagebox.showerror("خطأ", f"خطأ في تحميل الفترات: {e}")

    def _remove_periode(self):
        sel = self.periode_listbox.curselection()
        if sel:
            self.periode_listbox.delete(sel[0])
            self.periodes_conge.pop(sel[0])
            self._update_total_days()
            if not self.periodes_conge:
                self.periodes_frame.grid_remove()

    def _update_total_days(self):
        total = sum((fin - debut).days + 1 for debut, fin in self.periodes_conge)
        self.nbr_jours_var.set(str(total))

    # =========================================================================
    #  SAVE
    # =========================================================================

    def _save(self):
        if not self.id_employe:
            messagebox.showerror("خطأ", "الموظف غير معروف")
            return
        if not self.lieu_var.get():
            messagebox.showerror("خطأ", "يجب اختيار مكان العطلة")
            return

        # Gather periods
        if not self.periodes_conge:
            try:
                debut = self.date_debut.get_date()
                fin   = self.date_fin.get_date()
                if fin < debut:
                    messagebox.showerror("خطأ", "تاريخ النهاية يجب أن يكون بعد تاريخ البداية")
                    return
                periodes_to_save = [(debut, fin)]
            except Exception:
                messagebox.showerror("خطأ", "يرجى التحقق من التواريخ")
                return
        else:
            periodes_to_save = self.periodes_conge

        total_jours = sum((fin - debut).days + 1 for debut, fin in periodes_to_save)

        # Validate balance
        id_conge_to_exclude = self.id_conge if self.is_update_mode else None
        is_valid, message, _ = validate_conge_solde(self.id_employe, total_jours, id_conge_to_exclude)
        if not is_valid:
            messagebox.showerror("⚠️ رصيد غير كافٍ", message)
            return
        if not messagebox.askyesno("تأكيد العطلة", f"{message}\n\nهل تريد المتابعة؟"):
            return

        # Persist
        if self.is_update_mode:
            if not self.id_conge:
                messagebox.showerror("خطأ", "معرّف العطلة غير صالح")
                return
            print(f"🔄 UPDATE congé id={self.id_conge}, employe={self.id_employe}")
            success, msg = update_conge(
                id_conge   = self.id_conge,
                id_employe = self.id_employe,
                type_conge = self.type_conge_var.get(),
                periodes   = periodes_to_save,
                lieu       = self.lieu_var.get(),
            )
        else:
            print(f"➕ INSERT congé employe={self.id_employe}, résidence='{self.residence_required}'")
            success, msg = insert_conge(
                id_employe         = self.id_employe,
                type_conge         = self.type_conge_var.get(),
                periodes           = periodes_to_save,
                lieu               = self.lieu_var.get(),
                residence_required = self.residence_required,  # ← dynamic
            )

        if not success:
            messagebox.showerror("خطأ", msg)
            return

        messagebox.showinfo("نجاح", msg)

        if self.on_save_callback:
            self.on_save_callback()

        try:
            publish("conge_saved", id_conge=self.id_conge, id_employe=self.id_employe)
        except Exception:
            pass

        self.after(500, self._on_closing)

    # =========================================================================
    #  HELPERS
    # =========================================================================

    def _center(self):
        """Center the window on screen with fixed size."""
        # Force window to update
        self.update()

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Fixed window size (as set in __init__)
        window_width = 750
        window_height = 850

        # Calculate center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Ensure position is not negative
        x = max(0, x)
        y = max(0, y)

        # Set geometry with size and position
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.deiconify()  # show the window only after it is centered

        # Alternative: Use Tkinter's built-in centering
        # self.eval('tk::PlaceWindow %s center' % self.winfo_pathname(self.winfo_id()))

    def _on_closing(self):
        GenericAddConge._current_instance = None
        self.destroy()

    # =========================================================================
    #  ⚡ ASYNC VALIDATION & LOADING (Non-blocking)
    # =========================================================================

    def _async_validate_and_load(self):
        """
        Run expensive DB queries AFTER form is visible (non-blocking).
        If employee has existing congé in ADD mode, automatically load it.
        """
        try:
            # ── Check if employee already has a congé (INSERT mode only) ────
            if not self.is_update_mode:
                has_conge, conge_info = check_employe_has_conge_en_cours(self.id_employe)
                if has_conge:
                    # ✅ Auto-load existing congé data
                    conge_data = get_conge_by_employe_id(self.id_employe)
                    if conge_data:
                        # Switch to UPDATE mode automatically
                        self.is_update_mode = True
                        self.id_conge = conge_data.get("id_conge")
                        self.conge_data = conge_data
                        
                        # Update header
                        self._update_header_to_update_mode()
                        
                        # Load existing periods
                        self._load_existing_periodes()
                        
                        # Inform user
                        messagebox.showinfo(
                            "تنويه",
                            f"✅ تم تحميل العطلة الموجودة تلقائياً\n\n"
                            f"نوع العطلة: {conge_info['type_conge']}\n"
                            f"من: {conge_info['date_debut']}  إلى: {conge_info['date_fin']}\n"
                            f"الأيام: {conge_info['nb_jours']}\n\n"
                            f"يمكنك الآن تعديلها مباشرة من هنا"
                        )
                    else:
                        messagebox.showwarning(
                            "تنبيه",
                            "هذا الموظف لديه عطلة بالفعل، لكن لم يتم العثور على بيانات العطلة"
                        )
                        self._on_closing()
                        return

            # ── Load existing periods (UPDATE mode only) ────────────────────
            elif self.is_update_mode and self.id_conge:
                self._load_existing_periodes()

        except Exception as e:
            print(f"❌ _async_validate_and_load: {e}")
            import traceback; traceback.print_exc()

    def _update_header_to_update_mode(self):
        """Update the header to show UPDATE mode."""
        try:
            # Find and update the header label
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Label):
                            try:
                                text = child.cget("text")
                                if text == "إضافة عطلة":
                                    child.config(text="تعديل عطلة")
                                    break
                            except:
                                pass
        except Exception as e:
            print(f"⚠️ _update_header_to_update_mode: {e}")