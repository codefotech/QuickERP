from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

# Create your views here.
from apps.hotspot_customer.models import HotspotCustomer
from apps.hotspot_package.models import SellerHotspotPackage
from apps.payment.models import PackagePurchaseHistory, BkashPackagePurchaseRequest
from system.utils import paginate_data, paginate_data_with_raw_query
from django.db import connection


def income(request):
    pass


def expense(request):
    pass


def bkash_purchase_history(request):
    if request.method == 'POST':
        raw_query = """
                         SELECT bkash_payment_purchase_request.invoice_no , 
                         bkash_payment_purchase_request.payment_id,
                         bkash_payment_purchase_request.transaction_id,
                         hotspot_customer.mobile,
                         hotspot_packages.name,
                         bkash_payment_purchase_request.amount,
                         bkash_payment_purchase_request.updated_at,
                         bkash_payment_purchase_request.status
                         FROM bkash_payment_purchase_request
                         INNER JOIN hotspot_packages ON hotspot_packages.id = bkash_payment_purchase_request.package_id
                         INNER JOIN hotspot_customer ON hotspot_customer.id = bkash_payment_purchase_request.customer_id
                         INNER JOIN users ON users.id = hotspot_customer.admin_id
                         """
        where_condition = []
        where_condition.append(f"bkash_payment_purchase_request.status = 1")

        if request.user.user_type == 'RS-5005':
            where_condition.append(f"hotspot_customer.admin_id = {request.user.id}")

        elif request.user.user_type == 'GA-4004':
            where_condition.append(f"hotspot_customer.admin_id = {request.user.id}")

        elif request.user.user_type == 'SA-2002':
            pass

        search_value = request.POST.get('search[value]')

        if search_value:
            where_condition.append(
                f"hotspot_customer.mobile like '%{search_value}%' "
                f"or bkash_payment_purchase_request.transaction_id like '%{search_value}%' ")

        if where_condition:
            where_clause = "WHERE " + " AND ".join(where_condition)
            raw_query = raw_query + where_clause
        else:
            raw_query = raw_query

            # Execute the raw SQL query
        with connection.cursor() as cursor:
            cursor.execute(raw_query)
            rows = cursor.fetchall()

            data = rows

        response_data, page_data = paginate_data_with_raw_query(data, request)

        count = 0

        for data in page_data:
            print(data[7])
            if data[7] == 0:
                status = f'<a class="btn btn-warning ml-2" class="" > Initiated </a>'
            else:
                status = f'<a class="btn btn-success ml-2" class="" > Success </a>'

            count = count + 1
            response_data['data'].append({
                'count': count,
                'invoice': data[0],
                'payment_id': data[1],
                'transaction_id': data[2],
                'customer': data[3],
                'package_name': data[4],
                'amount': str(data[5]) + ' TK',
                'updated_at': data[6].strftime('%d-%B-%Y %H:%M:%S'),
                'status': mark_safe(status)
            })
        return JsonResponse(response_data)

    return render(request, 'backend/system/reports/bkash_package_purchase_with_gateway.html')


def bkash_purchase_history_date(request):
    columns = [None, 'name', 'mobile']

    reverse = False
    query = PackagePurchaseHistory.objects.filter(admin_id=request.user.id).all()
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

    count = 0
    for data in page_data:
        count = count + 1

        response_data['data'].append({
            'count': count,
            'id': data.id,
            'customer': data.name,
            'mobile': data.mobile,
        })

    return JsonResponse(response_data)
