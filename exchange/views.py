import datetime
from collections import defaultdict

from django.contrib.auth import logout
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.models import Permission
from django.db.models import Avg, Func
from django.shortcuts import render, redirect

from .forms import *
from .models import *


def day_month_conversion(day_of_year):
    d = datetime.datetime.strptime(str(day_of_year), "%j")
    day = d.strftime("%#d")
    month = d.strftime("%#m")
    return day + " " + months[int(month) - 1]


# TODO : optimize this mess
def visa_duration(day, week, month):
    d, w, m = "", "", ""
    if day > 1:
        d = str(day) + " jours"
    elif day == 1:
        d = str(day) + " jour"

    if week > 1:
        w = str(week) + " semaines"
    elif week == 1:
        w = str(week) + " semaine"

    if month != 0:
        m = str(month) + " mois"

    if d != "" and w != "" and m != "":
        return d + ", " + w + " et " + m
    elif d != "" and w != "":
        return d + " et " + w
    elif w != "" and m != "":
        return w + " et " + m
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
    return ((key, locs) for key, locs in tally.items() if len(locs) > 1)


class Round(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s, 2)"


def base(request):
    return render(request, "exchange/base.html")


def user(request):
    return render(request, "exchange/user.html")


# --------------------------------PAGE D'ACCUEIL-----------------------------------
# Actualisation de rankMetrique
# TODO : one function instead of 2 nearly identical
def actualiser_metrique_1():
    # moyenne des différent Rank pour chaque Department de Chaque Univ
    metrique_depa = Department.objects.values_list("University").annotate(Avg("Rank"))

    # insère la valeur dans l'université
    for elem in metrique_depa:
        instance = University.objects.get(id=elem[0])
        instance.rank_metric = elem[1]
        instance.save()


# Actualisation de lifeMetric
def actualiserMetrique2():
    # moyenne des différent Rank pour chaque Department de Chaque Univ
    metrique2_Depa = Exchange.objects.values_list("University").annotate(
        Avg("CulturalLifeGrade"), Avg("NightLifeGrade"), Avg("Security")
    )  # mettre le cout de la vie aussi

    # insère la valeur dans l'université
    for elem in metrique2_Depa:
        instance = University.objects.get(id=elem[0])
        instance.life_metric = (elem[1] + elem[2] + elem[3]) / 3
        instance.save()


def home(request):
    # requete pour donner toutes les universitées
    Univ_list = University.objects.all()

    # actualise les métriques
    actualiser_metrique_1()
    actualiserMetrique2()

    return render(request, "exchange/home.html", locals())


def index(request):
    return redirect("/home")


# -----------------------PAGE D'UNE UNIVERSITE (PAR id)-----------------
def university(request, idUni):
    # Requetes vers BD:
    univ = University.objects.get(pk=idUni)
    cont = UniversityContractStudent.objects.filter(university=univ)
    langue = (
        UniversityLanguages.objects.filter(university=univ)
        .exclude(language="Inconnu")
        .distinct()
    )
    ex = Exchange.objects.filter(university=univ)
    pl = ExchangeOffer.objects.filter(university=univ)
    S1 = ex.filter(semester=1)  # renvoie le premier élément de "ex" pour Semestre 1
    S2 = ex.filter(semester=2)  # renvoie le premier élément de "ex" pour Semestre 2

    # S1 will contain 0 or multiple Exchange objects in a QuerySet
    # Check if there is a need for a Visa anywhere
    s1_start, s1_end, s2_start, s2_end = 0, 0, 0, 0
    s1_start_date, s1_end_date, s2_start_date, s2_end_date = (
        "Pas d'information",
        "Pas d'information",
        "Pas d'information",
        "Pas d'information",
    )
    visa = []
    if S1:
        for e in S1:
            s1_start += int(
                e.start_date.strftime("%j")
            )  # <-- Gives the day of the year of that specific datetime.date object
            s1_end += int(e.end_date.strftime("%j"))
            visa.append(e.visa)

        s1_start_date = day_month_conversion(round(s1_start / len(S1)))
        s1_end_date = day_month_conversion(round(s1_end / len(S1)))

    if S2:
        for e in S2:
            s2_start += int(e.start_date.strftime("%j"))
            s2_end += int(e.end_date.strftime("%j"))
            visa.append(e.visa)

        s2_start_date = day_month_conversion(round(s2_start / len(S2)))
        s2_end_date = day_month_conversion(round(s2_end / len(S2)))

    # Round the average value
    # Find a way to turn a value between 1 and 366 to a dd-MM format
    visa_days, visa_weeks, visa_months = 0, 0, 0
    day_count, week_count, month_count = 0, 0, 0
    visa_text = ""

    if True in visa:
        for e in ex:
            if e.visa_days != -1:
                day_count += 1
                visa_days += e.visa_days
            if e.visa_weeks != -1:
                week_count += 1
                visa_weeks += e.visa_weeks
            if e.visa_months != -1:
                month_count += 1
                visa_months += e.visa_months

        visa_days = round(visa_days / day_count)
        visa_weeks = round(visa_weeks / week_count)
        visa_months = round(visa_months / month_count)

        visa_text = visa_duration(visa_days, visa_weeks, visa_months)
    else:
        visa_text = "Visa non nécessaire"

    # Pour avoir toutes les FinancialAid d'une échange "ex"
    fin = FinancialAid.objects.none()
    for e in ex:
        fin = fin | FinancialAid.objects.filter(Exchange=e).exclude(Value=-1)

    fin_list = []
    fin_filtered = fin.values("name", "received_every").annotate(avg_value=Avg("value"))

    # temp NE DOIS JAMAIS ETRE SAUVEGARDE!!!!!!!!!!!!
    for f in fin_filtered:
        temp = FinancialAid(
            name=f["name"],
            value=f["avg_value"],
            received_every=f["received_every"],
            exchange=Exchange.objects.first(),
        )
        fin_list.append(temp)

    # la moyenne des différentes notes pour touts les object Exchange d'un Université
    avg = Exchange.objects.filter(university=univ).aggregate(
        r=Round(Avg("rent")),
        m=Round(Avg("monthly_expenses")),
        n=Avg("night_life_grade"),
        c=Avg("cultural_life_grade"),
        s=Avg("security_grade"),
    )  # mettre le cout de la vie aussi

    return render(request, "exchange/university.html", locals())


