"""
Frontend/Views/Conges/Mai19/mai19.py
"""
from Frontend.Views.Conges.ResidenceBase import ResidenceBase


class Residence19mai(ResidenceBase):
    def __init__(self, parent):
        super().__init__(
            parent,
            title         = "الإقامة الجامعية 19 ماي 1956",
            subtitle      = "مرحبا بك في صفحة إقامة 19 ماي. يمكنك إدارة الموظفين من هنا.",
            residence_key = "mai1956",
        )
