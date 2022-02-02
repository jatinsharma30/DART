from unicodedata import category
from django.db import models
from datetime import date,timedelta
from django.http import JsonResponse, request
import datetime
from django.db.models import Q
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.name

class ProductCategoryManager(models.Manager):
    def categorySaleData(self,user,start,end):
        data={}
        q=Q(order__date_created__date__gte=start) & Q(order__date_created__date__lte=end)
        for orderProduct in OrderProduct.objects.filter(q).filter(product__user=user): 
            key=orderProduct.product.category.category
            if key in data:
                data[key]+=orderProduct.TotalCostProduct()
            else:
                data[key]=orderProduct.TotalCostProduct()
        print(data)
        return data

    def productSaleByCategory(self,user,start,end,category):
        data={}
        for product in Product.objects.filter(category=category):
            data[product.name]=0
        q=Q(order__date_created__date__gte=start) & Q(order__date_created__date__lte=end)
        for orderProduct in OrderProduct.objects.filter(q).filter(product__user=user).filter(product__category=category): 
            key=orderProduct.product.name
            data[key]+=orderProduct.TotalCostProduct()
        print(data)
        return data

class ProductCategory(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.CharField(max_length=100)
    objects=ProductCategoryManager()
    def __str__(self):
        return self.category  

class Product(models.Model):
    name = models.CharField(max_length=200, null=True,unique=True)
    price = models.FloatField(null=True)
    description = models.CharField(max_length=200, null=True,blank=True)
    unit = models.CharField(max_length=50,null=True,blank=True)
    qty=models.DecimalField( max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='product')
    category=models.ForeignKey(ProductCategory,null=True,blank=True,on_delete=models.CASCADE)

    def __str__(self):
        if self.category:
            return f"{self.name} ({self.category.category})"
        else:
            return self.name

    def productSales(self,start=None,end=None,user=None):
        sum=0
        orders=Order.objects.getOrderByDate(start,end,user)
        for order in orders:
            products=order.orderProducts.all() 
            for product in products:
                if product.product.id==self.id: 
                    sum+=product.TotalCostProduct()
        return sum
    
class OrderManager(models.Manager):
    def getOrderByDate(self,start,end,user):
        if (start and end):
            q=Q(date_created__date__gte=start) & Q(date_created__date__lte=end)
            qs=self.get_queryset().filter(user=user).filter(q)
        else:
            qs=self.get_queryset().filter(user=user).all()
        return qs
    def getOrderAmountByDate(self,start=None,end=None,user=None):
        qs=self.getOrderByDate(start,end,user)
        total=0
        for order in qs:
            total+=order.total()
        return total
    def getOrderPerDate(self,start=None,end=None,user=None):
        data={}
        if (start==None and end==None):
            firstOrder=self.get_queryset().filter(user=user).order_by('date_created').first()
            start=firstOrder.date_created.date()
            end=date.today()
        while start<=end:
            data[str(start)]=self.getOrderAmountByDate(start,start,user) 
            start+= timedelta(days=1)
        data={'labels':list(data.keys()),'data':list(data.values())}
        return JsonResponse(data)

    def months_between(self,date_start, date_end):
        months = []
        # Make sure start_date is smaller than end_date
        if date_start > date_end:
            tmp = date_start
            date_start = date_end
            date_end = tmp

        tmp_date = date_start
        while tmp_date.month <= date_end.month or tmp_date.year < date_end.year:
            months.append(tmp_date)  # Here you could do for example: months.append(datetime.datetime.strftime(tmp_date, "%b '%y"))

            if tmp_date.month == 12: # New year
                tmp_date = datetime.date(tmp_date.year + 1, 1, 1)
            else:
                tmp_date = datetime.date(tmp_date.year, tmp_date.month + 1, 1)
        return months

    def getOrderPerMonth(self,start=None,end=None,user=None):
        months=self.months_between(start,end)
        print(months)
        data={}
        for month in months:
            data[f"{month.strftime('%B')} {month.year}"]=0
            q=Q(order__date_created__year=month.year) & Q(order__date_created__month=month.month)
            print(OrderProduct.objects.filter(q).filter(product__user=user),month.month,start.year)
            for orderProduct in OrderProduct.objects.filter(q).filter(product__user=user):
                data[f"{month.strftime('%B')} {month.year}"]+=orderProduct.TotalCostProduct()
        data={'labels':list(data.keys()),'data':list(data.values())}
        return JsonResponse(data)
    
    def getTotalSaleByQuery(self,qs):
        total=0
        for q in qs:
            total+=q.total()
        return total

    def getOnlineSale(self,user):
        qs=self.get_queryset().filter(user=user).filter(saleType='Online Sale')
        count=qs.count()
        total=self.getTotalSaleByQuery(qs)
        res={"count":count,'total':total}
        return res
    def getOfflineSale(self,user):
        qs=self.get_queryset().filter(user=user).filter(saleType='Offline Sale')
        count=qs.count()
        total=self.getTotalSaleByQuery(qs)
        res={"count":count,'total':total}
        return res
    def getDineInSale(self,user):
        qs=self.get_queryset().filter(user=user).filter(orderState='Dine in')
        count=qs.count()
        total=self.getTotalSaleByQuery(qs)
        res={"count":count,'total':total}
        return res
    def getTakeawaySale(self,user):
        qs=self.get_queryset().filter(user=user).filter(orderState='Takeaway')
        count=qs.count()
        total=self.getTotalSaleByQuery(qs)
        res={"count":count,'total':total}
        return res
    def getPaymentMethodsSale(self,user):
        count=self.get_queryset().filter(user=user).count()
        qsCash=self.get_queryset().filter(user=user).filter(payment_method='Cash')
        try:
            cashCount=(qsCash.count()/count)*100
        except ZeroDivisionError:
            cashCount=0
        qsAmazonPay=self.get_queryset().filter(user=user).filter(payment_method='Amazon Pay')
        try:
            amazonCount=(qsAmazonPay.count()/count)*100
        except ZeroDivisionError:
            amazonCount=0
        qsGooglePay=self.get_queryset().filter(user=user).filter(payment_method='Google Pay')
        try:
            googleCount=(qsGooglePay.count()/count)*100
        except ZeroDivisionError:
            googleCount=0
        qsPaytm=self.get_queryset().filter(user=user).filter(payment_method='Paytm')
        try:
            paytmCount=(qsPaytm.count()/count)*100
        except ZeroDivisionError:
            paytmCount=0
        qsCard=self.get_queryset().filter(user=user).filter(payment_method='Card')
        try:
            cardCount=(qsCard.count()/count)*100
        except ZeroDivisionError:
            cardCount=0
        res={
            'cashCount':cashCount,
            'cashTotal':self.getTotalSaleByQuery(qsCash),
            'amazonCount':amazonCount,
            'amazonTotal':self.getTotalSaleByQuery(qsAmazonPay),
            'googleCount':googleCount,
            'googleTotal':self.getTotalSaleByQuery(qsGooglePay),
            'cardCount':cardCount,
            'cardTotal':self.getTotalSaleByQuery(qsCard),
            'paytmCount':paytmCount,
            'paytmTotal':self.getTotalSaleByQuery(qsPaytm)
        }
        return res
              
class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='order')
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    saleChoices=(
        ('Online Sale','Online Sale'),
        ('Offline Sale','Offline Sale')
    )
    saleType=models.CharField(choices=saleChoices,default='Offline Sale',max_length=15)
    orderStateChoices=(
        ('Dine in','Dine in'),
        ('Takeaway','Takeaway')
    )
    orderState=models.CharField(choices=orderStateChoices,default='Dine in',max_length=15)
    paymentChoices=(
        ('Cash','Cash'),
        ('Amazon Pay','Amazon Pay'),
        ('Google Pay','Google Pay'),
        ('Paytm','Paytm'),
        ('Card','Card')
    )
    payment_method=models.CharField(choices=paymentChoices,default='Cash',max_length=15)

    objects=OrderManager()

    def __str__(self):
        return f"{self.id}"

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