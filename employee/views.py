from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee

def home(request):
    employees = Employee.objects.all()
    return render(request, 'home.html', {'employees': employees})


def add(request):
    if request.method == 'POST':
        Employee.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            age=request.POST['age'],
            city=request.POST['city']
        )
        return redirect('home')
    return render(request, 'add.html')


def edit(request, id):
    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        employee.name = request.POST['name']
        employee.email = request.POST['email']
        employee.age = request.POST['age']
        employee.city = request.POST['city']
        employee.save()
        return redirect('home')

    return render(request, 'edit.html', {'employee': employee})