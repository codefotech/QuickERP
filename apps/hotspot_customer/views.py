import json
import random
from datetime import timedelta, datetime
from django.shortcuts import render, redirect, get_object_or_404

from apps.hotspot_customer.api_view import create_router_user, enable_ssh_router_user, generate_customer_token
from apps.hotspot_customer.models import HotspotCustomer, HotspotCustomerToken
from apps.hotspot_customer.forms import HotspotCustomerAddForm
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils.safestring import mark_safe
from django.contrib import messages

from apps.hotspot_router.models import HotspotActiveUser, HotspotHostIpMac
from system.Encryption import Encryption
from system.sms.send_sms import send_sms
from system.utils import CommonFunction, get_app_urls
from apps.hotspot_package.models import HotspotPackage, SellerHotspotPackage
from apps.seller.models import Seller, SellerExpense
from django.db.models import F, Func, Value, CharField
from system.enums.enum import ExpenseTypeEnum
from django.db import transaction
from apps.user.models import Users


def index(request, *args, **kwargs):
    get_app_urls()
    return render(request, 'backend/main/hotspot_customer/index.html')


def data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'mobile']

    reverse = False
    query = HotspotCustomer.objects.filter(admin_id=request.user.id).all()
    search_value = request.GET.get('search[value]')
    if search_value:
        query = HotspotCustomer.objects.search_by_data(search_value).filter(admin_id=request.user.id)

    if request.user.user_type == "SA-2002" or request.user.user_type == 'SUA-3003':
        query = HotspotCustomer.objects.all()
        if search_value:
            query = HotspotCustomer.objects.search_by_data(search_value)

    order_column = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')
    data = query
    if columns[order_column]:
        if order_dir == 'desc':
            reverse = True
        data = sorted(data, key=lambda p: getattr(p, columns[order_column]), reverse=reverse)
    if request.GET.get('start') and request.GET.get('length'):
        page = int(request.GET.get('start')) // int(request.GET.get('length')) + 1
    else:
        page = 0

    per_page = str(request.GET.get('length') if request.GET.get('length') else 25)
    paginator = Paginator(data, per_page)
    page_data = paginator.get_page(page)

    # Build response data
    response_data = {
        'draw': request.GET.get('draw'),
        'recordsTotal': query.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }
    user = HotspotHostIpMac.objects.exclude(comment__exact='').all()
    active_user = []
    for value in user:
        active_user.append(value.comment)

    count = 0
    for data in page_data:
        count = count + 1

        add_balance = f'<a class="btn btn-primary ml-2" onclick="add_balance({data.id})" class="" > Add Validity </a>'
        action_html = f'<a class="btn btn-primary" href="/hotspot_customers/edit/{data.id}" class="" > <i class="fas fa-edit primary-icon"></i> </a>' + add_balance

        countdown = f'''<div class="countdown" data-date="{data.package_expire_date.strftime('%Y-%m-%dT%H:%M:%S')}"><span class="days">0 days</span>
                     <span class="hours">0 hours</span> <span class="minutes">0 minutes
                     </span> <span class="seconds">0 seconds</span></div>'''

        status = '<i class="fa-solid fa-circle text-success"></i>'
        update = f'<br><a class="btn btn-primary ml-2 mt-1" onclick="update_ip({data.id})" class="" > Update </a>'
        status_val = 1
        if data.mobile[3:] not in active_user:
            status = '<i class="fa-solid fa-circle text-danger"></i>'
            status_val = 0
        expire_date = data.package_expire_date.strftime("%d %B %Y")

        if data.package_expire_date < datetime.now():
            expire_date = mark_safe('<span class="text-danger font-weight-bold">Expired</span>')

        response_data['data'].append({
            'count': count,
            'id': data.id,
            'name': data.name,
            'mac_address': data.mac_address + update if data.mac_address else '' + update,
            'mobile': data.mobile,
            'validity': mark_safe(countdown),
            'expire_date': expire_date,
            'status': mark_safe(status),
            'status_val': status_val,
            'action': mark_safe(action_html),

        })

    return JsonResponse(response_data)


def add(request):
    context = {}
    form = HotspotCustomerAddForm()
    if request.method == 'POST':
        form = HotspotCustomerAddForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('hotspot_customer_list')
        elif form.errors:
            messages.error(request, form.errors)
    context['form'] = form
    return render(request, 'backend/main/hotspot_customer/add.html', context=context)


