# -*- coding: utf-8 -*-  

from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.db.models import Max
from kd.models import Order, EndUser, ShippingUser, OrderStatus, Quote, QuoteAssignShippingUser, QuoteBid, ExternalOrder
from django.shortcuts import get_object_or_404
from random import randint
import datetime
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core import serializers
import json
import re
from django.core.urlresolvers import reverse
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from operator import itemgetter

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
        # I am testing
    #objects=Order.objects.filter(shipping_user_id=request.user.email)
    if request.method == "GET":
        order_type=request.GET['order_type']
        time_based = request.GET['time']
        asc = request.GET['asc']
        objects = __get_orders(request, order_type)
        orders = __generate_formate_orders(objects)
        sortedOrders = __sort_orders(orders, time_based, asc)
        paginator = Paginator(sortedOrders, 25)
        page = request.GET.get('page')
        try:
            orderList = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            orderList = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            orderList = paginator.page(paginator.num_pages)
        return render(request, 'kd/profile.html', {'orders' : orderList, 'order_type': order_type})

def __get_orders(request, order_type):
    relatedOrderStatus=OrderStatus.objects.filter(order__shipping_user_id=request.user.email)
    curOrders = Order.objects.annotate(lastest_order_status_time=Max('orderstatus__time'))
    objects = relatedOrderStatus.filter(time__in=[o.lastest_order_status_time for o in curOrders]).order_by('-time')
    if order_type == 'initial':
        filteredObjects = objects.filter(status='initial')
        return filteredObjects
    if order_type == 'shipping':
        filteredObjects = objects.filter(status='shipping')
        return filteredObjects
    if order_type == 'delivered':
        filteredObjects = objects.filter(status='delivered')
        return filteredObjects
    return objects


def __generate_formate_orders(filteredObjects):
    orders=[]
    for entry in filteredObjects:
        orders.append({'order_id' : entry.id, 
            'sender' : entry.order.sender.name, 
            'receiver' : entry.order.receiver.name,
            'location' : entry.location,
            'status' : entry.status,
            'update_time' : str(entry.time),#entry.time.strftime('%Y/%m/%d/') + str(entry.time.hour) + ':' + str(entry.time.minute),
            'create_time' : str(entry.order.create_time) })#entry.order.create_time.strftime('%Y/%m/%d/') + str(entry.order.create_time.hour) + ':' + str(entry.order.create_time.minute)}) 
    return orders

def __generate_formate_orders_from_order(orderObjects):
    orders=[]
    for entry in orderObjects:
        orders.append({'order_id' : entry.id, 
            'sender' : entry.sender.name, 
            'receiver' : entry.receiver.name,
            'create_time' : str(entry.create_time) })#entry.order.create_time.strftime('%Y/%m/%d/') + str(entry.order.create_time.hour) + ':' + str(entry.order.create_time.minute)}) 
    return orders

def __sort_orders(objects, time_based, asc):
    reverse = False
    if asc == '0' :
        reverse = True
    sortedObjects = sorted(objects,key=itemgetter(time_based), reverse=reverse)
    return sortedObjects

@csrf_protect
def search_order(request):
    if request.method == "GET":
        order_id = request.GET['order_id']
        if OrderStatus.objects.filter(id=order_id).exists():
            objects=OrderStatus.objects.filter(id=order_id).order_by('-time')
            status = []
            for o in objects:
                status.append({
                    'status' : o.status,
                    'location' : o.location,
                    'time' : str(o.time)
                    })
            external_order_id=''
            external_checking_method=''
            if ExternalOrder.objects.filter(order=order_id).exists():
                external_order_objects=ExternalOrder.objects.filter(order=order_id)
                external_order_id=external_order_objects.values()[0]['external_order_id']
                external_checking_method=external_order_objects.values()[0]['external_checking_method']
            return render(request, 'kd/order_info.html', 
                {'order_id' : order_id, 
                'order_status' : objects.values('status')[0]['status'], 
                'curr_location' : objects.values('location')[0]['location'],
                'update_time' : str(objects.values('time')[0]['time']),
                'objects' : status,
                'external_order_id':external_order_id,
                'external_checking_method':external_checking_method})

        else:
            return render(request, 'kd/search_order_failed.html', {'order_id' : order_id})
        
    return render(request, 'kd/home.html', {})

