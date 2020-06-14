from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import *
from .models import *
from django.db.models import Avg, Func
import datetime
from collections import defaultdict

#pour l'authentification
from django_cas_ng.signals import cas_user_authenticated #signal
from django.contrib.auth.decorators import login_required,permission_required,user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Permission

months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

def day_month_conversion(day_of_year):
	d = datetime.datetime.strptime(str(day_of_year), "%j")
	day = d.strftime("%#d")
	month = d.strftime("%#m")
	return(day+" "+months[int(month)-1])
 
def visa_duration(day, week, month):
	d, w, m = "", "", ""
	if day > 1:
		d = str(day)+" jours"
	elif day == 1:
		d = str(day)+" jour"

	if week > 1:
		w = str(week)+" semaines"
	elif week == 1:
		w = str(week)+" semaine"

	if month != 0:
		m = str(month)+" mois"

	if d != "" and w != "" and m != "":
		return d+", "+w+" et "+m
	elif d != "" and w != "":
		return d+" et "+w
	elif w != "" and m != "":
		return w+" et "+m
	elif d != "":
		return d
	elif w != "":
		return w
	elif m != "":
		return m

def duplicates_in_fin(list_to_check):
    tally = defaultdict(list)
    for index, item in enumerate(list_to_check):
        tally[item].append(index)
    return ((key,locs) for key,locs in tally.items() if len(locs)>1)

class Round(Func):
	function = 'ROUND'
	template='%(function)s(%(expressions)s, 2)'

def base(request):
	return render(request, 'exchange/base.html')

def user(request):
	return render(request, 'exchange/user.html')

#--------------------------------PAGE D'ACCUEIL-----------------------------------
# Actualisation de rankMetrique
def actualiserMetrique1():
	#moyenne des différent Rank pour chaque Department de Chaque Univ
	metrique_Depa = Department.objects.values_list('University').annotate(Avg('Rank'))
  
	#insère la valeur dans l'université
	for elem in metrique_Depa:
		instance = University.objects.get(ID=elem[0])
		instance.RankMetric = elem[1]
		instance.save()

# Actualisation de lifeMetric
def actualiserMetrique2():
	#moyenne des différent Rank pour chaque Department de Chaque Univ
	metrique2_Depa = Exchange.objects.values_list('University').annotate(Avg('CulturalLifeGrade'),Avg('NightLifeGrade'),Avg('Security'))#mettre le cout de la vie aussi
  
	#insère la valeur dans l'université
	for elem in metrique2_Depa:
		instance = University.objects.get(ID=elem[0])
		instance.LifeMetric = ((elem[1]+elem[2]+elem[3])/3)
		instance.save()


def home(request):
	#requete pour donner toutes les universitées
	Univ_list = University.objects.all()

	#actualise les métriques
	actualiserMetrique1()
	actualiserMetrique2()

	return render(request, 'exchange/home.html', locals())


