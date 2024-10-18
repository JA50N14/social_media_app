from django.shortcuts import render

# Create your views here.


def feed(request):
    if request.method == 'GET':
        return render(request, 'feed.html')
    