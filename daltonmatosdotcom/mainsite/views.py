# Create your views here.


from django.shortcuts import render_to_response

def index(request):
  return render_to_response('mainsite/templates/index.html', {'home_active': 'active'})
