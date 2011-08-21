# Create your views here.

from django.shortcuts import render_to_response

def index(request):
  return render_to_response('projects/templates/index.html', {'projects_active': 'active'})


def wsgid(request):
  return render_to_response('projects/templates/wsgid.html', {'projects_active': 'active'})