@csrf_protect
def search_order_form_insider(request):
    if request.user.is_authenticated()==False:
        return render(request, 'kd/home.html', {})
    return render(request, 'kd/search_order_insider.html')

@csrf_protect
def search_order_results_insider(request):
    if request.user.is_authenticated()==False:
        return render(request, 'kd/home.html', {})
    if request.method == "POST":
        order_id = request.POST['order_id']
        order_id = order_id.strip()
        if not order_id == "":
            objects = Order.objects.filter(id=order_id)
            if objects == None or not objects.exists():
        	return render(request, 'kd/search_order_insider_failed.html', {});
            else:
                return HttpResponseRedirect('/order_info/?order_id='+order_id)

        sender = None
        sender_name=request.POST['sender_name']
        sender_phone_number=request.POST['sender_phone_number']
        if not sender_name=="" and not sender_phone_number=="":
            sender = EndUser.objects.filter(name=sender_name, phone_number=sender_phone_number)
        # else if not sender_phone_number=="":
        #     sender = EndUser.objects.filter(phone_number=sender_phone_number)
        # else if not sender_name == "":
        #     sender = EndUser.objects.filter(name=sender_name)
        receiver = None
        receiver_name=request.POST['receiver_name']
        receiver_phone_number=request.POST['receiver_phone_number']
        if not receiver_name=="" and not receiver_phone_number=="":
            receiver = EndUser.objects.filter(name=receiver_name, phone_number=receiver_phone_number)
        # else if not sender_phone_number=="":
        #     receivers = EndUser.objects.filter(phone_number=receiver_phone_number)
        # else if not receiver_name == "":
        #     receivers = EndUser.objects.filter(name=receiver_name)
        # package_current_status=request.POST['package_current_status']
        # package_current_location=request.POST['package_current_location']
        objects = None
        if not sender==None and not receiver==None:
        	objects = Order.objects.filter(sender=sender, receiver=receiver)
        elif not sender==None:
        	objects = Order.objects.filter(sender=sender)
        elif not receiver==None:
        	objects= Order.objects.filter(receiver=receiver)

        if objects == None or not objects.exists():
        	return render(request, 'kd/search_order_insider_failed.html', {});

        orders = __generate_formate_orders_from_order(objects)
        # sortedOrders = __sort_orders(orders, time_based, '0')
        paginator = Paginator(orders, 25)
        page = request.GET.get('page')
        try:
            orderList = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            orderList = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            orderList = paginator.page(paginator.num_pages)
        return render(request, 'kd/search_order_results_insider.html', {'orders' : orderList})
    return render(request, 'kd/home.html') 


@csrf_protect
def order_info_insider(request):
    if request.user.is_authenticated()==False or request.user.email != Order.objects.get(id=request.GET['order_id']).shipping_user_id:
        return render(request, 'kd/search_order_failed.html', {'order_id' : request.GET['order_id']})
    if request.method == "GET":
        order_id = request.GET['order_id']
        if OrderStatus.objects.filter(id=order_id).exists():
            objects=OrderStatus.objects.filter(id=order_id).order_by('-time')
            external_order_id=''
            external_checking_method=''
            if ExternalOrder.objects.filter(order=order_id).exists():
                external_order_objects=ExternalOrder.objects.filter(order=order_id)
                external_order_id=external_order_objects.values()[0]['external_order_id']
                external_checking_method=external_order_objects.values()[0]['external_checking_method']
            status = []
            for o in objects:
            	status.append({
            		'status' : o.status,
            		'location' : o.location,
            		'time' : str(o.time)
            		})
            return render(request, 'kd/order_info_insider.html', 
                {'curStatus' : objects[0],
                'curStatus_time': str(objects[0].time),
                'create_time' : str(objects[0].order.create_time),
                'objects' : status,
                'external_order_id':external_order_id,
                'external_checking_method':external_checking_method})

        else:
            return render(request, 'kd/search_order_failed.html', {'order_id' : order_id})
        
    return render(request, 'kd/profile.html', {})