def edit(request, id=None):
    context = {}
    if id is not None:
        hotspot_customer = get_object_or_404(HotspotCustomer, id=id)
    else:
        hotspot_customer = None

    if request.method == 'POST':
        form = HotspotCustomerAddForm(request.POST, instance=hotspot_customer)
        if form.is_valid():
            form.save()
            return redirect('hotspot_customer_list')
    else:
        form = HotspotCustomerAddForm(instance=hotspot_customer)

    query = Users.objects.all()
    context['user_data'] = CommonFunction.model_to_dict(model=None, query=query, key='id', value='username')
    context['data'] = hotspot_customer
    context['form'] = form
    return render(request, 'backend/main/hotspot_customer/edit.html', context=context)


@transaction.atomic
def hotspot_customer_validity_add(request):
    if request.method == 'GET':
        customer_id = request.GET.get('customer_id')
        if request.user.user_type == 'GA-4004':
            query = (HotspotPackage.objects.filter(admin_id=request.user.id, status=1)
                     .annotate(concatenated_value=Func(F('name'), Value(' - '),
                                                       F('price'), Value(' TK'), function='CONCAT',
                                                       output_field=CharField())))

            package = CommonFunction.model_to_dict(model=None, key='id', value='concatenated_value', query=query)

        elif request.user.user_type == 'RS-5005':
            if round(float(request.user.wallet_balance)) <= 0:
                return JsonResponse({'error': "Your wallet haven't enough balance"}, status=302)
            seller = Seller.objects.filter(user_id=request.user.id).first()
            seller_package = SellerHotspotPackage.objects.filter(admin_id=seller.admin_id, seller_id=seller.id).all()
            result = SellerHotspotPackage.objects.filter(admin_id=seller.admin_id, seller_id=seller.id) \
                .annotate(concatenated_value=Func(F('package__name'), Value(' - '),
                                                  F('price'), Value(' TK'), function='CONCAT',
                                                  output_field=CharField()))
            package = CommonFunction.model_to_dict(model=None, key='package_id', value='concatenated_value',
                                                   query=result)

        elif request.user.user_type == 'SR-6006':
            if round(float(request.user.wallet_balance)) <= 0:
                return JsonResponse({'error': "Your wallet haven't enough balance"}, status=302)
            reseller = Seller.objects.filter(user_id=request.user.id).first()
            seller = Seller.objects.filter(user_id=reseller.admin_id).first()
            result = SellerHotspotPackage.objects.filter(admin_id=seller.admin_id, seller_id=seller.id) \
                .annotate(concatenated_value=Func(F('package__name'), Value(' - '),
                                                  F('price'), Value(' TK'), function='CONCAT',
                                                  output_field=CharField()))
            package = CommonFunction.model_to_dict(model=None, key='package_id', value='concatenated_value',
                                                   query=result)

        else:
            query = (HotspotPackage.objects.filter(admin_id=request.user.id, status=1)
                     .annotate(concatenated_value=Func(F('name'), Value(' - '),
                                                       F('price'), Value(' TK'), function='CONCAT',
                                                       output_field=CharField())))

            package = CommonFunction.model_to_dict(model=None, key='id', value='concatenated_value', query=query)

        context = {
            'customer_id': customer_id,
            'package': package
        }
        return render(request, 'backend/main/hotspot_customer/add_validity.html', context=context)

    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        if not package_id:
            return JsonResponse({'error': "Please select a package!!!"}, status=302)
        else:
            if request.user.user_type == 'RS-5005':
                seller = Seller.objects.filter(user_id=request.user.id).first()
                package = SellerHotspotPackage.objects.filter(seller_id=seller.id, package_id=package_id).first()
                if float(package.price) > float(request.user.wallet_balance):
                    return JsonResponse({'error': "Your wallet haven't enough balance!!!"}, status=302)
                else:
                    try:
                        customer_id = request.POST.get('customer_id')
                        customer = HotspotCustomer.objects.get(id=customer_id)
                        previous_date = customer.package_expire_date
                        if customer.package_expire_date < datetime.now():
                            customer.package_expire_date = datetime.now() + timedelta(
                                days=int(package.package.day))
                        else:
                            customer.package_expire_date = customer.package_expire_date + timedelta(
                                days=int(package.package.day))

                        customer.save()
                        if previous_date < datetime.now():
                            enable_ssh_router_user(customer.mobile, customer.admin_id)
                        seller = Users.objects.filter(id=customer.admin_id).first()
                        seller.wallet_balance = float(seller.wallet_balance) - float(package.price)
                        seller.save()

                        expense_history = SellerExpense()
                        expense_history.customer_id = customer_id
                        expense_history.expense_amount = package.price
                        expense_history.expense_purpose = ExpenseTypeEnum.add_balance
                        expense_history.expense_by = request.user.id
                        expense_history.save()

                        return JsonResponse({'success': "Validity Added Successfully......"}, status=201)
                    except Exception as e:
                        return JsonResponse({'error': "System Have Query Error [E-HC-201] :" + str(e)}, status=302)

            elif request.user.user_type == 'GA-4004':
                package = HotspotPackage.objects.filter(admin_id=request.user.id, id=package_id).first()
                try:
                    customer_id = request.POST.get('customer_id')
                    customer = HotspotCustomer.objects.get(id=customer_id)
                    previous_date = customer.package_expire_date

                    if customer.package_expire_date < datetime.now():
                        customer.package_expire_date = datetime.now() + timedelta(
                            days=int(package.day))
                    else:
                        customer.package_expire_date = customer.package_expire_date + timedelta(
                            days=int(package.day))

                    customer.save()
                    if previous_date < datetime.now():
                        enable_ssh_router_user(customer.mobile, customer.admin_id)

                    expense_history = SellerExpense()
                    expense_history.customer_id = customer_id
                    expense_history.expense_amount = package.price
                    expense_history.expense_purpose = ExpenseTypeEnum.add_balance
                    expense_history.expense_by = request.user.id
                    expense_history.save()

                    return JsonResponse({'success': "Validity Added Successfully......"}, status=201)
                except Exception as e:
                    return JsonResponse({'error': "System Have Query Error [E-HC-201] :" + str(e)}, status=302)


