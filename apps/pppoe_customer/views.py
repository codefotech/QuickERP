import datetime
import calendar

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.safestring import mark_safe

from apps.config.models import GeneralAdminConfig
from apps.package.forms import PackageAddForm
from apps.package.models import Package, SellerPackage
from apps.pppoe_customer.forms import PPPoeCustomerAddForm
from apps.pppoe_customer.models import PPPOECustomer
from apps.router.models import Router
from apps.seller.models import Seller
from apps.user.models import Users
from system.router.ssh_router import add_pppoe_user
from system.utils import CommonFunction, paginate_data
from django.db.models import F, Func, Value, CharField
from django.contrib import messages
from django.db import transaction


def index(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.user.user_type == 'SA-2002':
            data = PPPOECustomer.objects.filter(admin_id=request.user.id, status=0).all()
        else:
            data = PPPOECustomer.objects.filter(status=0).all()
        response_data, page_data = paginate_data(PPPOECustomer, data, request)

        count = 0
        for data in page_data:
            count = count + 1
            action_html = f'<a class="btn btn-info" href="/pppoe_customer/edit/{data.id}" ><i class="fas fa-edit primary-icon"></i> Edit</a>'
            response_data['data'].append({
                'count': count,
                'name': data.name,
                'pppoe_user': data.pppoe_user,
                'pppoe_pass': data.pppoe_password,
                'phone': data.mobile,
                'package': data.package.name if data.package and data.package.name else '',
                'bill_amount': data.bill_amount,
                'bill_day': data.bill_day,
                'upload_download': '',
                'connected_status': '',
                'enable_disable': '',
                'status': '',
                'expire_at': data.expire_at.strftime("%Y-%m-%d %H:%M:%S"),
                'created_at': data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'action': mark_safe(action_html)
            })
        return JsonResponse(response_data)
    return render(request, 'backend/main/pppoe_customer/index.html')


@transaction.atomic
def add(request):
    context = {}

    if request.method == 'POST':
        form = PPPoeCustomerAddForm(request.POST.copy())
        if form.is_valid():
            # form.save()

            if request.user.user_type == 'RS-5005':
                seller = Seller.objects.filter(user_id=request.user.id).first()
                package = SellerPackage.objects.filter(package_id=request.POST.get('package_id'),
                                                       seller_id=seller.id).first()
                if datetime.date.today().day < int(seller.free_user_create_deadline):
                    price = package.price
                    bill_day = int(request.POST.get('bill_day'))

                    print('Price :', price)
                    print('Bill Day :', bill_day)
                    print('Last Day Of Create User :', 29)

                    today_date = datetime.date.today()

                    remaining_days = bill_day
                    months = 1
                    total_price = 0

                    while remaining_days > 0:
                        start_of_month = today_date.replace(day=1, month=today_date.month)
                        if today_date.month != 12:
                            end_of_month = today_date.replace(day=1, month=today_date.month + 1) - datetime.timedelta(
                                days=1)
                        elif today_date.month == 12:
                            end_of_month = today_date.replace(day=1, month=1,
                                                              year=today_date.year + 1) - datetime.timedelta(
                                days=1)

                        print(today_date.strftime("%B"))
                        print(start_of_month)
                        print(end_of_month)

                        # Calculate the number of days remaining in the current month
                        if today_date.month == datetime.date.today().month:
                            days_in_current_month = (end_of_month - today_date).days

                            price_for_the_month = float(price) / end_of_month.day
                            total_price = total_price + (price_for_the_month * days_in_current_month)
                            print('days in current month used:', days_in_current_month)

                            remaining_days -= days_in_current_month
                            print('remaining days', remaining_days if remaining_days > 0 else 0)

                        else:
                            days_in_current_month = end_of_month.day
                            if remaining_days > days_in_current_month:
                                price_for_the_month = float(price) / end_of_month.day
                                total_price = total_price + (price_for_the_month * days_in_current_month)
                                print('days in current month used:', days_in_current_month)
                            else:
                                price_for_the_month = float(price) / end_of_month.day
                                total_price = total_price + (price_for_the_month * remaining_days)
                                print('days in current month used:', remaining_days)

                            remaining_days -= days_in_current_month
                            print('remaining days', remaining_days if remaining_days > 0 else 0)

                        # Move to the next month
                        if today_date.month != 12:
                            today_date = today_date.replace(day=1, month=today_date.month + 1)
                        elif today_date.month == 12:
                            today_date = today_date.replace(day=1, month=1, year=today_date.year + 1)

                        # Increment the month counter
                        if remaining_days > 0:
                            months += 1

                    user = Users.objects.filter(id=request.user.id).first()
                    seller_wallet = user.wallet_balance
                    if float(seller_wallet) > float(total_price):
                        user.wallet_balance = float(user.wallet_balance) - float(total_price)
                        user.save()
                        form.instance.expire_at = datetime.datetime.today() + datetime.timedelta(int(bill_day))
                        form.save()
                        package = Package.objects.filter(id=request.POST.get('package_id')).first()
                        add_pppoe_user(package.router_id, package.profile, request.POST.get('pppoe_user'),
                                       request.POST.get('pppoe_password'))
                        return redirect('pppoe_customer_list')

                    else:
                        messages.error(request, 'Your wallet balance is very low. Please try again after add balance.')

                        context['form'] = form
                        query = Package.objects.filter(admin_id=request.user.id)
                        context['package_list'] = CommonFunction.model_to_dict(model=None, query=query, key='id',
                                                                               value='name')

                        if request.user.user_type == 'GA-4004':
                            router_ids = GeneralAdminConfig.objects.filter(admin_id=request.user.id).first().router_list
                            query = Package.objects.filter(admin_id=request.user.id,
                                                           router_id__in=eval(router_ids)).all()
                            context['package_list'] = CommonFunction.model_to_dict(model=None, query=query, key='id',
                                                                                   value='name')

                        elif request.user.user_type == 'RS-5005':
                            seller_id = Seller.objects.filter(user_id=request.user.id).first().id
                            query = SellerPackage.objects.filter(seller_id=seller_id).annotate(
                                concatenated_value=Func(F('package__name'), Value(' - '),
                                                        F('price'), Value(' TK'), function='CONCAT',
                                                        output_field=CharField()))
                            context['package_list'] = CommonFunction.model_to_dict(model=None, query=query,
                                                                                   key='package_id',
                                                                                   value='concatenated_value')

                        return render(request, 'backend/main/pppoe_customer/add.html', context=context)

    else:
        form = PackageAddForm()
    context['form'] = form
    query = Package.objects.filter(admin_id=request.user.id)
    context['package_list'] = CommonFunction.model_to_dict(model=None, query=query, key='id', value='name')

    if request.user.user_type == 'GA-4004':
        router_ids = GeneralAdminConfig.objects.filter(admin_id=request.user.id).first().router_list
        query = Package.objects.filter(admin_id=request.user.id, router_id__in=eval(router_ids)).all()
        context['package_list'] = CommonFunction.model_to_dict(model=None, query=query, key='id', value='name')

    elif request.user.user_type == 'RS-5005':
        seller_id = Seller.objects.filter(user_id=request.user.id).first().id
        query = SellerPackage.objects.filter(seller_id=seller_id).annotate(
            concatenated_value=Func(F('package__name'), Value(' - '),
                                    F('price'), Value(' TK'), function='CONCAT',
                                    output_field=CharField()))
        context['package_list'] = CommonFunction.model_to_dict(model=None, query=query, key='package_id',
                                                               value='concatenated_value')

    return render(request, 'backend/main/pppoe_customer/add.html', context=context)


def edit(request, id=None):
    context = {}
    if id is not None:
        customer = get_object_or_404(PPPOECustomer, id=id)
    else:
        customer = None

    if request.method == 'POST':
        form = PPPoeCustomerAddForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('pppoe_customer_list')
    else:
        form = PPPoeCustomerAddForm(instance=customer)
    context['data'] = customer
    context['form'] = form
    query = Package.objects.filter(admin_id=request.user.id)
    context['package_list'] = CommonFunction.model_to_dict(model=None, query=query, key='id', value='name')
    if request.user.user_type == 'GA-4004':
        router_ids = GeneralAdminConfig.objects.filter(admin_id=request.user.id).first().router_list
        query = Package.objects.filter(admin_id=request.user.id, router_id__in=eval(router_ids)).all()
        context['package_list'] = CommonFunction.model_to_dict(model=None, query=query, key='id', value='name')

    elif request.user.user_type == 'RS-5005':
        seller_id = Seller.objects.filter(user_id=request.user.id).first().id
        query = SellerPackage.objects.filter(seller_id=seller_id).annotate(
            concatenated_value=Func(F('package__name'), Value(' - '),
                                    F('price'), Value(' TK'), function='CONCAT',
                                    output_field=CharField()))
        context['package_list'] = CommonFunction.model_to_dict(model=None, query=query, key='id',
                                                               value='concatenated_value')
    return render(request, 'backend/main/pppoe_customer/edit.html', context=context)
