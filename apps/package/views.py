import json

from django.db.models import Sum, Count
from django.shortcuts import render, redirect, get_object_or_404

from apps.package.forms import PackageAddForm, AssignPackageForm
from apps.package.models import Package, SellerPackage
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe
from django.http import JsonResponse

from apps.router.models import Router
from apps.seller.models import Seller
from system.router.main import Microtik
from system.utils import CommonFunction, paginate_data


# Create your views here.

def index(request, *args, **kwargs):
    return render(request, 'backend/main/package/index.html')


def data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'profile', 'router']

    reverse = False
    query = Package.objects.filter(admin_id=request.user.id, status=1).all()
    search_value = request.GET.get('search[value]')
    if search_value:
        query = Package.objects.search_by_data(search_value).filter(admin_id=request.user.id, status=1)

    if request.user.user_type == "RS-5005":
        package_list = SellerPackage.objects.filter(seller_id=request.user.id).values_list('package_id', flat=True)
        query = Package.objects.filter(id__in=package_list, status=1).all()
        if search_value:
            query = Package.objects.search_by_data(search_value).filter(id__in=package_list, status=1)


    if request.user.user_type == "SA-2002":
        query = Package.objects.all()
        if search_value:
            query = Package.objects.search_by_data(search_value)

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
        'recordsTotal': Package.objects.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }

    count = 0
    for data in page_data:
        count = count + 1

        action_html = f'<a href="/package/edit/{data.id}" class="" > <i class="fas fa-edit primary-icon"></i> </a>'
        if data.status == 1:
            status = mark_safe('<button class="btn btn-success">Active</button>')
        else:
            status = mark_safe('<button class="btn btn-danger">Inactive</button>')

        response_data['data'].append({
            'count': count,
            'id': data.id,
            'name': data.name,
            'router': data.router.name if data.router else '',
            'profile': data.profile,
            'status': status,
            'action': mark_safe(action_html),

        })
    # f'<a href="/user/edit/{data.id}" class="btn btn-xs btn-primary"><i class="fa fa-edit"></i> Edit</a>'

    return JsonResponse(response_data)


def add(request):
    context = {}

    if request.method == 'POST':
        form = PackageAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/package')
    else:
        form = PackageAddForm()
    context['form'] = form
    query = Router.objects.filter(admin_id=request.user.id)
    context['router_data'] = CommonFunction.model_to_dict(model=Router, query=query, key='id', value='name')
    return render(request, 'backend/main/package/add.html', context=context)


def edit(request, id=None):
    context = {}
    if id is not None:
        package = get_object_or_404(Package, id=id)
    else:
        package = None

    if request.method == 'POST':
        form = PackageAddForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            return redirect('package_list')
    else:
        form = PackageAddForm(instance=package)
    context['data'] = package
    context['form'] = form
    query = Router.objects.filter(admin_id=request.user.id)
    context['router_data'] = CommonFunction.model_to_dict(model=Router, query=query, key='id', value='name')

    return render(request, 'backend/main/package/edit.html', context=context)


# seller package list
def assign_package(request):

    return render(request, 'backend/main/package/assign_package/index.html')


# seller package data
def assign_seller_list(request):
    if request.method == 'POST':
        if not request.user.user_type == 'SA-2002':
            data = Seller.objects.filter(admin_id=request.user.id).annotate(package_count=Count('sellerpackage'))

        else:
            data = SellerPackage.objects.all()

        response_data, page_data = paginate_data(SellerPackage, data, request)

        count = 0
        for data in page_data:
            count = count + 1
            value = data.id
            action_html = f'<a class="btn btn-info" href="/package/assign/{value}" > Assign Packages</a>'

            if request.user.user_type == 'RS-5005':
                action_html = f'<a class="btn btn-info" href="/package/reseller_assign/{value}" > Assign Packages</a>'


            response_data['data'].append({
                'count': count,
                'name': data.user.name,
                'package': data.package_count,
                'action': mark_safe(action_html),
            })
        return JsonResponse(response_data)


