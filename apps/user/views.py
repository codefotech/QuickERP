from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from system.auth import authenticate_user
from apps.user.models import Users, UserTypes
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils.safestring import mark_safe
from django.contrib.auth import login as system_login, logout

from system.auth.permission import get_permitted_url_list_by_user_type
from system.utils import CommonFunction, get_app_urls
from django.contrib import messages
from apps.user.forms import UserAddForm, UserLoginForm
from django.contrib.auth import logout
from django.db.models import Q
from system.sms.send_sms import send_sms
import random
from datetime import datetime, timedelta
from system.utils import hash_password


# Create your views here.

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            if email and password:
                user = authenticate_user(email=email, password=password)
                if user:
                    request.session['logged_in_pass'] = True
                    system_login(request, user)
                    return redirect('/dashboard')
                else:
                    form.add_error(None, "Invalid login credentials")
    else:
        form = UserLoginForm()

    return render(request, 'frontend/login.html', {'form': form})


def logout_view(request):
    logout(request)
    # Redirect to a page after logging out (e.g., home page)
    return redirect('login')


def index(request, *args, **kwargs):
    return render(request, 'backend/system/user/index.html')


def data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'user_email', 'user_type', 'user_mobile', 'user_status']

    reverse = False
    query = Users.objects.all()
    if request.user.user_type == "SUA-3003":
        # codes_to_exclude = ['GA-4004']
        # query = Users.objects.exclude(Q(user_type__in=codes_to_exclude))
        query = Users.objects.filter(user_type='GA-4004', user_status=1).all()

    elif request.user.user_type == "GA-4004" or request.user.user_type == 'RS-5005' or request.user.user_type == 'GA-6006':
        # codes_to_exclude = ['GA-4004']
        # query = Users.objects.exclude(Q(user_type__in=codes_to_exclude))
        query = Users.objects.filter(user_type='G-1001', user_status=1, admin=request.user.id).all()

    search_value = request.GET.get('search[value]')

    if search_value:
        if request.user.user_type == "SUA-3003":
            query = Users.objects.search_by_user_name(search_value).filter(user_type='GA-4004', user_status=1)
        elif request.user.user_type == "GA-4004" or request.user.user_type == 'RS-5005' or request.user.user_type == 'GA-6006':
            query = Users.objects.search_by_user_name(search_value).filter(user_type='G-1001', user_status=1,
                                                                           admin=request.user.id)

    order_column = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')

    # Map the column index to the column name

    data = query
    if columns[order_column]:
        if order_dir == 'desc':
            reverse = True
        data = sorted(data, key=lambda p: getattr(p, columns[order_column]), reverse=reverse)
    # Paginate data
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
        'recordsTotal': Users.objects.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }

    count = 0
    for data in page_data:
        count = count + 1
        edit = f'<a href="/user/edit/{data.id}" class="btn btn-warning m-1"> Edit</a>'

        action_html = f'<div style="text-align:left;"><a href="/user/view/{data.id}" class="btn btn-primary m-1"> Open</a>' + edit + '</div>'

        user_type = data.user_type_name

        if request.user.user_type == 'GA-4004' or request.user.user_type == 'SR-6006' or request.user.user_type == 'RS-5005':
            user_type = data.user_role_name
        response_data['data'].append({
            'count': count,
            'id': data.id,
            'name': data.name,
            'email': data.email,
            'user_type': user_type,
            'mobile': data.user_mobile,
            'status': data.status,
            'action': mark_safe(action_html),

        })

    return JsonResponse(response_data)


def add(request):
    context = {}
    form = UserAddForm()
    if request.method == 'POST':
        form = UserAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/user')
        elif form.errors:
            messages.error(request, form.errors)

    if request.user.is_sysadmin:
        context['user_types'] = CommonFunction.model_to_dict(model=UserTypes, key='code', value='name',
                                                             order_by='id')
    if request.user.is_supadmin:
        codes_to_exclude = ['SA-2002', 'SUA-3003']
        query = UserTypes.objects.exclude(Q(code__in=codes_to_exclude))
        context['user_types'] = CommonFunction.model_to_dict(model=UserTypes, key='code', value='name',
                                                             order_by='id', query=query)
    if request.user.user_type == 'GA-4004':
        context['user_roles'] = {1: 'Manager', 2: 'Staff', 3: 'Store'}

    context['status'] = {1: 'Active', 0: 'Inactive'}
    context['form'] = form
    return render(request, 'backend/system/user/add.html', context=context)


def edit(request, id=None):
    context = {}
    if id is not None:
        user = get_object_or_404(Users, id=id)
    else:
        user = None

    form = UserAddForm()
    if request.method == 'POST':
        form = UserAddForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('/user')
        elif form.errors:
            messages.error(request, form.errors)

    if request.user.is_sysadmin:
        context['user_types'] = CommonFunction.model_to_dict(model=UserTypes, key='code', value='name',
                                                             order_by='id')
    if request.user.is_supadmin:
        codes_to_exclude = ['SA-2002', 'SUA-3003']
        query = UserTypes.objects.exclude(Q(code__in=codes_to_exclude))
        context['user_types'] = CommonFunction.model_to_dict(model=UserTypes, key='code', value='name',
                                                             order_by='id', query=query)
    if request.user.user_type == 'GA-4004':
        context['user_roles'] = {1: 'Manager', 2: 'Staff', 3: 'Store'}

    context['status'] = {1: 'Active', 0: 'Inactive'}
    context['form'] = form
    context['data'] = user
    return render(request, 'backend/system/user/edit.html', context=context)