@csrf_protect
def edit_order_info_show(request):
    if request.user.is_authenticated()==False or request.user.email != Order.objects.get(id=request.GET['order_id']).shipping_user_id:
        return render(request, 'kd/search_order_failed.html', {'order_id' : request.GET['order_id']})
    if request.method == "GET":
        order_id = request.GET['order_id']
        if OrderStatus.objects.filter(id=order_id).exists():
            objects=OrderStatus.objects.filter(id=order_id).order_by('-time')
            return render(request, 'kd/edit_order_info_show.html', 
                {'curStatus' : objects[0] })

        else:
            return render(request, 'kd/edit_order_failed.html', {'order_id' : order_id})
        
    return render(request, 'kd/profile.html', {})

@csrf_protect
def edit_order_info(request):
    if request.user.is_authenticated()==False:
        return render(request, 'kd/home.html', {})
    if request.method == "POST":
        empty_items, error_items = __form_validator(request.POST)
        if len(empty_items) != 0 or len(error_items) != 0: 
            return render(request, 'kd/order_create_failure.html', {'error_items' : error_items, 'empty_items' : empty_items})
        order_id = request.POST['order_id']
        sender=__update_enduser(request.POST['sender_name'], 
            request.POST['sender_phone_number'], 
            request.POST['sender_company_name'], 
            request.POST['sender_address'], 
            request.POST['sender_postcode'])
        receiver=__update_enduser(request.POST['receiver_name'], 
            request.POST['receiver_phone_number'], 
            request.POST['receiver_company_name'], 
            request.POST['receiver_address'], 
            request.POST['receiver_postcode'])
        price = 0
        if not request.POST['package_price'] == '':
            price = request.POST['package_price']
        weight = 0
        if not request.POST['package_weight'] == '':
            weight = request.POST['package_weight']
        shipping_user_id = request.POST['shipping_user_id']
        create_time = request.POST['create_time']
        try:
            curOrder = Order.objects.get(id=order_id)
            curOrder.price = price
            curOrder.weight = weight
            curOrder.sender=sender
            curOrder.receiver=receiver
            curOrder.save()
            return render(request, 'kd/order_edit_success.html', {'order_id' : order_id}) 
        except Order.DoesNotExists:
            return render(request, 'kd/edit_order_failed.html', {'order_id' : order_id})
    return render(request, 'kd/edit_order_failed.html', {'order_id' : order_id})

@csrf_protect
def edit_external_order_info_show(request):
    if request.user.is_authenticated()==False or request.user.email != Order.objects.get(id=request.GET['order_id']).shipping_user_id:
        return render(request, 'kd/search_order_failed.html', {'order_id' : request.GET['order_id']})
    if request.method == "GET":
        order_id = request.GET['order_id']
        external_order_id=''
        external_checking_method=''
        if ExternalOrder.objects.filter(order=order_id).exists():
            external_order_objects=ExternalOrder.objects.filter(order=order_id)
            external_order_id=external_order_objects.values()[0]['external_order_id']
            external_checking_method=external_order_objects.values()[0]['external_checking_method']
        return render(request, 'kd/edit_external_order_info_show.html', 
                {'external_order_id' : external_order_id, 'external_checking_method' : external_checking_method, 'order_id' : order_id })  
    return render(request, 'kd/search_order_failed.html', {})

