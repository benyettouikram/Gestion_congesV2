from Frontend.Views.Conges.ResidenceBase import ResidenceBase
class ResidenceHeni(ResidenceBase):
    def __init__(self, parent):
        super().__init__(
            parent,
            title         = "الإقامة الجامعية هني صالح",
            subtitle      = "مرحبا بك في صفحة إقامة هني صالح.",
            residence_key = "heni",
        )