def user_type_data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'user_email', 'user_type', 'user_mobile', 'user_status']

    reverse = False
    query = UserTypes.objects.all()

    search_value = request.GET.get('search[value]')

    if search_value:
        query = Users.objects.search_by_user_name(search_value)

    order_column = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')

    # Map the column index to the column name

    data = query
    if columns[order_column]:
        if order_dir == 'desc':
            reverse = True
        data = sorted(data, key=lambda p: getattr(p, columns[order_column]), reverse=reverse)
    # Paginate data
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
        'recordsTotal': Users.objects.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }

    count = 0
    for data in page_data:
        count = count + 1

        action_html = f'<div style="text-align:left;"><a href="/user/assign_permission/{data.id}" class="btn btn-primary m-1"> Assign Permission</a></div>'

        response_data['data'].append({
            'count': count,
            'id': data.id,
            'name': data.name,
            'code': data.code,
            'status': data.status,
            'action': mark_safe(action_html),

        })

    return JsonResponse(response_data)


def user_permission(request):
    return render(request, 'backend/system/user/permission_list.html')


def assign_permission(request, id):
    context = {
        'get_app_urls': get_app_urls(),
        'id': id,
    }
    assign_data = {}
    if request.POST:
        for key, value in request.POST.items():
            if value == 'on':
                key_parts = key.split('.')
                if len(key_parts) == 2:
                    main_key, sub_key = key_parts
                    if main_key not in assign_data:
                        assign_data[main_key] = [sub_key]
                    else:
                        assign_data[main_key].append(sub_key)

        user_type = UserTypes.objects.get(id=id)
        user_type.permission = assign_data
        user_type.save()

    context['permission_list'] = get_permitted_url_list_by_user_type(id)
    context['user_type'] = UserTypes.objects.get(id=id)

    return render(request, 'backend/system/user/assign_permission.html', context)


def sendotp(request):
    return render(request, 'frontend/sendotp.html')


def forgot_pass(request):
    import base64
    if request.POST:
        try:
            number = request.POST.get('user_mobile')
            if Users.objects.filter(user_mobile=number).exists():
                otp_code = random.randint(1000, 9999)
                user = Users.objects.filter(user_mobile=number).first()
                user.remember_token = otp_code
                user.otp_expire_time = datetime.now() + timedelta(minutes=2)
                user.save()
                messages = f'Your otp code is {otp_code}'
                send_sms(number, messages)
                return JsonResponse(
                    {'success': True, 'number': number, 'message': f'Otp Send to Your Mobile Number {number}'})
            else:
                return JsonResponse({'error': True, 'message': f'There have no user with this number {number}'})
        except Exception as e:
            return JsonResponse(
                {'error': True, 'message': f'{e}[M-105]'})

    return render(request, 'frontend/forgot_pass.html')


def submit_otp(request):
    if request.POST:
        otp = request.POST.get('otp')
        number = request.POST.get('mobile')
        user = Users.objects.filter(user_mobile=number).first()
        if user.remember_token == otp:
            if user.otp_expire_time > datetime.now():
                if user.remember_token == otp:
                    return JsonResponse(
                        {'success': True, 'number': number, 'email': user.email, 'message': 'OTP Verified'})

            else:
                return JsonResponse({'error': True, 'message': 'Your OTP have expired'})
        else:
            return JsonResponse({'error': True, 'message': "Wrong OTP given!"})


def reset_password(request):
    if request.POST:
        try:
            password = request.POST.get('password')
            email = request.POST.get('email')
            if email:
                user = Users.objects.filter(email=email).first()
                user.password = hash_password(password)
                user.save()
                return JsonResponse(
                    {'success': True, 'message': 'Password changed'})
        except Exception as e:
            return JsonResponse(
                {'error': True, 'message': f'{e}[M-106]'})

    return render(request, 'frontend/error-404.html')


def verify_email(request):
    return render(request, 'frontend/verify_email.html')


def countries(request):
    return render(request, 'backend/system/user/others/countries.html')


def states(request):
    return render(request, 'backend/system/user/states.html')


def cities(request):
    return render(request, 'backend/system/user/others/cities.html')


def zones(request):
    return render(request, 'backend/system/user/zones.html')


def wallet_recharge_history(request):
    return render(request, 'backend/system/user/wallet_recharge_history.html')


def ticket(request):
    return render(request, 'backend/system/user/ticket.html')


def header(request):
    return render(request, 'backend/system/user/others/header.html')


def footer(request):
    return render(request, 'backend/system/user/others/footer.html')


def pages(request):
    return render(request, 'backend/system/user/others/pages.html')


def appearance(request):
    return render(request, 'backend/system/user/others/appearance.html')


def general_settings(request):
    return render(request, 'backend/system/user/others/general_settings.html')


def languages(request):
    return render(request, 'backend/system/user/languages.html')


def currency(request):
    return render(request, 'backend/system/user/others/currency.html')


def smtp_settings(request):
    return render(request, 'backend/system/user/smtp_settings.html')


def payment_methods(request):
    return render(request, 'backend/system/user/others/payment_methods.html')


def file_system_and_cache_configuration(request):
    return render(request, 'backend/system/user/others/file_system_and_cache_configuration.html')


def social_media_logins(request):
    return render(request, 'backend/system/user/social_media_logins.html')


def facebook_chat(request):
    return render(request, 'backend/system/user/others/facebook_chat.html')


def facebook_comment(request):
    return render(request, 'backend/system/user/others/facebook_comment.html')


def analytics_tools(request):
    return render(request, 'backend/system/user/others/analytics_tools.html')


def google_recaptcha(request):
    return render(request, 'backend/system/user/others/google_recaptcha.html')


def google_map(request):
    return render(request, 'backend/system/user/others/google_map.html')


def google_firebase(request):
    return render(request, 'backend/system/user/others/google_firebase.html')


def server_status(request):
    return render(request, 'backend/system/user/others/server_status.html')
