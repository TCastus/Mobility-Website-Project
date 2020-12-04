from django import forms

from .models import *


#----------------------RAJOUT D'INFO------------------------
#RajouterInfo1 - Student
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        labels = {
            'name':('Prénom'),
            'surname':('Nom de famille'),
            'INSA_department':('Département INSA'),
            'nationality':('Nationalité')
        }

#RajouterInfo2 - Language
class LangueForm(forms.ModelForm):
    class Meta:
        model = UniversityLanguages
        exclude = ('university',)
   
#RajouterInfo2 -  Departement
class DepForm(forms.Form):
    GRADE = (
        (0,'------'),
		(1, '1'),
		(2, '2'),
		(3, '3'),
		(4, '4'),
		(5, '5')
	)

    NameDep = forms.ModelChoiceField(queryset=Department.objects.none(),label="département de l'université dans lequel l'échange a été effectué",required=False)
    Note = forms.ChoiceField(choices=GRADE,required=False, label="Note du département (/5)",help_text="Notez la qualité de l'enseignement (5 étant la note la plus haute)")

    def __init__(self,qs, *args, **kwargs): 
        super(DepForm, self).__init__(*args, **kwargs) 
        self.fields['NameDep'].queryset = qs


#RajouterInfo3 - Exchange
class ExchForm(forms.ModelForm):
    class Meta:
        model = Exchange
        exclude = ('student', 'university', 'visa',)
        widgets = {
            'comment':forms.Textarea(attrs={'cols': 80, 'rows': 10})
        }

    

#RajouterInfo3 - Exchange (case à cocher)
class ExchFormVisa(forms.ModelForm):
    class Meta:
        model = Exchange
        fields = ('visa',)

#RajouterInfo4 - Aides Finances
class FinancialForm(forms.ModelForm):
    class Meta:
        model = FinancialAid
        exclude = ('exchange',)
        labels = {
            'name':("Nom de la bourse"),
            'amount':("Valeur de la bourse (en €)"),
            'received_every':("S'agit-il d'une valeur mensuelle, hebdomadaire ou journalière ?")
        }

#-----------------RECHERCHE AVANCEE-------------------
#Filtre : continent
class RAcontinentForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ('continent',)
    

#Filtre : Contract
class ContractForm(forms.ModelForm):
    CONTRACTS = (
        ('','---------'),
        ('DD','Double Diplome'),
        ('M','Mobilite')
    )
    ContractType = forms.ChoiceField(choices=CONTRACTS,required=False, label="Type de contrat avec l'INSA")
   
    class Meta:
        model = UniversityContractStudent
        fields = ['contract_type']
       

#Ordonage : 
class OrdreForm(forms.Form):
    ORDRES = (
        ('','------'),
        ('rank_metric','Ranking'),
        ('life_metric','Qualité de Vie'),
        ('name','Pays'),
        ('CWUR_rank','Ranking Mondial'),
        ('Demand','Demande')
    )
    Ordre = forms.ChoiceField(choices=ORDRES, widget=forms.Select(attrs={'class':"required"}))

#------------------PROF: MOFIFIE----------------
#RajouterInfo2 - Department
class DepartForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name', 'rank',)
        labels = {
            'name':("Nom du département de l'université dans lequel l'échange a été effectué"),
            'rank':('Note du département (/5)')
        }

#Modifie Infos Université
class UnivForm(forms.ModelForm):
    class Meta:
        model = University
        fields = ('demand',)
        labels = {
            'demand':('Nombre de demandes (en moyenne)')
        }

class UnivPlacesForm(forms.ModelForm):
    class Meta:
        model = ExchangeOffer
        fields = ('available_places',)
        labels = {
            'available_places':('Nombre de places')
        }

