from Frontend.Views.Conges.ResidenceBase import ResidenceBase
class ResidenceHassania2000(ResidenceBase):
    def __init__(self, parent):
        super().__init__(
            parent,
            title         = "الإقامة الجامعية الحسنية 2000 سرير",
            subtitle      = "مرحبا بك في صفحة إقامة الحسنية 2000 سرير.",
            residence_key = "hassania_2000",
        )