#-----------------------PAGE D'UNE UNIVERSITE (PAR ID)-----------------
def university(request, idUni):
	#Requetes vers BD:
	univ = University.objects.get(pk=idUni)
	cont = UniversityContractsStudent.objects.filter(University=univ)
	langue = UniversityLanguages.objects.filter(University=univ).exclude(Language="Inconnu").distinct()
	ex = Exchange.objects.filter(University=univ)
	pl = UniversityPlaces.objects.filter(University=univ)
	S1 = ex.filter(Semester=1) #renvoie le premier élément de "ex" pour Semestre 1
	S2 = ex.filter(Semester=2) #renvoie le premier élément de "ex" pour Semestre 2
	
	# S1 will contain 0 or multiple Exchange objects in a QuerySet
	# Check if there is a need for a Visa anywhere
	s1_start, s1_end, s2_start, s2_end = 0, 0, 0, 0
	s1_start_date, s1_end_date, s2_start_date, s2_end_date = "Pas d'information", "Pas d'information", "Pas d'information", "Pas d'information"
	visa = []
	if S1:
		for e in S1:
			s1_start += int(e.StartDate.strftime("%j")) # <-- Gives the day of the year of that specific datetime.date object
			s1_end += int(e.EndDate.strftime("%j"))
			visa.append(e.Visa)
		
		s1_start_date = day_month_conversion(round(s1_start/len(S1)))
		s1_end_date = day_month_conversion(round(s1_end/len(S1)))
	
	if S2:
		for e in S2:
			s2_start += int(e.StartDate.strftime("%j"))
			s2_end += int(e.EndDate.strftime("%j"))
			visa.append(e.Visa)
		
		s2_start_date = day_month_conversion(round(s2_start/len(S2)))
		s2_end_date = day_month_conversion(round(s2_end/len(S2)))
	
	# Round the average value
	# Find a way to turn a value between 1 and 366 to a dd-MM format
	visa_days, visa_weeks, visa_months = 0, 0, 0
	day_count, week_count, month_count = 0, 0, 0	
	visa_text = ""
 
	if True in visa:
		for e in ex:
			if e.VisaDays != -1:
				day_count += 1
				visa_days += e.VisaDays
			if e.VisaWeeks != -1:
				week_count += 1
				visa_weeks += e.VisaWeeks
			if e.VisaMonths != -1:
				month_count += 1
				visa_months += e.VisaMonths
				
		visa_days = round(visa_days/day_count)
		visa_weeks = round(visa_weeks/week_count)
		visa_months = round(visa_months/month_count)
		
		visa_text = visa_duration(visa_days, visa_weeks, visa_months)
	else:
		visa_text = "Visa non nécessaire"
	
	# Pour avoir toutes les FinancialAid d'une échange "ex"
	fin = FinancialAid.objects.none()
	for e in ex:
		fin = fin | FinancialAid.objects.filter(Exchange=e).exclude(Value=-1)
	
	fin_list = []
	fin_filtered = fin.values("Name", "ReceivedEvery").annotate(avg_value=Avg("Value"))
	
	# temp NE DOIS JAMAIS ETRE SAUVEGARDE!!!!!!!!!!!!
	for f in fin_filtered:
		temp = FinancialAid(Name = f["Name"], Value=f["avg_value"], ReceivedEvery=f["ReceivedEvery"], Exchange=Exchange.objects.first())
		fin_list.append(temp)
	
	
	#la moyenne des différentes notes pour touts les object Exchange d'un Université
	avg = Exchange.objects.filter(University=univ).aggregate(r=Round(Avg('Rent')),m=Round(Avg('MonthlyExpenses')),n=Avg('NightLifeGrade'),c=Avg('CulturalLifeGrade'),s=Avg('Security'))#mettre le cout de la vie aussi

	return render(request, 'exchange/university.html', locals())


#-----------------------PAGE RECHERCHE AVANCEE-----------------
def search(request):
	#Initialisation d'un objets Université pour requête 
	qs = University.objects.none()

	#Initialisation des forms 
	form = RAContinentForm(request.POST or None) 
	formContract = ContractForm(request.POST or None)
	ordre = OrdreForm(request.POST or None)

	#liste de tout les objects Pays
	ttl = Country.objects.all().order_by('CountryName')
	
	#Verifie que le submit est cohérent
	if form.is_valid() and formContract.is_valid() and ordre.is_valid() :
		#prend toutes les valuers
		Continent = form.cleaned_data['Continent']
		CountryName = request.POST.get('CountryName')
		ContractType = formContract.cleaned_data['ContractType']
		ordres = ordre.cleaned_data['Ordre']

		#En fonction des options choisies on fait une requete différente
		universitiesC = UniversityContractsAdmin.objects.filter(University__City__Country__Continent=Continent)     
							#UniversityContractsStudent
			#Si On filtre par pays
		if(CountryName!=""):
			universitiesC = universitiesC.filter(University__City__Country__CountryName=CountryName)

			#Si on filtre par contract
		if(ContractType!=""):
			universitiesC = universitiesC.filter(ContractType=ContractType)

			#Ordre : soit par pays soit par autre
		if(ordres=="CountryName"):
			universitiesC = universitiesC.order_by('University__City__Country__CountryName', 'University__City__CityName')
		else:
			universitiesC = universitiesC.order_by('-University__'+ordres, 'University__City__Country__CountryName', 'University__City__CityName')
		
		#dit qu'on peut afficher la liste des Universités
		valide=True           

	return render(request, 'exchange/search.html', locals())



