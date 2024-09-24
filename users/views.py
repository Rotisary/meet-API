from django.shortcuts import render

def docs_view(request):
    return render(request, 'users/docs.html')