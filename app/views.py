from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from .models import *
from .forms import CustomerProfileForm, CustomerRegistrationForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
import json


class ProductView(View):
    def get(self,request):
        totalitem = 0
        topwears = Product.objects.filter(category = 'TW')
        bottomwears = Product.objects.filter(category = 'BW')
        mobiles = Product.objects.filter(category = 'M')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user = request.user))
        context = {
            'topwears' : topwears,
            'bottomwears' : bottomwears,
            'mobiles' : mobiles,
            'totalitem':totalitem
        }
        return render(request,'app/home.html',context)
        


class ProductDetailView(View):
    def get(self,request,pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        review = Review.objects.filter(pk=pk)
        review_user = None
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id)& Q(user=request.user)).exists()
            totalitem = len(Cart.objects.filter(user = request.user))
            review = Review.objects.filter(product=product.id).exclude(user=request.user)
            review_user = Review.objects.filter(Q(product=product.id)& Q(user=request.user))
        return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'totalitem':totalitem,'review':review,'review_user':review_user})



@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id = product_id)
    Cart(user=user,product = product).save()
    return redirect('/cart')


@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user = user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        totalitem = len(Cart.objects.filter(user = user))
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount = p.quantity * p.product.discounted_price
                amount+= tempamount
            total_amount = amount+shipping_amount
            return render(request, 'app/addtocart.html',{'carts':cart,'totalamount':total_amount,'amount':amount,'totalitem':totalitem})
        else:
            return render(request,'app/emptycart.html')



def search(request):
    search_text = request.GET['search']
    result = Product.objects.filter(Q(title__icontains=search_text)| Q(brand__icontains = search_text))
    return render(request,'app/search.html',{'result':result,'text':search_text})



def items(request):
  if request.is_ajax():
    q = request.GET.get('term', '')
    items = Product.objects.filter(Q(title__icontains=q)| Q(brand__icontains = q))
    results = []
    for pl in items:
      place_json = {}
      place_json = pl.title
      results.append(place_json)
    data = json.dumps(results)
  else:
    data = 'fail'
  mimetype = 'application/json'
  return HttpResponse(data, mimetype)




def plus_cart(request):
    if(request.method == 'GET'):
        prod_id = request.GET['prod_id']
        c= Cart.objects.get(Q(product = prod_id)& Q(user=request.user))
        c.quantity+=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount+= tempamount
        total_amount = shipping_amount+amount

        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':total_amount
        }

        return JsonResponse(data)


def minus_cart(request):
    if(request.method == 'GET'):
        prod_id = request.GET['prod_id']
        c= Cart.objects.get(Q(product = prod_id)& Q(user=request.user))
        c.quantity-=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount+= tempamount
        total_amount = shipping_amount+amount

        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':total_amount
        }

        return JsonResponse(data)

def remove_cart(request):
    if(request.method == 'GET'):
        prod_id = request.GET['prod_id']
        c= Cart.objects.get(Q(product = prod_id)& Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount+= tempamount
        total_amount = shipping_amount+amount

        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':total_amount
        }

        return JsonResponse(data)

def buy_now(request):
 return render(request, 'app/buynow.html')

@login_required
def address(request):
    totalitem = len(Cart.objects.filter(user = request.user))
    add = Customer.objects.filter(user = request.user)
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary','totalitem':totalitem})

@login_required
def orders(request):
    totalitem = len(Cart.objects.filter(user = request.user))
    op = OrderPlaced.objects.filter(user = request.user)
    return render(request, 'app/orders.html',{'order_placed':op,'totalitem':totalitem})



def mobile(request,data=None):
    totalitem = len(Cart.objects.filter(user = request.user))
    if data == None:
        mobiles = Product.objects.filter(category = 'M')
    elif data=='below':
        mobiles = Product.objects.filter(category = 'M').filter(discounted_price__lte=10000)
    elif data=='above':
        mobiles = Product.objects.filter(category = 'M').filter(discounted_price__gte=10000)
    else:
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    return render(request, 'app/mobile.html',{'mobiles':mobiles,'totalitem':totalitem})


def topwears(request,data=None):
    totalitem = len(Cart.objects.filter(user = request.user))
    if data == None:
        topwears = Product.objects.filter(category = 'TW')
    
    elif data == 'below':
        topwears = Product.objects.filter(category = 'TW').filter(discounted_price__lte=1000)

    elif data == 'above':
        topwears = Product.objects.filter(category = 'TW').filter(discounted_price__gte = 1000)

    else:
        topwears = Product.objects.filter(category = 'TW').filter(brand = data)
    return render(request,'app/topwear.html',{'topwears':topwears,'totalitem':totalitem})


def bottomwears(request,data=None):
    totalitem = len(Cart.objects.filter(user = request.user))
    if data == None:
        bottomwears = Product.objects.filter(category = 'BW')
    
    elif data == 'below':
        bottomwears = Product.objects.filter(category = 'BW').filter(discounted_price__lte = 1000)

    elif data == 'above':
        bottomwears = Product.objects.filter(category = 'BW').filter(discounted_price__gte = 1000)
    
    else:
        bottomwears = Product.objects.filter(category = 'BW').filter(brand = data)
    
    return render(request,'app/bottomwear.html',{'bottomwears':bottomwears,'totalitem':totalitem})


def login(request):
 return render(request, 'app/login.html')


class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',{'form':form})

    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulations!! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html',{'form':form})



@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user = user)
    amount = 0.0
    shipping_amount = 70.00
    total_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount+= tempamount
    total_amount = shipping_amount+amount
    return render(request, 'app/checkout.html',{'add':add,'totalamount':total_amount,'cart_items':cart_items})


@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user = user)

    for c in cart:
        OrderPlaced(user = user,customer = customer,product = c.product,quantity=c.quantity).save()
        c.delete()
    return redirect("orders")




@method_decorator(login_required,name = 'dispatch')
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})

    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congratulations!! Profile Updated Successfully')
        form = CustomerProfileForm()
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})



def Reviews(request,pk):
    star = request.POST.get('rating')
    comment = request.POST.get('comment')
    product = Product.objects.get(id=pk)
    obj = Review(user = request.user,product=product,rating=star,comments=comment)
    obj.save()
    return HttpResponseRedirect(reverse("product-detail",args=(pk,)))



