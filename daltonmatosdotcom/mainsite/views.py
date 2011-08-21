# Create your views here.


from django.shortcuts import render_to_response

def index(request):
  return render_to_response('mainsite/templates/index.html', {'home_active': 'active'})

def about(request):
  return render_to_response('mainsite/templates/about.html', {'about_active': 'active'})

def blog(request):
  return render_to_response('mainsite/templates/blog.html', {'blog_active': 'active'})

def contact(request):
  return render_to_response('mainsite/templates/contact.html', {'contact_active': 'active'})
