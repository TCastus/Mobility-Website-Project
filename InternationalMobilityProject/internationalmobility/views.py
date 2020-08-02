from django.shortcuts import render,redirect
from django.http import HttpResponse

def root(request):
    return redirect('/exchange/home')