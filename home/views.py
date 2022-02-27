from unicodedata import category, name
from venv import create
from django.shortcuts import render,redirect
from django.contrib import messages 
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Customer, OrderProduct,Product,Order,ProductCategory,Expense,ExpenseType
import json
from django.http import JsonResponse
from datetime import date
from datetime import datetime
from django.forms.models import model_to_dict
from django.core.serializers import serialize
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import Q

#for bill print
from django.http import HttpResponse
from django.views.generic import View
from main.utils import render_to_pdf

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
    category=ProductCategory.objects.filter(user=request.user)
    expenseTotal=Expense.objects.filter(user=request.user).filter(date_created=date.today()).aggregate(total=Coalesce(Sum('price'), 0.0))
    expenseMonth=Expense.objects.filter(user=request.user).filter(date_created__gte=date.today().replace(day=1)).aggregate(total=Coalesce(Sum('price'), 0.0))
    param={
        'todaySale':todaySale,
        'totalSale':totalSale,
        'thisMonthSale':thisMonthSale,
        'onlineSale':onlineSale,
        'offlineSale':offlineSale,
        'dineInSale':dineInSale,
        'takeawaySale':takeawaySale,
        'paymentMethods':paymentMethods,
        'categorys':category,
        'expenseTotal':expenseTotal,
        'expenseMonth':expenseMonth
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

# def handleSignup(request):
#     if request.method=='POST':
#         email=request.POST['email']
#         username=request.POST['username']
#         password=request.POST['password']
#         password2=request.POST['password2']
#         if User.objects.filter(email=email).exists():
#             messages.error(request,'email id already taken')
#         elif User.objects.filter(username=username).exists():
#             messages.error(request,'username taken kindly login or enter another username')
            
#         elif password!=password2:
#             messages.error(request,'enter same password in both fields')

#         else:
#             user = User.objects.create_user(username=username,email=email,password=password)
#             user.save()
#             login(request,user)
#             return redirect('home')
#     return render(request,'signup.html')

@login_required
def GeneratePdf(request,id):
    try:
        order=Order.objects.get(id=id,user=request.user)
        # if order.cancel():
        #     print('yes1')
        #     return HttpResponse("Not found")
    except Exception as e:
        order=None
        # print('yes')
        return HttpResponse("Not found")
    # template = get_template('invoice.html')
    context = {'order':order}
    # html = template.render(context)
    pdf = render_to_pdf('invoice/invoice.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" %(order.id)
        content = "inline; filename='%s'" %(filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    # print('yes3')
    return HttpResponse("Not found")

@login_required
def order(request):
    if request.method=='POST':
        customerId=request.POST['customerId']
        customerName=request.POST['customerName']
        phone=request.POST['phone']
        saleOptions=request.POST['saleOptions']
        # print(saleOptions)
        paymentOptions=request.POST['paymentOptions']
        email=request.POST.get('email','')
        # print(paymentOptions)
        order_state=request.POST.get('order_state','Dine in')
        onlineOption=request.POST.get('onlineOption','Zomato')
        split=request.POST.get('split','')
        # print(saleOptions,order_state,paymentOptions)
        
        if customerId!="":
            customer=Customer.objects.filter(user=request.user).filter(id=customerId).update(phone=phone,name=customerName,email=email)
            customer=Customer.objects.filter(user=request.user).filter(id=customerId).first()
        else:
            customer=Customer.objects.create(name=customerName,phone=phone,email=email,user=request.user)
            customer.save()
        print(split)
        if split!='':
            amount1=request.POST['amount1']
            amount2=request.POST['amount2']
            paymentOptions2=request.POST['paymentOptions2']
            print(amount1,amount2,paymentOptions2)
            if saleOptions=='Online Sale':
                order=Order.objects.create(customer=customer,saleType=saleOptions,onlineSaleOption=onlineOption,orderState=order_state,payment_method=paymentOptions,user=request.user,payment1=amount1,payment2=amount2,is_split=True,payment_method2=paymentOptions2)
            else:
                order=Order.objects.create(customer=customer,saleType=saleOptions,orderState=order_state,payment_method=paymentOptions,user=request.user,payment1=amount1,payment2=amount2,is_split=True,payment_method2=paymentOptions2)
            order.save()
        else: 
            if saleOptions=='Online Sale':
                order=Order.objects.create(customer=customer,saleType=saleOptions,onlineSaleOption=onlineOption,orderState=order_state,payment_method=paymentOptions,user=request.user)
            else:
                order=Order.objects.create(customer=customer,saleType=saleOptions,orderState=order_state,payment_method=paymentOptions,user=request.user)
            order.save()

        items=request.POST['items']
        items=json.loads(items)
        for item in items.keys():
            product=Product.objects.get(id=int(item))
            orderProduct=OrderProduct.objects.create(order=order,product=product,quantity=items[item])
            orderProduct.save()
        messages.success(request,f"Order Placed (order id- {order.id}) <a href='order-history/OrderId-{order.id}' class='btn btn-link ml-2' style='text-decoration: none;'>view detals</a> <a href='order/invoice/{order.id}' target='_blank'  class='btn btn-primary mr-auto'>print</a>")
        # return GeneratePdf(request,order.id)
        # messages.success(request,f"Order Placed (order id- {order.id}) <a href='order-history/OrderId-{order.id}' class='btn btn-link' style='text-decoration: none;'>view detals</a>")
            # print(int(item),items[item])
    products=Product.objects.filter(user=request.user)
    customers=Customer.objects.filter(user=request.user)
    param={'products':products,'customers':customers}
    return render(request,'order.html',param)

@login_required
def cancelOrder(request,id):
    try:
        order=Order.objects.get(id=id,user=request.user)
        if order.cancel():
            order.delete()
            messages.success(request,f"Order Canceled sucessfully" )
            return redirect('order-history')
        else:
            return HttpResponse("Not found")
    except Exception as e:
        return HttpResponse("Not found")

@login_required
def addProduct(request):
    if request.method=='POST':
        productName=request.POST['productName']
        price=request.POST['price']
        qty=request.POST['qty']
        unit=request.POST['unit']
        category=request.POST['category']
        description=request.POST['description']
        obj, created=ProductCategory.objects.get_or_create(user=request.user,category=category)
        product=Product.objects.create(name=productName,price=price,description=description,unit=unit,qty=qty,user=request.user,category=obj)
        product.save()
        messages.success(request,f"Product ({productName}) created sucessfully!")
    # products=Product.objects.filter(user=request.user)
    categories=ProductCategory.objects.filter(user=request.user)
    param={'categories':categories}
    return render(request,'addProduct.html',param)
@login_required
def product(request):
    products=Product.objects.filter(user=request.user)
    categories=ProductCategory.objects.filter(user=request.user)
    param={'products':products,'categories':categories}
    return render(request,'productList.html',param)

@login_required
def editProduct(request,id):
    try:
        product=Product.objects.get(id=id,user=request.user)
        categories=ProductCategory.objects.filter(user=request.user)
        if request.method=='POST':
            productName=request.POST['productName']
            price=request.POST['price']
            qty=request.POST['qty']
            unit=request.POST['unit']
            category=request.POST['category']
            description=request.POST['description']
            obj, created=ProductCategory.objects.get_or_create(user=request.user,category=category)
            print(product.price,price)
            print(type(product.price),type(price))
            if product.price==float(price):
                print('update')
                product.name=productName
                product.description=description
                product.unit=unit
                product.qty=qty
                product.category=obj
                product.save()
                messages.success(request,"Product edited sucessfully!")
            else:
                product.is_active=False
                product.save()
                product=Product.objects.create(name=productName,price=price,description=description,unit=unit,qty=qty,user=request.user,category=obj)
                product.save()
                messages.success(request,"Product edited sucessfully!")
        param={'categories':categories,'product':product}
        return render(request,'editProduct.html',param)
    except Exception as e:
        return redirect('product')

@login_required
def deleteProduct(request,id):
    try:
        product=Product.objects.get(id=id,user=request.user)
        product.is_active=False
        product.save()
        messages.success(request,f" product {product.name} has been deleted sucessfully")
        return redirect('product')
    except Exception as e:
        return redirect('product')

@login_required
def orderHistory(request,id=None):
    if id is None:
        orders=Order.objects.filter(user=request.user).order_by('-date_created')
        if len(orders)==0:
            messages.error(request,f"No Order History")
        param={'orders':orders}
        return render(request,'order-history.html',param)
    else:
        print(id)
        inputType=id.split('-')[0]
        if inputType=='phone':
            orders=Order.objects.filter(user=request.user).filter(customer__phone=id.split('-')[1])
            phone=id.split('-')[1]
            if len(orders)==0:
                messages.error(request,f"No Order with Customer number- {phone}")
        elif inputType=='date':
            date=id.split('-')[1:]
            date='-'.join(date)
            orders=Order.objects.filter(user=request.user).filter(date_created__date=date)
            if len(orders)==0:
                messages.error(request,f"No Order with date - {date}")
        elif inputType=='OrderId':
            orders=Order.objects.filter(user=request.user).filter(id=int(id.split('-')[1]))
            if not orders:
                messages.error(request,f"No Order with order Id- {int(id.split('-')[1])}")
        param={'orders':orders}
        return render(request,'order-history.html',param)

@login_required  
def getCategoryProductSale(request):
    if request.method=="POST":
        data = json.loads(request.body)
        start=data['start']
        end=data['end']
        category=data['category']
        data=ProductCategory.objects.productSaleByCategory(request.user,start,end,category)
        data={'labels':list(data.keys()),'data':list(data.values())}
        return JsonResponse(data)

@login_required  
def getCategorySale(request):
    if request.method=="POST":
        dates = json.loads(request.body)
        start=dates['start']
        end=dates['end']
        data=ProductCategory.objects.categorySaleData(request.user,start,end)
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
def getOrderSaleByMonth(request):
    if request.method=="POST":
        dates = json.loads(request.body)
        start=dates['start']
        start+='-01'
        start=datetime.strptime(start, '%Y-%m-%d').date()#convert string to date
        end=dates['end']
        end+='-27'
        end=datetime.strptime(end, '%Y-%m-%d').date()
        data=Order.objects.getOrderPerMonth(start,end,request.user)
        return data

# @login_required
# def customerExist(request):
#     if request.method=='POST':
#         data = json.loads(request.body)
#         number=data['number']
#         if Customer.objects.filter(user=request.user).filter(phone=number).exists():
#             responseData=Customer.objects.filter(user=request.user).filter(phone=number).first()
#             print('t')
#             return JsonResponse(model_to_dict(responseData))
#         return JsonResponse({})

@login_required
def addExpense(request):
    if request.method=='POST':
        itemName=request.POST['itemName']
        price=request.POST['price']
        description=request.POST['description']
        type=request.POST['type']
        date=request.POST['date']
        try:
            expenseType=ExpenseType.objects.get(id=type,user=request.user)
        except Exception as e:
            expenseType=ExpenseType.objects.create(user=request.user,name=type)
            expenseType.save()
        newExpense=Expense.objects.create(user=request.user,name=itemName,price=price,description=description,type=expenseType,date_created=date)
        newExpense.save()
        messages.success(request,"Item added sucessfully!")
    return redirect('expense')

@login_required
def expense(request):
    if request.method=='POST':
        start=request.POST['start']
        end=request.POST['end']
        # start=datetime.strptime(start, '%Y-%m-%d').date()
        # end=datetime.strptime(end, '%Y-%m-%d').date()
        q=Q(date_created__gte=start) & Q(date_created__lte=end)
    else:
        q=Q(date_created__gte=date.today()) & Q(date_created__lte=date.today())   
    expenseType=ExpenseType.objects.filter(user=request.user)
    items=Expense.objects.filter(user=request.user).filter(q)
    param={'expenseTypes':expenseType,'items':items}
    return render(request,'expense.html',param)

@login_required
def handleLogout(request):
    logout(request)
    return redirect('handleLogin')
