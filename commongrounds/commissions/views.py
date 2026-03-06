from django.shortcuts import render

from commissions.models import Commission


def requests_list(request):
    return render(request, "requests_list.html", {"requests": Commission.objects.all()})


def request_details(request, pk):
    return render(request, "request_details.html", {"request": Commission.objects.get(pk=pk)})
