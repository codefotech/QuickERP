from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from apps.hotspot_package.forms import HotspotPackageAddForm, AssignHotspotPackageForm
from apps.hotspot_package.models import HotspotPackage, SellerHotspotPackage
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from apps.seller.models import Seller
from system.utils import CommonFunction, paginate_data


# Create your views here.

def index(request, *args, **kwargs):
    return render(request, 'backend/main/hotspot_package/index.html')


def data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'profile', 'router']

    reverse = False
    query = HotspotPackage.objects.filter(admin_id=request.user.id, status=1).all()
    search_value = request.GET.get('search[value]')
    if search_value:
        query = HotspotPackage.objects.search_by_data(search_value).filter(admin_id=request.user.id, status=1)

    if request.user.user_type == "SA-2002":
        query = HotspotPackage.objects.all()
        if search_value:
            query = HotspotPackage.objects.search_by_data(search_value)

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
        'recordsTotal': HotspotPackage.objects.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }

    count = 0
    for data in page_data:
        count = count + 1

        action_html = f'<a href="/hotspot_package/edit/{data.id}" class="" > <i class="fas fa-edit primary-icon"></i> </a>'
        if data.status == 1:
            status = mark_safe('<button class="btn btn-success">Active</button>')
        else:
            status = mark_safe('<button class="btn btn-danger">Inactive</button>')

        response_data['data'].append({
            'count': count,
            'id': data.id,
            'name': data.name,
            'day': data.day,
            'price': data.price,
            'status': status,
            'action': mark_safe(action_html),

        })
    # f'<a href="/user/edit/{data.id}" class="btn btn-xs btn-primary"><i class="fa fa-edit"></i> Edit</a>'

    return JsonResponse(response_data)


def add(request):
    context = {}

    if request.method == 'POST':
        form = HotspotPackageAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hotspot_package_list')
    else:
        form = HotspotPackageAddForm()
    context['form'] = form
    return render(request, 'backend/main/hotspot_package/add.html', context=context)


def edit(request, id=None):
    context = {}
    if id is not None:
        package = get_object_or_404(HotspotPackage, id=id)
    else:
        package = None

    if request.method == 'POST':
        form = HotspotPackageAddForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            return redirect('hotspot_package_list')
    else:
        form = HotspotPackageAddForm(instance=package)
    context['data'] = package
    context['form'] = form
    return render(request, 'backend/main/hotspot_package/edit.html', context=context)


def assign_hotspot_package(request):
    return render(request, 'backend/main/hotspot_package/assign_package/index.html')


def assign_seller_list(request):
    if request.method == 'POST':
        if request.user.user_type == 'RS-5005':
            data = Seller.objects.filter(admin_id=request.user.id, user__user_status=1).annotate(
                package_count=Count('sellerhotspotpackage'))

        elif request.user.user_type == 'SA-2002':
            data = Seller.objects.filter(admin_id=request.user.id, user__user_status=1).annotate(
                package_count=Count('sellerhotspotpackage'))

        else:
            data = Seller.objects.filter(admin_id=request.user.id, user__user_status=1).annotate(
                package_count=Count('sellerhotspotpackage'))

        response_data, page_data = paginate_data(SellerHotspotPackage, data, request)

        count = 0
        for data in page_data:
            count = count + 1

            action_html = f'<a class="btn btn-info" href="/hotspot_package/assign/{data.id}" > Assign Packages</a>'

            response_data['data'].append({
                'count': count,
                'name': data.user.name,
                'package': data.package_count,
                'action': mark_safe(action_html),
            })
        return JsonResponse(response_data)


def assign_seller_hotspot_package(request, id):
    data = {'id': id}
    data['name'] = Seller.objects.get(id=id).user.name
    if request.method == 'POST':
        if request.user.user_type == 'RS-5005':
            data = SellerHotspotPackage.objects.filter(seller_id=id).all()
        elif request.user.user_type == 'SA-2002':
            data = SellerHotspotPackage.objects.filter(seller_id=id).all()
        else:
            data = SellerHotspotPackage.objects.filter(admin_id=request.user.id, seller_id=id).all()

        response_data, page_data = paginate_data(SellerHotspotPackage, data, request)

        count = 0
        for data in page_data:
            count = count + 1
            action_html = f'<a class="btn btn-info" href="/hotspot_package/assign_hotspot_package/edit/{data.id}" ><i class="fas fa-edit primary-icon"></i> Edit</a>'
            response_data['data'].append({
                'count': count,
                'package': data.package.name,
                'price': data.price,
                'action': mark_safe(action_html)
            })
        return JsonResponse(response_data)
    return render(request, 'backend/main/hotspot_package/assign_package/seller_package.html', context=data)


