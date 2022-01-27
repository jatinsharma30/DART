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
def report(request):
    todaySale=Order.objects.getOrderAmountByDate(date.today(),date.today(),request.user)
    totalSale=Order.objects.getOrderAmountByDate(None,None,request.user)
    onlineSale=Order.objects.getOnlineSale(request.user)
    offlineSale=Order.objects.getOfflineSale(request.user)
    dineInSale=Order.objects.getDineInSale(request.user)
    takeawaySale=Order.objects.getTakeawaySale(request.user)
    thisMonthSale=Order.objects.getOrderAmountByDate(date.today().replace(day=1),date.today(),request.user)
    paymentMethods=Order.objects.getPaymentMethodsSale(request.user)
    param={
        'todaySale':todaySale,
        'totalSale':totalSale,
        'thisMonthSale':thisMonthSale,
        'onlineSale':onlineSale,
        'offlineSale':offlineSale,
        'dineInSale':dineInSale,
        'takeawaySale':takeawaySale,
        'paymentMethods':paymentMethods
        }
    return render(request,'report.html',param)

@login_required
def home(request):
    return render(request,'home.html')

def handleLogin(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        # print(email,password)
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
        saleOptions=request.POST['saleOptions']
        # print(saleOptions)
        paymentOptions=request.POST['paymentOptions']
        # print(paymentOptions)
        order_state=request.POST.get('order_state','Dine in')
        # print(saleOptions,order_state,paymentOptions)
        email=request.POST.get('email','')
        customer=Customer.objects.create(name=customerName,phone=phone,email=email)
        customer.save()
        order=Order.objects.create(customer=customer,saleType=saleOptions,orderState=order_state,payment_method=paymentOptions,user=request.user)
        order.save()

        items=request.POST['items']
        items=json.loads(items)
        for item in items.keys():
            product=Product.objects.get(id=int(item))
            orderProduct=OrderProduct.objects.create(order=order,product=product,quantity=items[item])
            orderProduct.save()
            # print(int(item),items[item])
    products=Product.objects.filter(user=request.user)
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
        product=Product.objects.create(name=productName,price=price,description=description,unit=unit,qty=qty,user=request.user)
        product.save()
    products=Product.objects.filter(user=request.user)
    param={'products':products}
    return render(request,'product.html',param)

@login_required
def orderHistory(request):
    orders=Order.objects.filter(user=request.user).order_by('-date_created')
    param={'orders':orders}
    return render(request,'order-history.html',param)

@login_required  
def getProductsSale(request):
    if request.method=="POST":
        dates = json.loads(request.body)
        data={}
        start=dates['start']
        end=dates['end']
        products=Product.objects.filter(user=request.user)
        for product in products:
            data[product.name]=product.productSales(start,end,request.user)
        # print(data)
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
        data=Order.objects.getOrderPerDate(start,end,request.user)
        return data

@login_required
def handleLogout(request):
    logout(request)
    return redirect('handleLogin')
