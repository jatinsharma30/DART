from django.shortcuts import render,redirect
from django.contrib import messages 
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Customer, OrderProduct,Product,Order
import json
from django.http import JsonResponse
from datetime import date
from datetime import datetime

# Create your views here.
@login_required
def home(request):
    todaySale=Order.objects.getOrderAmountByDate(date.today(),date.today())
    totalSale=Order.objects.getOrderAmountByDate()
    thisMonthSale=Order.objects.getOrderAmountByDate(date.today().replace(day=1),date.today())
    product=Product.objects.get(id=1).productSales()
    getOrderPerDate=Order.objects.getOrderPerDate(date(2022,1,15),date.today())
    print(getOrderPerDate)
    print(product)
    param={'todaySale':todaySale,'totalSale':totalSale,'thisMonthSale':thisMonthSale}
    return render(request,'home.html',param)

def handleLogin(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        print(email,password)
        try:
            user=User.objects.get(email=email)
            if user.check_password(password):
                login(request,user)
                return redirect('home')
            else:
                messages.error(request,'Wrong email or password')
        except User.DoesNotExist:
            messages.error(request,'Wrong email or password')
    return render(request,'login.html')

def handleSignup(request):
    if request.method=='POST':
        email=request.POST['email']
        username=request.POST['username']
        password=request.POST['password']
        password2=request.POST['password2']
        if User.objects.filter(email=email).exists():
            messages.error(request,'email id already taken')
        elif User.objects.filter(username=username).exists():
            messages.error(request,'username taken kindly login or enter another username')
            
        elif password!=password2:
            messages.error(request,'enter same password in both fields')

        else:
            user = User.objects.create_user(username=username,email=email,password=password)
            user.save()
            login(request,user)
            return redirect('home')
    return render(request,'signup.html')

@login_required
def order(request):
    if request.method=='POST':
        customerName=request.POST['customerName']
        phone=request.POST['phone']
        email=request.POST.get('email','')
        customer=Customer.objects.create(name=customerName,phone=phone,email=email)
        customer.save()
        order=Order.objects.create(customer=customer)
        order.save()

        items=request.POST['items']
        items=json.loads(items)
        for item in items.keys():
            product=Product.objects.get(id=int(item))
            orderProduct=OrderProduct.objects.create(order=order,product=product,quantity=items[item])
            orderProduct.save()
            print(int(item),items[item])
    products=Product.objects.all()
    param={'products':products}
    return render(request,'order.html',param)

@login_required
def product(request):
    if request.method=='POST':
        productName=request.POST['productName']
        price=request.POST['price']
        qty=request.POST['qty']
        unit=request.POST['unit']
        description=request.POST['description']
        product=Product.objects.create(name=productName,price=price,description=description,unit=unit,qty=qty)
        product.save()
    products=Product.objects.all()
    param={'products':products}
    return render(request,'product.html',param)

@login_required
def orderHistory(request):
    orders=Order.objects.all()
    param={'orders':orders}
    return render(request,'order-history.html',param)

@login_required  
def getProductsSale(request):
    if request.method=="POST":
        dates = json.loads(request.body)
        data={}
        start=dates['start']
        end=dates['end']
        products=Product.objects.all()
        for product in products:
            data[product.name]=product.productSales(start,end)
        print(data)
        data={'labels':list(data.keys()),'data':list(data.values())}
        return JsonResponse(data)

@login_required
def getOrderSale(request):
    if request.method=="POST":
        dates = json.loads(request.body)
        start=dates['start']
        start=datetime.strptime(start, '%Y-%m-%d').date()#convert string to date
        end=dates['end']
        end=datetime.strptime(end, '%Y-%m-%d').date()
        data=Order.objects.getOrderPerDate(start,end)
        return data

