from django.shortcuts import render, HttpResponseRedirect

def docs_view(request):
    return HttpResponseRedirect(
        "https://documenter.getpostman.com/view/33652201/2sB2xFgTgT#meet-api-documentation"
    )  # Redirect to the Postman documentation URL