# -----------------------PAGE RECHERCHE AVANCEE-----------------
def search(request):
    # Initialisation d'un objets Université pour requête
    qs = University.objects.none()

    # Initialisation des forms
    form = RAcontinentForm(request.POST or None)
    formContract = ContractForm(request.POST or None)
    ordre = OrdreForm(request.POST or None)

    # liste de tout les objects Pays
    ttl = Country.objects.all().order_by("name")

    # Verifie que le submit est cohérent
    if form.is_valid() and formContract.is_valid() and ordre.is_valid():
        # prend toutes les valuers
        continent = form.cleaned_data["continent"]
        name = request.POST.get("name")
        ContractType = formContract.cleaned_data["contract_type"]
        ordres = ordre.cleaned_data["Ordre"]

        # En fonction des options choisies on fait une requete différente
        universitiesC = UniversityContractAdmin.objects.filter(
            university__city__country__continent=continent
        )
        # UniversityContractsStudent
        # Si On filtre par pays
        if name != "":
            universitiesC = universitiesC.filter(
                university__city__country__country_name=name
            )

        # Si on filtre par contract
        if ContractType != "":
            universitiesC = universitiesC.filter(contract_type=ContractType)

        # Ordre : soit par pays soit par autre
        if ordres == "name":
            universitiesC = universitiesC.order_by(
                "university__city__country__name", "university__city__name"
            )
        else:
            universitiesC = universitiesC.order_by(
                "-university__" + ordres,
                "university__city__country__name",
                "university__city__name",
            )

        # dit qu'on peut afficher la liste des Universités
        valide = True

    return render(request, "exchange/search.html", locals())


# ---------RAJOUTER INFO--------------------------------
# selection continent
def reviewExchange(request):
    return render(request, "exchange/reviewExchange.html", locals())


# selection pays
def countries(request, continent):
    # donne lsite des objects pays selon le continent du paramètre de l'URL
    pays_var = Country.objects.filter(continent=continent)
    return render(request, "exchange/countries.html", locals())


# selection ville
def cities(request, country):
    # donne l'object pays grace à l'URL
    p = Country.objects.get(pk=country)

    # donne les villes pour ce pays là
    ville = City.objects.filter(country=p)

    return render(request, "exchange/cities.html", locals())


# selection univ
def universities(request, city):
    # Obtien l'objet City grave à l'URL
    v = City.objects.get(pk=city)

    # donne toutes les universités de cette ville là
    Uni = University.objects.filter(city=v)

    return render(request, "exchange/universities.html", locals())


# rajouter info étape 1:Student
def edit(request, univ):
    # prend l'object Université par l'URL
    Uni = University.objects.get(pk=univ)
    univid = Uni.id

    # Initialise, verifie et prend les info du formulaire pour Student
    form = StudentForm(request.POST or None)
    if form.is_valid():
        # enregistre les info données par le Fomrulaire dans DB
        student = form.save()

        # on passera l'id de l'étudiant dans l'URL
        studentid = student.id

        # redirige vers prochaine page
        return redirect(
            "/edit-department-student/" + str(univid) + "/" + str(studentid)
        )

    return render(request, "exchange/edit.html", locals())


# rajouter info étape 2:Department et UnivLanguage
def editDepartmentStudent(request, univ, stud):
    # Recupère Université et Student du l'URL
    Uni = University.objects.get(pk=univ)
    Stud = Student.objects.get(pk=stud)
    studentid = Stud.id
    univid = Uni.id

    # Forms pour Department et UniversityLanguage
    form2 = LangueForm(request.POST or None)

    # Form pour les département de l'université en question
    qs = Department.objects.filter(university=Uni)
    formDep = DepForm(qs)

    if form2.is_valid():
        # Prend le resultat du form Departement
        idDep = request.POST.get("NameDep")
        note = request.POST.get("Note")
        if idDep != "":
            Dep = Department.objects.get(pk=idDep)
            Dep.rank = note
            Dep.save()  # enregistre dans la base de donné

        # enregistre langue dans DB
        lang = form2.save(commit=False)
        lang.university = Uni
        lang.save()

        # redirige vers next form
        return redirect("/edit-exchange/" + str(univid) + "/" + str(studentid))

    return render(request, "exchange/editDepartmentStudent.html", locals())


