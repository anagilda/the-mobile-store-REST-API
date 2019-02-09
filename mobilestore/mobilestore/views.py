from django.shortcuts import render

def homepage(request):
    ''' Home page view - API guide'''
    return render(request, 'home.html')
