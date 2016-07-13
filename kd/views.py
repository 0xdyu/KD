# -*- coding: utf-8 -*-  

from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.db.models import Max
from kd.models import Order, EndUser, ShippingUser, OrderStatus
from django.shortcuts import get_object_or_404
from random import randint
import datetime
from django.http import JsonResponse, HttpResponse
from django.core import serializers
import json
from django.core.urlresolvers import reverse
from django.contrib.auth.views import password_reset, password_reset_confirm


# Create your views here.

def home(request):
    return render(request, 'kd/home.html')

@csrf_protect
def login(request):
    return render(request, 'kd/login.html')

@csrf_protect
def user_profile(request):
    if request.user.is_authenticated()==False:
        return render(request, 'kd/home.html', {})
    #objects=Order.objects.filter(shipping_user_id=request.user.email)
    relatedOrderStatus=OrderStatus.objects.filter(order__shipping_user_id=request.user.email)
    curOrders = Order.objects.annotate(lastest_order_status_time=Max('orderstatus__time'))
    objects = relatedOrderStatus.filter(time__in=[o.lastest_order_status_time for o in curOrders]).order_by('-time')
    return render(request, 'kd/profile.html', {'orders' : objects})

def ajax_get_all_order(request):
    relatedOrderStatus=OrderStatus.objects.filter(order__shipping_user_id=request.user.email)
    curOrders = Order.objects.annotate(lastest_order_status_time=Max('orderstatus__time'))
    objects = relatedOrderStatus.filter(time__in=[o.lastest_order_status_time for o in curOrders]).order_by('-time')
    return HttpResponse(__generate_json(objects))

def ajax_get_inital_order(request):
    relatedOrderStatus=OrderStatus.objects.filter(order__shipping_user_id=request.user.email)
    curOrders = Order.objects.annotate(lastest_order_status_time=Max('orderstatus__time'))
    objects = relatedOrderStatus.filter(time__in=[o.lastest_order_status_time for o in curOrders]).order_by('-time')
    filteredObjects = objects.filter(status='initial')
    return HttpResponse(__generate_json(filteredObjects))

def ajax_get_shipping_order(request):
    relatedOrderStatus=OrderStatus.objects.filter(order__shipping_user_id=request.user.email)
    curOrders = Order.objects.annotate(lastest_order_status_time=Max('orderstatus__time'))
    objects = relatedOrderStatus.filter(time__in=[o.lastest_order_status_time for o in curOrders]).order_by('-time')
    filteredObjects = objects.filter(status='shipping')
    return HttpResponse(__generate_json(filteredObjects))

def ajax_get_delivered_order(request):
    relatedOrderStatus=OrderStatus.objects.filter(order__shipping_user_id=request.user.email)
    curOrders = Order.objects.annotate(lastest_order_status_time=Max('orderstatus__time'))
    objects = relatedOrderStatus.filter(time__in=[o.lastest_order_status_time for o in curOrders]).order_by('-time')
    filteredObjects = objects.filter(status='delivered')
    return HttpResponse(__generate_json(filteredObjects))

def __generate_json(filteredObjects):
    orders=[]
    for entry in filteredObjects:
        orders.append({'order_id' : entry.id, 
            'sender' : entry.order.sender.name, 
            'receiver' : entry.order.receiver.name,
            'location' : entry.location,
            'status' : entry.status,
            'update_time' : entry.time.strftime('%Y/%m/%d/') + str(entry.time.hour) + ':' + str(entry.time.minute),
            'create_time' : entry.order.create_time.strftime('%Y/%m/%d/') + str(entry.order.create_time.hour) + ':' + str(entry.order.create_time.minute)}) 
    qs_json=json.dumps(orders)
    return qs_json

@csrf_protect
def search_order(request):
    if request.method == "GET":
        order_id = request.GET['order_id']
        if OrderStatus.objects.filter(id=order_id).exists():
            objects=OrderStatus.objects.filter(id=order_id).order_by('-time')
            return render(request, 'kd/order_info.html', 
                {'order_id' : order_id, 
                'order_status' : objects.values('status')[0]['status'], 
                'curr_location' : objects.values('location')[0]['location'],
                'update_time' : objects.values('time')[0]['time']})

        else:
            return render(request, 'kd/search_order_failed.html', {'order_id' : order_id})
        
    return render(request, 'kd/home.html', {})

@csrf_protect
def order_info_insider(request):
    if request.user.is_authenticated()==False or request.user.email != Order.objects.get(id=request.GET['order_id']).shipping_user_id:
        return render(request, 'kd/search_order_failed.html', {'order_id' : request.GET['order_id']})
    if request.method == "GET":
        order_id = request.GET['order_id']
        if OrderStatus.objects.filter(id=order_id).exists():
            objects=OrderStatus.objects.filter(id=order_id).order_by('-time')
            return render(request, 'kd/order_info_insider.html', 
                {'curStatus' : objects[0],
                'objects' : objects})

        else:
            return render(request, 'kd/search_order_failed.html', {'order_id' : order_id})
        
    return render(request, 'kd/profile.html', {})

