from django.shortcuts import render


def requests_list(request):
    return render(request, "requests_list.html")

def request_details(request, request_id):
    return render(request, "request_details.html", {"request": {"id": request_id} })