def assign_seller_package(request, id):
    data = {'id': id}
    data['name'] = Seller.objects.get(id=id).user.name
    if request.method == 'POST':
        if request.user.user_type == 'RS-5005':
            data = SellerPackage.objects.filter(seller_id=id).all()
        elif not request.user.user_type == 'SA-2002':
            data = SellerPackage.objects.filter(admin_id=request.user.id, seller_id=id).all()
        else:
            data = SellerPackage.objects.filter(seller_id=id).all()

        response_data, page_data = paginate_data(SellerPackage, data, request)

        count = 0
        for data in page_data:
            count = count + 1
            action_html = f'<a class="btn btn-info" href="/package/assign_package/edit/{data.id}" ><i class="fas fa-edit primary-icon"></i> Edit</a>'
            response_data['data'].append({
                'count': count,
                'package': data.package.name,
                'price': data.price,
                'action': mark_safe(action_html)
            })
        return JsonResponse(response_data)
    return render(request, 'backend/main/package/assign_package/seller_package.html', context=data)

def assign_reseller_package(request, id):
    data = {'id': id}
    data['name'] = Seller.objects.get(id=id).user.name
    if request.method == 'POST':
        if request.user.user_type == 'RS-5005':
            data = SellerPackage.objects.filter(seller_id=id).all()
        elif not request.user.user_type == 'SA-2002':
            data = SellerPackage.objects.filter(admin_id=request.user.id, seller_id=id).all()
        else:
            data = SellerPackage.objects.filter(seller_id=id).all()

        response_data, page_data = paginate_data(SellerPackage, data, request)

        count = 0
        for data in page_data:
            count = count + 1
            action_html = f'<a class="btn btn-info" href="/package/assign_package/edit/{data.id}" ><i class="fas fa-edit primary-icon"></i> Edit</a>'
            response_data['data'].append({
                'count': count,
                'package': data.package.name,
                'price': data.price,
                'action': mark_safe(action_html)
            })
        return JsonResponse(response_data)
    return render(request, 'backend/main/package/assign_package/reseller_package.html', context=data)

def assign_new_package(request, id):
    if request.method == 'POST':
        form = AssignPackageForm(request.POST)
        if form.is_valid():
            form.save()
            if request.user.user_type == 'RS-5005':
                return redirect('/package/reseller_assign/' + str(id))

            return redirect('/package/assign/' + str(id))
    else:
        form = AssignPackageForm()

    seller = Seller.objects.get(id=id)

    if request.user.user_type == 'RS-5005':
        seller_id = Seller.objects.filter(user_id=request.user.id).first().id
        package_list = SellerPackage.objects.filter(seller_id=seller_id).values_list('package_id', flat=True)

        query = Package.objects.filter(id__in=package_list, status=1).all()
    else:
        query = Package.objects.filter(admin_id=request.user.id).all()

    context = {'package_list': CommonFunction.model_to_dict(model=None, query=query, key='id', value='name'), 'id': id,
               'seller': seller, 'form': form}
    return render(request, 'backend/main/package/assign_package/assign_new.html', context=context)



def edit_assign_package(request, id):
    seller_package = SellerPackage.objects.get(id=id)
    if request.method == 'POST':
        form = AssignPackageForm(request.POST, instance=seller_package)
        if form.is_valid():
            form.save()
            if request.user.user_type == 'RS-5005':
                return redirect('/package/reseller_assign/' + str(seller_package.seller.id))
            return redirect('/package/assign/' + str(seller_package.seller.id))
    else:
        form = AssignPackageForm()

    seller = seller_package.seller
    if request.user.user_type == 'RS-5005':
        seller_id = Seller.objects.filter(user_id=request.user.id).first().id
        package_list = SellerPackage.objects.filter(seller_id=seller_id).values_list('package_id', flat=True)
        query = Package.objects.filter(id__in=package_list, status=1).all()
    else:
        query = Package.objects.filter(admin_id=request.user.id).all()
    context = {'package_list': CommonFunction.model_to_dict(model=None, query=query, key='id', value='name'), 'id': id,
               'seller': seller, 'form': form, 'data':seller_package}
    return render(request, 'backend/main/package/assign_package/edit.html', context=context)


def seller_own_package_list(request):
    seller = Seller.objects.filter(user_id=request.user.id).first()
    return assign_seller_package(request, seller.id)