@csrf_protect
def order_update_call(request):
    if request.user.is_authenticated()==False or request.user.email != Order.objects.get(id=request.GET['order_id']).shipping_user_id:
        return render(request, 'kd/order_update_fail.html', {'order_id' : request.GET['order_id']})
    return render(request, 'kd/order_update.html', {'order_id' : request.GET['order_id']})

@csrf_protect
def order_update(request):
    if request.user.is_authenticated()==False:
        return render(request, 'kd/home.html', {})
    if request.method == "POST":
        order_id = request.POST['order_id']
        curOrder = Order.objects.filter(id=order_id)[:1].get()
        if OrderStatus.objects.filter(id=order_id).exists():
            OrderStatus.objects.create(order=curOrder,
                id=order_id,
                time=datetime.datetime.now(),
                status=request.POST['package_current_status'],
                location=request.POST['package_current_location'],
                primKey=str(order_id)+str(datetime.datetime.now())
                )
            return render(request, 'kd/order_update_success.html', {'order_id' : order_id})
        else:
            return render(request, 'kd/order_update_fail.html', {'order_id' : order_id})
    return render(request, 'kd/home.html', {})

@csrf_protect
def create(request):
    if request.user.is_authenticated()==False:
        return render(request, 'kd/home.html', {})
    return render(request, 'kd/create.html')

@csrf_protect
def create_order(request):
    if request.user.is_authenticated()==False:
        return render(request, 'kd/home.html', {})
    if request.method == "POST":
        error_items = __form_validator(request.POST)
        if len(error_items) != 0:
            return render(request, 'kd/order_create_failure.html', {'error_items' : error_items})
        id = __generate_order_id()
        sender=__check_enduser_exists(request.POST['sender_name'], 
            request.POST['sender_phone_number'], 
            request.POST['sender_company_name'], 
            request.POST['sender_address'], 
            request.POST['sender_postcode'])
        receiver=__check_enduser_exists(request.POST['receiver_name'], 
            request.POST['receiver_phone_number'], 
            request.POST['receiver_company_name'], 
            request.POST['receiver_address'], 
            request.POST['receiver_postcode'])
        curOrder = Order.objects.create(id=id,
                price=request.POST['package_price'],
                weight=request.POST['package_weight'],
                shipping_user_id=request.user.email,
                sender=sender,
                receiver=receiver,
                create_time=datetime.datetime.now()
                )
        OrderStatus.objects.create(order=curOrder,
            id=id,
            time=datetime.datetime.now(),
            status=request.POST['package_current_status'],
            location=request.POST['package_current_location'],
            primKey=str(id)+str(datetime.datetime.now())
            )
        
    return render(request, 'kd/order_create_success.html', {'order_id' : id}) 

def reset_confirm(request, uidb36=None, token=None):
    return password_reset_confirm(request, template_name='kd/password_reset_confirmation.html',
        uidb36=uidb36, token=token, post_reset_redirect=reverse('login'))

def reset(request):
    return password_reset(request, template_name='kd/password_reset_form.html',
        email_template_name='kd/password_reset_email.html',
        subject_template_name='kd/password_reset_subject.txt',
        post_reset_redirect=reverse('login'))

########## helper function ###########

# Generate 10 digit random nubmer for order id, return string
def __generate_order_id():
    start = 10 ** 9
    end = (10 ** 10) - 1
    random_id = str(randint(start, end))
    while Order.objects.filter(id=random_id).exists():
            random_id = __generate_order_id()
    return random_id;

# Generate 10 digit random nubmer for user id, return string
def __generate_user_id():
    start = 10 ** 9
    end = (10 ** 10) - 1
    random_id = str(randint(start, end))
    while EndUser.objects.filter(user_id=random_id).exists() or ShippingUser.objects.filter(user_id=random_id).exists():
            random_id = __generate_order_id()
    return random_id;

# check the existing about end user and create the end user if this is a new end user
def __check_enduser_exists(user_name, phone_number, company_name, address, postcode):
    if EndUser.objects.filter(name=user_name, phone_number=phone_number).exists():
            return EndUser.objects.get(name=user_name, phone_number=phone_number);
    user_id = __generate_user_id()
    return EndUser.objects.create(user_id=user_id,
            name=user_name,
            phone_number=phone_number,
            company_name=company_name,
            address=address,
            postcode=postcode
            );

# Check whether must filled in items are not empty
def __form_validator(form):
    must_filled_items = ['sender_name',
                         'sender_phone_number',
                         'sender_address',
                         'sender_postcode',
                         'receiver_name',
                         'receiver_phone_number',
                         'receiver_address',
                         'receiver_phone_number',]
    en_to_cn = {'sender_name' : u"寄件人姓名",
                'sender_phone_number' : u"寄件人联系方式",
                'sender_address' : u"寄件人地址",
                'sender_postcode' : u"寄件人邮编",
                'receiver_name' : u"收件人姓名",
                'receiver_phone_number' : u"收件人联系方式",
                'receiver_address' : u"收件人地址",
                'receiver_phone_number' : "收件人联系方式"}
    error_items = []
    for item in must_filled_items:
        if not form[item]:
            error_items.append(en_to_cn[item])
    return error_items