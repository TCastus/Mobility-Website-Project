from django.db import models

from .consts import *


class Country(models.Model):
    name = models.CharField(max_length=100)
    continent = models.CharField(max_length=30, choices=CONTINENTS)
    ECTSConversion = models.FloatField(default=0)  # 1 crédit du pays concerné vaut x crédits ECTS

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class University(models.Model):
    name = models.CharField(max_length=1000)
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    website = models.URLField(blank=True)

    # Utilisation des coordonnées pour afficher les POI sur la carte interactive
    latitude = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)

    rank_metric = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    life_metric = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    CWUR_rank = models.IntegerField(null=True, blank=True)

    demand = models.IntegerField(default=0)
    project = models.BooleanField(default=False)
    can_split_year = models.BooleanField(default=False)

    # TODO : make a ManyToManyField out of this mess
    AvailableForBS = models.BooleanField(default=False)
    AvailableForGCU = models.BooleanField(default=False)
    AvailableForGE = models.BooleanField(default=False)
    AvailableForGEN = models.BooleanField(default=False)
    AvailableForGI = models.BooleanField(default=False)
    AvailableForGM = models.BooleanField(default=False)
    AvailableForIF = models.BooleanField(default=False)
    AvailableForSGM = models.BooleanField(default=False)
    AvailableForTC = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ExchangeOffer(models.Model):
    university = models.ForeignKey('University', on_delete=models.CASCADE)
    duration = models.CharField(max_length=200, choices=DURATION)
    available_places = models.IntegerField(default=0)
    exclusive = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)


# TODO : merge admin and student into one class
class UniversityContractAdmin(models.Model):
    contract_type = models.CharField(max_length=200, choices=CONTRACTS, default="X")
    university = models.ForeignKey('University', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.contract_type) + " at " + self.university.name


class UniversityContractStudent(models.Model):
    contract_type = models.CharField(max_length=200, choices=CONTRACTS, default="X")
    university = models.ForeignKey('University', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.contract_type) + " at " + self.university.name


class UniversityLanguages(models.Model):
    university = models.ForeignKey('University', on_delete=models.CASCADE)
    language = models.CharField(max_length=50, default="")
    diploma_language = models.CharField(max_length=200, null=True, blank=True, )
    language_level = models.CharField(max_length=10, choices=LEVEL, null=True, blank=True, default="X", )

    def __str__(self):
        return str(self.language) + " for " + self.university.name


class Department(models.Model):
    university = models.ForeignKey('University', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    rank = models.IntegerField(default=1,
                               help_text="Utilisez une valeur entre 1 et 5, 1 étant la plus basse et 5 la plus haute.")

    class Meta:
        permissions = (("noter_depart", "Creer et noter un département d'une université"),)

    def __str__(self):
        return str(self.name) + " at " + self.university.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(default="prenom.nom@insa-lyon.fr",
                              help_text="Utilisez votre adresse INSA : prenom.nom@insa-lyon.fr")

    INSA_department = models.CharField(max_length=10, choices=DEPARTMENT)
    nationality = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "[" + str(self.INSA_department) + "]" +  str(self.email)


class FinancialAid(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True, default=0)
    received_every = models.CharField(max_length=15, null=True, blank=True, choices=RECEIVED_EVERY)
    exchange = models.ForeignKey('Exchange', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Exchange(models.Model):
    university = models.ForeignKey('University', on_delete=models.CASCADE)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)

    year = models.IntegerField(default=4, choices=YEAR_CHOICE)
    semester = models.IntegerField(default=1, choices=SEMESTER_CHOICE)
    start_date = models.DateField()
    end_date = models.DateField()

    visa = models.BooleanField(default=False)
    visa_months = models.IntegerField(null=True, blank=True, default=0)
    visa_weeks = models.IntegerField(null=True, blank=True, default=0)
    visa_days = models.IntegerField(null=True, blank=True, default=0)

    comment = models.CharField(max_length=10000, null=True, blank=True)
    rent = models.IntegerField(null=True, blank=True, default=0)
    monthly_expenses = models.IntegerField(null=True, blank=True, default=0)

    night_life_grade = models.IntegerField(null=True, blank=True, default=0, choices=GRADE)
    cultural_life_grade = models.IntegerField(null=True, blank=True, default=0, choices=GRADE)
    security_grade = models.IntegerField(null=True, blank=True, default=0, choices=GRADE)


    def __str__(self):
        return str(self.student) + " at " + self.university.name
