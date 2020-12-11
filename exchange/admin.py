from django.contrib import admin

from .models import (
    Country,
    City,
    University,
    ExchangeOffer,
    UniversityContractAdmin,
    UniversityContractStudent,
    UniversityLanguages,
    Student,
    Department,
    FinancialAid,
    Exchange,
)

admin.site.register(Country)
admin.site.register(City)
admin.site.register(University)
admin.site.register(ExchangeOffer)
admin.site.register(UniversityContractAdmin)
admin.site.register(UniversityContractStudent)
admin.site.register(UniversityLanguages),
admin.site.register(Student),
admin.site.register(Department),
admin.site.register(FinancialAid),
admin.site.register(Exchange)