def get_hotspot_customer_active_status(request):
    user = HotspotHostIpMac.objects.exclude(comment__exact='').all()
    active_user = []
    for value in user:
        active_user.append(value.comment)

    if request.POST.get('data'):
        data = json.loads(request.POST.get('data'))
        customers = HotspotCustomer.objects.filter(id__in=data).all()
        router_data = {}
        for i in customers:
            mobile = i.mobile
            if mobile.startswith("+88"):
                mobile = mobile[3:]

            if mobile not in active_user:
                router_data[i.id] = False
            else:
                router_data[i.id] = True

        return JsonResponse({'data': json.dumps(router_data)})


def hotspot_customer_update_ip(request):
    if request.method == 'GET':
        customer_id = request.GET.get('customer_id')
        context = {
            'customer_id': customer_id
        }
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        ip_address = request.POST.get('ip_address')
        hotspot_host_ip = HotspotHostIpMac.objects.filter(ip_address=ip_address).first()
        if hotspot_host_ip:
            mac_address = hotspot_host_ip.mac_address
            customer = HotspotCustomer.objects.filter(id=customer_id).first()
            if not HotspotCustomer.objects.filter(mac_address=mac_address).exists():
                customer.mac_address = mac_address
                customer.save()
                if customer.package_expire_date > datetime.now():
                    enable_ssh_router_user(customer.mobile, customer.admin_id)

                return JsonResponse({'success': "Mac Update Successfully"}, status=201)

            else:
                return JsonResponse({'error': "Mac Address Already Exist"}, status=302)



        else:
            return JsonResponse({'error': "Invalid Ip Address, No Mac Found"}, status=302)

    return render(request, 'backend/main/hotspot_customer/update_ip.html', context=context)


