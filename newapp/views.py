from django.shortcuts import render
from .models import collection
# Create your views here.
#its a request handler
from django.http import HttpResponse

#def say_hello(request):
 #   #return HttpResponse("hello world")
  
  #  return render(request,'styling.html',{'name':'Rabid'})
def index (request):
  
  collections= list(collection.find({}, {
    
    "_id": 0,
    "Employee Name": 1,
    "Status": 1,
    "Availed Leaves Annual Leaves": 1,
    "Availed Leaves Casual Leaves": 1,
    "Availed Leaves Sick Leaves": 1,
    "Availed Leaves WFH": 1,
    "Availed Leaves Extra": 1,
    "Allocated Leaves Annual": 1,
    "Allocated Leaves Casual": 1,
    "Allocated Leaves Sick": 1,
    "Allocated Leaves Extra": 1,
    "Allocated Leaves WFH": 1,
    "RemainingAnnual": 1,
    "Remaining Casual": 1,
    "Remaining Sick": 1,
    "Remaining Extra": 1,
    "Remaining WFH": 1
}))
  return render(request,'styling.html',{'collections':collections})
  #return HttpResponse(collections)