#---------RAJOUTER INFO--------------------------------
#selection continent
def reviewExchange(request):        
	 return render(request, 'exchange/reviewExchange.html', locals())

#selection pays
def countries(request,continent):
	#donne lsite des objects pays selon le Continent du paramètre de l'URL
	 pays_var = Country.objects.filter(Continent=continent)
	 return render(request, 'exchange/countries.html',locals())

#selection ville
def cities(request,country):
	#donne l'object pays grace à l'URL
	 p = Country.objects.get(pk=country)

	 #donne les villes pour ce pays là
	 ville = City.objects.filter(Country=p)

	 return render(request, 'exchange/cities.html',locals())

#selection univ
def universities(request,city):
	#Obtien l'objet City grave à l'URL
	 v = City.objects.get(pk=city)

	 #donne toutes les universités de cette ville là
	 Uni = University.objects.filter(City=v)

	 return render(request, 'exchange/universities.html',locals())

#rajouter info étape 1:Student
def edit(request,univ):
	#prend l'object Université par l'URL
	 Uni = University.objects.get(pk=univ)
	 univID = Uni.ID

	#Initialise, verifie et prend les info du formulaire pour Student
	 form = StudentForm(request.POST or None)
	 if form.is_valid():
		 #enregistre les info données par le Fomrulaire dans DB
		  student = form.save()

		  #on passera l'ID de l'étudiant dans l'URL
		  studentID = student.ID
		  
		  #redirige vers prochaine page
		  return redirect('/exchange/edit-department-student/'+str(univID)+'/'+str(studentID))

	 return render(request, 'exchange/edit.html', locals())

#rajouter info étape 2:Department et UnivLanguage
def editDepartmentStudent(request,univ,stud):
	#Recupère Université et Student du l'URL
	Uni = University.objects.get(pk=univ)
	Stud = Student.objects.get(pk=stud)
	studentID = Stud.ID
	univID = Uni.ID

	#Forms pour Department et UniversityLanguage
	form2= LangueForm(request.POST or None)

	#Form pour les département de l'université en question
	qs = Department.objects.filter(University=Uni)
	formDep = DepForm(qs)   

	if form2.is_valid():
		#Prend le resultat du form Departement
		idDep = request.POST.get('NameDep')
		note = request.POST.get('Note')
		if(idDep!=""):
			Dep = Department.objects.get(pk=idDep)
			Dep.Rank = note
			Dep.save() #enregistre dans la base de donné

		#enregistre langue dans DB
		lang = form2.save(commit=False)
		lang.University = Uni
		lang.save()

		#redirige vers next form
		return redirect('/exchange/edit-exchange/'+str(univID)+'/'+str(studentID))

	return render(request, 'exchange/editDepartmentStudent.html', locals())

#rajouter info étape 3:Exchange
def editExchange(request,univ,stud):
	#recupère info de URL
	Uni = University.objects.get(pk=univ)
	Stud = Student.objects.get(pk=stud)
	univID = Uni.ID

	#Formulaire pour Exchange
	form = ExchForm(request.POST or None)
	formVisa = ExchFormVisa(request.POST or None)#poue la case à cohcer c'est un cas à part

	if form.is_valid() and formVisa.is_valid():
		Visa = formVisa.cleaned_data['Visa']#case à cocher

		#enregitrer dans la base de donné
		exch = form.save(commit=False)
		exch.University = Uni
		exch.Student = Stud
		exch.Visa = Visa
		exch.save()

		#pour passage de paramètre dans URL
		exchID=exch.ID

		#redirige vers next form
		return redirect('/exchange/edit-financial/'+str(univID)+'/'+str(exchID))

	return render(request, 'exchange/editExchange.html', locals())

