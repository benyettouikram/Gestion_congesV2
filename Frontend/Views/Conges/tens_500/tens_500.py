from Frontend.Views.Conges.ResidenceBase import ResidenceBase
class ResidenceTens500(ResidenceBase):
    def __init__(self, parent):
        super().__init__(
            parent,
            title         = "الإقامة الجامعية تنس 500 سرير",
            subtitle      = "مرحبا بك في صفحة إقامة تنس 500 سرير.",
            residence_key = "tens_500",
        )