def assign_new_hotspot_package(request, id):
    if request.method == 'POST':
        form = AssignHotspotPackageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/hotspot_package/assign/' + str(id))
    else:
        form = AssignHotspotPackageForm()

    seller = Seller.objects.get(id=id)

    if request.user.user_type == 'RS-5005':
        seller_id = Seller.objects.filter(user_id=request.user.id).first().id
        package_list = SellerHotspotPackage.objects.filter(seller_id=seller_id).values_list('package_id', flat=True)
        query = HotspotPackage.objects.filter(id__in=package_list, status=1).all()
    else:
        query = HotspotPackage.objects.filter(admin_id=request.user.id).all()

    context = {'package_list': CommonFunction.model_to_dict(model=None, query=query, key='id', value='name'), 'id': id,
               'seller': seller, 'form': form}
    return render(request, 'backend/main/hotspot_package/assign_package/assign_new.html', context=context)


def edit_assign_hotspot_package(request, id):
    seller_package = SellerHotspotPackage.objects.get(id=id)
    if request.method == 'POST':
        form = AssignHotspotPackageForm(request.POST, instance=seller_package)
        if form.is_valid():
            form.save()
            return redirect('/hotspot_package/assign/' + str(seller_package.seller.id))
    else:
        form = AssignHotspotPackageForm()

    seller = seller_package.seller
    if request.user.user_type == 'RS-5005':
        seller_id = Seller.objects.filter(user_id=request.user.id).first().id
        package_list = SellerHotspotPackage.objects.filter(seller_id=seller_id).values_list('package_id', flat=True)
        query = HotspotPackage.objects.filter(id__in=package_list, status=1).all()
    else:
        query = HotspotPackage.objects.filter(admin_id=request.user.id).all()
    context = {'package_list': CommonFunction.model_to_dict(model=None, query=query, key='id', value='name'), 'id': id,
               'seller': seller, 'form': form, 'data': seller_package}
    return render(request, 'backend/main/hotspot_package/assign_package/edit.html', context=context)


def seller_own_hotspot_package(request):
    reseller = Seller.objects.filter(user_id=request.user.id).first()
    id = reseller.id
    data = {'id': id}
    data['name'] = Seller.objects.get(id=id).user.name
    if request.method == 'POST':
        if request.user.user_type == 'RS-5005':
            data = SellerHotspotPackage.objects.filter(seller_id=id).all()
        elif request.user.user_type == 'SA-2002':
            data = SellerHotspotPackage.objects.filter(seller_id=id).all()
        else:
            data = SellerHotspotPackage.objects.filter(admin_id=request.user.id, seller_id=id).all()

        response_data, page_data = paginate_data(SellerHotspotPackage, data, request)

        count = 0

        for data in page_data:
            add_balance = f'<a class="btn btn-primary ml-2" onclick="add_customer_price({data.id})"> Edit Price </a>'

            count = count + 1
            response_data['data'].append({
                'count': count,
                'package': data.package.name,
                'price': data.price,
                'seller_price': data.customer_price,
                'action': mark_safe(add_balance)
            })
        return JsonResponse(response_data)
    return render(request, 'backend/main/hotspot_package/assign_package/seller_own_package.html', context=data)


def seller_own_package_edit_view(request):
    if request.method == 'POST':
        id = request.POST.get('assign_package_id')
        data = SellerHotspotPackage.objects.filter(pk=id).first()

        price = request.POST.get('price')
        if float(price) <= float(data.price):
            return JsonResponse({'error': 'Price cannot be less than or equal Seller Price'}, status=302)
        else:
            data.customer_price = float(price)
            data.save()
            return JsonResponse({'success': "Customer Price Updated Successfully......"}, status=201)


    else:
        id = request.GET.get('assign_package_id')
        data = SellerHotspotPackage.objects.filter(pk=id).first()
        context = {'data': data}
        return render(request, 'backend/main/hotspot_package/assign_package/seller_customer_price_update.html', context=context)
