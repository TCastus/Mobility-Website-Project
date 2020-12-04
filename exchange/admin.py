from django.contrib import admin

from .models import Country, City, University, UniversityPlaces, UniversityContractsAdmin, \
    UniversityContractsStudent, UniversityLanguages, Student, \
    Department, FinancialAid, Exchange

admin.site.register(Country)
admin.site.register(City)
admin.site.register(University)
admin.site.register(UniversityPlaces)
admin.site.register(UniversityContractsAdmin)
admin.site.register(UniversityContractsStudent)
admin.site.register(UniversityLanguages),
admin.site.register(Student),
admin.site.register(Department),
admin.site.register(FinancialAid),
admin.site.register(Exchange)