def hotspot_login(request):
    token = request.session.get('token')
    if token:
        token_data = HotspotCustomerToken.objects.filter(token=token).first()
        if token_data:
            current_time = datetime.now()
            if token_data.expire_at >= current_time and token_data.status != 0:
                customer_id = token_data.customer_id
                customer = HotspotCustomer.objects.get(id=customer_id)
                if customer:
                    return  redirect('hotspot_dashboard')
    error = ''
    context = {'error': error}
    if request.POST:
        mobile = request.POST.get('mobile')
        if len(mobile) > 11 or len(mobile) < 11:
            context['error'] = 'Invalid Phone Number'
        else:
            mobile = '+88' + mobile
            customer = HotspotCustomer.objects.filter(mobile=mobile).first()
            if customer:
                otp_code = random.randint(1000, 9999)
                customer.otp_token = otp_code
                customer.otp_expire_time = datetime.now() + timedelta(minutes=4)
                customer.save()
                message = f'Your OTP code is {otp_code}'
                send_sms(mobile, message)
                messages.success(request, 'OTP sent successfully')
                return redirect('hotspot_user_otp_validate/'+Encryption.encode(mobile))

            else:
                context['error'] = 'You are not registered user'

        return render(request, 'frontend/hotspot_login.html', context=context)
    return render(request, 'frontend/hotspot_login.html')


def valid_otp(request, mobile):
    token = request.session.get('token')
    if token:
        token_data = HotspotCustomerToken.objects.filter(token=token).first()
        if token_data:
            current_time = datetime.now()
            if token_data.expire_at >= current_time and token_data.status != 0:
                customer_id = token_data.customer_id
                customer = HotspotCustomer.objects.get(id=customer_id)
                if customer:
                    return redirect('hotspot_dashboard')

    if request.POST:
        mobile = Encryption.decode(mobile)
        otp = request.POST.get('otp')
        customer = HotspotCustomer.objects.filter(mobile=mobile).first()
        if str(customer.otp_token) == str(otp):
            token = generate_customer_token(customer.id, customer.otp_token)
            request.session['token'] = token
            messages.success(request, 'Hotspot Successfully logged in')
            return redirect('hotspot_dashboard')
    context = {'mobile': mobile}
    return render(request, 'frontend/valid_otp.html', context=context)


def hotspot_dashboard(request):
    token = request.session.get('token')
    if request.session.get('token'):
        return render(request, 'frontend/hotspot_dashboard.html')
    else:
        if not token:
            return redirect('hotspot_login')

        token_data = HotspotCustomerToken.objects.filter(token=token).first()
        if token_data:
            current_time = datetime.now()
            if token_data.expire_at >= current_time and token_data.status != 0:
                return render(request, 'frontend/hotspot_dashboard.html')

            else:
                request.session['token'] = ''
                return redirect('hotspot_login')

        else:
            request.session['token'] = ''
            return redirect('hotspot_login')



def hotspot_customer_mac_update(request):
    ip_address = request.GET.get('ip_address')
    token = request.session.get('token')
    if token is None:
        response_data = {
            'status': 'error',
            'message': 'Token field is required'
        }
        return JsonResponse(response_data, status=401)

    elif ip_address is None:
        response_data = {
            'status': 'error',
            'message': 'ip_address field is required'
        }
        return JsonResponse(response_data, status=401)

    else:
        token_data = HotspotCustomerToken.objects.filter(token=token).first()
        if token_data:
            current_time = datetime.now()
            if token_data.expire_at >= current_time and token_data.status != 0:
                customer_id = token_data.customer_id
                customer = HotspotCustomer.objects.get(id=customer_id)
                if customer:
                    if customer.package_expire_date >= current_time:
                        ip_address_mac = HotspotHostIpMac.objects.filter(ip_address=ip_address).first()
                        if ip_address_mac:
                            if ip_address_mac.mac_address != customer.mac_address:
                                customer.mac_address = ip_address_mac.mac_address
                                customer.save()

                        response_data = {
                            'status': 'success',
                            'valid': True
                        }
                        return JsonResponse(response_data, status=200)

                    else:
                        response_data = {
                            'status': 'error',
                            'message': "You haven't enough balance.."
                        }
                        return JsonResponse(response_data, status=302)

                else:
                    response_data = {
                        'status': 'error',
                        'message': 'Customer Not Found'
                    }
                    return JsonResponse(response_data, status=404)
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Token has expired'
                }
                return JsonResponse(response_data, status=404)
        else:
            response_data = {
                'status': 'error',
                'message': 'Customer Invalid Token'
            }
            return JsonResponse(response_data, status=404)

    return HttpResponse('Mac Update')