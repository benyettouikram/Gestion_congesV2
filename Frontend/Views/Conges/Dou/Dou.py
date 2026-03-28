from Frontend.Views.Conges.ResidenceBase import ResidenceBase

class ResidenceDou(ResidenceBase):
    def __init__(self, parent):
        super().__init__(
            parent,
            title         = "مديرية الخدمات الجامعية",
            subtitle      = "مرحبا بك في صفحة المديرية. يمكنك إدارة الموظفين من هنا.",
            residence_key = "dou",
        )