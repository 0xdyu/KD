from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from kd.models import Order, EndUser, ShippingUser, OrderStatus
from django.shortcuts import get_object_or_404
from random import randint
import datetime

# Create your views here.

def home(request):
    return render(request, 'kd/home.html')

@csrf_protect
def user_profile(request):
    return render(request, 'kd/profile.html')

@csrf_protect
def search_order(request):
    if request.method == "GET":
        order_id = request.GET['order_id']
        if OrderStatus.objects.filter(order_id=order_id).exists():
            objects=OrderStatus.objects.filter(order_id=order_id).order_by('-time')
            return render(request, 'kd/order_info.html', 
                {'order_id' : order_id, 
                'order_status' : objects.values('status')[0]['status'], 
                'curr_location' : objects.values('location')[0]['location'],
                'update_time' : objects.values('time')[0]['time']})

        else:
            return render(request, 'kd/search_order_failed.html', {'order_id' : order_id})
        
    return render(request, 'kd/home.html', {})

@csrf_protect
def create(request):
    return render(request, 'kd/create.html')

@csrf_protect
def create_order(request):
    if request.user.is_authenticated()==False:
        return render(request, 'kd/home.html', {})
    if request.method == "POST":
        id = __generate_order_id()
        sender_id=__check_enduser_exists(request.POST['sender_name'], 
            request.POST['sender_phone_number'], 
            request.POST['sender_company_name'], 
            request.POST['sender_address'], 
            request.POST['sender_postcode'])
        receiver_id=__check_enduser_exists(request.POST['receiver_name'], 
            request.POST['receiver_phone_number'], 
            request.POST['receiver_company_name'], 
            request.POST['receiver_address'], 
            request.POST['receiver_postcode'])
        Order.objects.create(id=id,
                weight=request.POST['package_weight'],
                shipping_user_id=request.user.email,
                sender_id=sender_id,
                receiver_id=receiver_id
                )
        OrderStatus.objects.create(order_id=id,
            time=datetime.datetime.now(),
            status=request.POST['package_current_status'],
            location=request.POST['package_current_location'],
            primKey=str(id)+str(datetime.datetime.now())
            )
        
    return render(request, 'kd/create.html', {}) 

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
            return EndUser.objects.get(name=user_name, phone_number=phone_number).user_id;
    user_id = __generate_user_id()
    EndUser.objects.create(user_id=user_id,
            name=user_name,
            phone_number=phone_number,
            company_name=company_name,
            address=address,
            postcode=postcode
            )
    return user_id;
