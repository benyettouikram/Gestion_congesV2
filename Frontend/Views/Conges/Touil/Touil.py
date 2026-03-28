from Frontend.Views.Conges.ResidenceBase import ResidenceBase
class ResidenceTouil(ResidenceBase):
    def __init__(self, parent):
        super().__init__(
            parent,
            title         = "الإقامة الجامعية طويل عبد القادر",
            subtitle      = "مرحبا بك في صفحة إقامة طويل عبد القادر.",
            residence_key = "Touil",
        )