@csrf_protect
def edit_external_order_info(request):
    if request.user.is_authenticated()==False:
        return render(request, 'kd/home.html', {})
    if request.method == "POST":
        order_id = request.POST['order_id']
        curOrder = Order.objects.get(id=order_id)
        external_order_id = request.POST['external_order_id']
        external_checking_method = request.POST['external_checking_method']
        old_external_order_id = request.POST['old_external_order_id']
        if ExternalOrder.objects.filter(external_order_id=old_external_order_id).exists():
            ExternalOrder.objects.filter(external_order_id=old_external_order_id).delete()
            # curExternalOrder = ExternalOrder.objects.get(order=order_id)
            # curExternalOrder.external_order_id = external_order_id
            # curExternalOrder.external_checking_method = external_checking_method
            # curExternalOrder.save()
        if (not external_order_id == '') or (not external_checking_method == ''):
            ExternalOrder.objects.create(order=curOrder,
                external_order_id=external_order_id,
                external_checking_method=external_checking_method)
        return render(request, 'kd/order_edit_success.html', {'order_id' : order_id})

    return render(request, 'kd/edit_order_failed.html', {'order_id' : order_id})

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
        empty_items, error_items = __form_validator(request.POST)
        if len(empty_items) != 0 or len(error_items) != 0: 
            return render(request, 'kd/order_create_failure.html', {'error_items' : error_items, 'empty_items' : empty_items})
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
        price = 0
        if not request.POST['package_price'] == '':
            price = request.POST['package_price']
        weight = 0
        if not request.POST['package_weight'] == '':
            weight = request.POST['package_weight']

        curOrder = Order.objects.create(id=id,
                price=price,
                weight=weight,
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
        external_order_id = request.POST['external_order_id']
        external_checking_method = request.POST['external_checking_method']
        if (not external_order_id == '') or (not external_checking_method == ''):
            ExternalOrder.objects.create(order=curOrder,
                external_order_id=external_order_id,
                external_checking_method=external_checking_method)
        
    return render(request, 'kd/order_create_success.html', {'order_id' : id}) 


@csrf_protect
def quote(request):
    return render(request, 'kd/create_quote.html')

@csrf_protect
def create_quote(request):
    if request.method == "POST":
        #empty_items, error_items = __form_validator(request.POST)
        #if len(empty_items) != 0 or len(error_items) != 0: 
        #    return render(request, 'kd/quote_create_failure.html', {'error_items' : error_items, 'empty_items' : empty_items})
        id = __generate_order_id()
        sender=__check_enduser_exists(request.POST['sender_name'], 
            request.POST['sender_phone_number'], 
            request.POST['sender_company_name'], 
            request.POST['sender_address'], 
            request.POST['sender_postcode'])
        # receiver=__check_enduser_exists(request.POST['receiver_name'], 
        #     request.POST['receiver_phone_number'], 
        #     request.POST['receiver_company_name'], 
        #     request.POST['receiver_address'], 
        #     request.POST['receiver_postcode'])
        weight = 0
        if not request.POST['package_weight'] == '':
            weight = request.POST['package_weight']
        height = 0
        if not request.POST['package_height'] == '':
            height = request.POST['package_height']
        width = 0
        if not request.POST['package_width'] == '':
            width = request.POST['package_width']
        length = 0
        if not request.POST['package_length'] == '':
            length = request.POST['package_length']
        curQuote = Quote.objects.create(id=id,
                weight=weight,
                sender_address=request.POST['sender_address'],
                receiver_address= request.POST['receiver_address'],
                create_time=datetime.datetime.now(),
                height= height,
                width= width,
                length= length,
                sender_info=sender,
                notes=request.POST['package_notes']
                )
        QuoteAssignShippingUser.objects.create(quote=curQuote,
            shipping_user_id="",
            primKey=str(id)+str("")
            )
        return render(request, 'kd/quote_create_success.html', {'order_id' : id})
    return render(request, 'kd/quote_create_success.html', {'order_id' : "unknow"})

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
    while Order.objects.filter(id=random_id).exists()  or Quote.objects.filter(id=random_id).exists():
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

def __update_enduser(user_name, phone_number, company_name, address, postcode):
    if EndUser.objects.filter(name=user_name, phone_number=phone_number).exists():
        userObject = EndUser.objects.get(name=user_name, phone_number=phone_number)
        userObject.company_name=company_name
        userObject.postcode=postcode
        userObject.address=address
        userObject.save()
        return userObject
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
                         'receiver_name',
                         'receiver_phone_number',
                         'receiver_address'
                         ]
    en_to_cn = {'sender_name' : u"寄件人姓名",
                'sender_phone_number' : u"寄件人联系方式",
                'receiver_name' : u"收件人姓名",
                'receiver_phone_number' : u"收件人联系方式",
                'receiver_address' : u"收件人地址"}
    empty_items = []
    error_items = []
    for item in must_filled_items:
        if not form[item]:
            empty_items.append(en_to_cn[item])


    return empty_items, error_items