# rajouter info étape 3:Exchange
def editExchange(request, univ, stud):
    # recupère info de URL
    Uni = University.objects.get(pk=univ)
    Stud = Student.objects.get(pk=stud)
    univid = Uni.id

    # Formulaire pour Exchange
    form = ExchForm(request.POST or None)
    formVisa = ExchFormVisa(
        request.POST or None
    )  # poue la case à cohcer c'est un cas à part

    if form.is_valid() and formVisa.is_valid():
        Visa = formVisa.cleaned_data["visa"]  # case à cocher

        # enregitrer dans la base de donné
        exch = form.save(commit=False)
        exch.university = Uni
        exch.student = Stud
        exch.visa = Visa
        exch.save()

        # pour passage de paramètre dans URL
        exchid = exch.id

        # redirige vers next form
        return redirect("/edit-financial/" + str(univid) + "/" + str(exchid))

    return render(request, "exchange/editExchange.html", locals())


# rajouter info étape 4: Aides Finances
def editFinancial(request, univ, exch):
    # recupère données de URL
    Uni = University.objects.get(pk=univ)
    Exch = Exchange.objects.get(pk=exch)
    Exchid = Exch.id

    # form pour les Aides Finacières
    form = FinancialForm(request.POST or None)
    if form.is_valid():
        Name = form.cleaned_data["name"]
        Value = form.cleaned_data["amount"]
        ReceivedEvery = form.cleaned_data["received_every"]

        # enregistre dans base de donnée
        fin = form.save(commit=False)
        fin.exchange = Exch
        fin.save()

        # aller vers page d'accueil
        return redirect("/home")

    return render(request, "exchange/editFinancial.html", locals())


# ----------------AUTHENTIFICATION---------
# Connexion
@login_required(login_url="/accounts/login/")  # redirige vers CAS
def exchangeLogin(request):
    print(request.session["attributes"])  # affiche attributs de l'utilisateur
    user = request.user  # prend le user

    # rajoute permission pour noter info officielles
    permission = Permission.objects.get(codename="noter_depart")
    user.user_permissions.add(permission)
    # ici faire user.atribuChePa == blabla

    # reviesn à la page d'accueil
    return redirect("/home")


# Renvoie faux si utilisateur est connecté
def check(user):
    return not (user.is_authenticated)


# DECONEXION ou sinon CAS_IGNORE_REFERER à true
@user_passes_test(check, login_url="/accounts/logout/")  # redirige vers deconnexion CAS
def exchangeLogout(request):
    logout(request)
    # HttpResponse(reverse('cas_ng_logout'))
    # reverse(connexion)
    # redirige vers accueil
    return redirect("/home")


# ----------------------PROF : MODIFIE--------------------
# pour la page d'ajout de département
@permission_required("exchange.noter_depart")
def addDepartment(request, univ):
    # Initialisation des forms
    form = DepartForm(request.POST or None)
    formUni = UnivForm(request.POST or None)
    formUniPlaces = UnivPlacesForm(request.POST or None)

    # Reuperation de l'Universite ensuite des département de l'Université
    Uni = University.objects.get(pk=univ)
    departs = Department.objects.filter(University=Uni)
    pl = ExchangeOffer.objects.filter(University=Uni)

    # recupère les données du Form de Départment
    if form.is_valid():
        Name = form.cleaned_data["name"]
        Rank = form.cleaned_data["rank"]

        # Creer un nouveau département dans BD
        depart = Department(Name=Name, University=Uni, Rank=Rank)
        depart.save()

    # recupere les donnes du form Université
    if formUni.is_valid():
        Places = formUniPlaces.cleaned_data["available_places"]
        Demand = formUni.cleaned_data["demand"]

        # modifie les valeurs de l'université
        pl.available_places = Places
        Uni.demand = Demand
        Uni.save()
        pl.save()

    return render(request, "exchange/addDepartment.html", locals())


# pour la page de modification d'un département
@permission_required("exchange.noter_depart")
def editDepartment(request, dep):
    # recupère le départ de l'URL
    form = DepartForm(request.POST or None)
    depart = Department.objects.get(pk=dep)

    # recupère info du fom de Départment
    if form.is_valid():
        Name = form.cleaned_data["name"]
        Rank = form.cleaned_data["rank"]

        # modifie les valeurs
        depart.name = Name
        depart.rank = Rank
        depart.save()

        # redirige vers la première page d'ajout officiellle
        return redirect("/add-department/" + str(depart.university.id))

    return render(request, "exchange/editDepartment.html", locals())


def review(request):
    return render(request, "exchange/addInformation.html", {})


# --------------Rapport---------------
def rapport(request):
    return render(request, "exchange/rapport.html", {})
