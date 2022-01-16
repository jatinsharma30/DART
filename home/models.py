from math import prod
from django.db import models
from datetime import date,timedelta
from django.http import JsonResponse
from django.db.models import Q

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

# class ProductManager(models.Manager):
#     sale=0
#     def productSales(self,start=None,end=None):
#         orders=Order.objects.getOrderByDate(start,end)
#         for order in orders:
#             products=order.orderProducts.all()
#             for product in products:
#                 print(product.product.name)
#                 print(self.model) 
#                 if product.product.name==self.name:
#                     print(product.TotalCostProduct())
#                 else:
#                     print('none')
                
#     pass

class Product(models.Model):
    name = models.CharField(max_length=200, null=True,unique=True)
    price = models.FloatField(null=True)
    description = models.CharField(max_length=200, null=True,blank=True)
    unit = models.CharField(max_length=50)
    qty=models.DecimalField( max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def productSales(self,start=None,end=None):
        sum=0
        orders=Order.objects.getOrderByDate(start,end)
        for order in orders:
            products=order.orderProducts.all() 
            for product in products:
                if product.product.id==self.id: 
                    sum+=product.TotalCostProduct()
        return sum
    
class OrderManager(models.Manager):
    def getOrderByDate(self,start,end):
        if (start and end):
            q=Q(date_created__date__gte=start) & Q(date_created__date__lte=end)
            qs=self.get_queryset().filter(q)
        else:
            qs=self.get_queryset().all()
        return qs
    def getOrderAmountByDate(self,start=None,end=None):
        qs=self.getOrderByDate(start,end)
        total=0
        for order in qs:
            total+=order.total()
        return total
    def getOrderPerDate(self,start=None,end=None):
        data={}
        if (start==None and end==None):
            firstOrder=self.get_queryset().order_by('date_created').first()
            start=firstOrder.date_created.date()
            end=date.today()
        while start<=end:
            data[str(start)]=self.getOrderAmountByDate(start,start) 
            start+= timedelta(days=1)
        data={'labels':list(data.keys()),'data':list(data.values())}
        return JsonResponse(data)
        
              
class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    objects=OrderManager()

    def total(self):
        totalAmount=0
        for orderProduct in self.orderProducts.all():
            totalAmount+=orderProduct.TotalCostProduct()
        return totalAmount

class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='orderProducts')
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,related_name='orderProducts')
    quantity = models.IntegerField(default=1)
    def TotalCostProduct(self):
        return self.product.price*self.quantity