#rajouter info étape 4: Aides Finances
def editFinancial(request,univ,exch):
	#recupère données de URL
	Uni = University.objects.get(pk=univ)
	Exch = Exchange.objects.get(pk=exch)
	ExchID = Exch.ID

	#form pour les Aides Finacières
	form = FinancialForm(request.POST or None)
	if form.is_valid():
		Name = form.cleaned_data['Name']
		Value = form.cleaned_data['Value']
		ReceivedEvery = form.cleaned_data['ReceivedEvery']

		#enregistre dans base de donnée
		fin = form.save(commit=False)
		fin.Exchange = Exch
		fin.save()

		#aller vers page d'accueil
		return redirect('/exchange/home')

	return render(request, 'exchange/editFinancial.html', locals())


#----------------AUTHENTIFICATION---------
#Connexion
@login_required(login_url='/accounts/login/')#redirige vers CAS
def exchangeLogin(request):
	 print(request.session['attributes'])#affiche attributs de l'utilisateur
	 user = request.user#prend le user

	 #rajoute permission pour noter info officielles 
	 permission = Permission.objects.get(codename='noter_depart')
	 user.user_permissions.add(permission)
	 #ici faire user.atribuChePa == blabla
	 
	 #reviesn à la page d'accueil
	 return redirect('/exchange/home')

#Renvoie faux si utilisateur est connecté 
def check(user):
	 return not(user.is_authenticated)

#DECONEXION ou sinon CAS_IGNORE_REFERER à true
@user_passes_test(check , login_url='/accounts/logout/')#redirige vers deconnexion CAS
def exchangeLogout(request):
	 logout(request)
	 #HttpResponse(reverse('cas_ng_logout'))
	 #reverse(connexion)
	 #redirige vers accueil
	 return redirect('/exchange/home')


#----------------------PROF : MODIFIE--------------------
#pour la page d'ajout de département
@permission_required('exchange.noter_depart')
def addDepartment(request,univ):
	#Initialisation des forms
	form = DepartForm(request.POST or None)
	formUni = UnivForm(request.POST or None)
	formUniPlaces = UnivPlacesForm(request.POST or None)

	#Reuperation de l'Universite ensuite des département de l'Université
	Uni = University.objects.get(pk=univ)
	departs = Department.objects.filter(University = Uni)
	pl = UniversityPlaces.objects.filter(University = Uni)

	#recupère les données du Form de Départment
	if form.is_valid():
		Name = form.cleaned_data['Name']
		Rank = form.cleaned_data['Rank']

		#Creer un nouveau département dans BD
		depart = Department(Name=Name,University=Uni,Rank=Rank)
		depart.save()
	
	#recupere les donnes du form Université
	if formUni.is_valid():
		Places = formUniPlaces.cleaned_data['Places']
		Demand = formUni.cleaned_data['Demand']

		#modifie les valeurs de l'université
		pl.Places = Places
		Uni.Demand = Demand
		Uni.save()
		pl.save()

	return render(request, 'exchange/addDepartment.html',locals())

#pour la page de modification d'un département
@permission_required('exchange.noter_depart')
def editDepartment(request,dep):
	#recupère le départ de l'URL
	form = DepartForm(request.POST or None)
	depart = Department.objects.get(pk = dep)

	#recupère info du fom de Départment
	if form.is_valid():
		Name = form.cleaned_data['Name']
		Rank = form.cleaned_data['Rank']

		#modifie les valeurs
		depart.Name = Name
		depart.Rank = Rank
		depart.save()

		#redirige vers la première page d'ajout officiellle
		return redirect('/exchange/add-department/'+str(depart.University.ID))

	return render(request, 'exchange/editDepartment.html',locals())

def review(request):
    return render(request, 'exchange/addInformation.html', {})

#--------------Rapport---------------
def rapport(request):
	 return render(request, 'exchange/rapport.html', {})
