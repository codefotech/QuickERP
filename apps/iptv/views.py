from django.shortcuts import render, redirect, get_object_or_404

from apps.iptv.forms import IptvAddForm
from apps.iptv.models import Iptv
from apps.router.models import Router
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe
from apps.router.forms import RouterAddForm
from django.http import JsonResponse
from PIL import Image
import base64
import os
from io import BytesIO
from datetime import datetime, timedelta, timezone, date
import uuid


def index(request, *args, **kwargs):
    return render(request, 'backend/main/iptv/index.html')


def data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'url', 'api_port', 'order']

    reverse = False
    query = Iptv.objects.all()
    search_value = request.GET.get('search[value]')

    if search_value:
        query = Iptv.objects.search_by_data(search_value)

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
        'recordsTotal': Router.objects.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }

    count = 0
    for data in page_data:
        count = count + 1

        action_html = f'<a href="/iptv/edit/{data.id}" class="" > <i class="fas fa-edit primary-icon"></i> </a>'
        img = f"<img src='/media/" + data.image + "'>"
        response_data['data'].append({
            'count': count,
            'id': data.id,
            'name': data.name,
            'image': img,
            'status': data.status,
            'action': mark_safe(action_html),

        })
    # f'<a href="/user/edit/{data.id}" class="btn btn-xs btn-primary"><i class="fa fa-edit"></i> Edit</a>'

    return JsonResponse(response_data)


def add(request):
    context = {}

    if request.method == 'POST':
        form = IptvAddForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            if form.data.get('image_base64'):
                year_month = f"{date.today().year}/{date.today().month}/"
                path = 'iptv/image/' + year_month
                os.makedirs(os.path.join('media', path), exist_ok=True)
                image_data = form.data.get('image_base64').split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
                image = image.resize((400, 225))
                datetime_str = datetime.now().strftime('%Y%M%d%H%M%S')
                user_picture_name = f"image-{datetime_str}-{uuid.uuid4()}.jpeg"
                picture_path = os.path.join(path, user_picture_name)
                with open('media/' + picture_path, 'wb') as f:
                    image.save(f, 'jpeg')
                form.instance.image = str(picture_path)
            form.save()
            return redirect('/iptv')
    else:
        form = IptvAddForm()
    context['form'] = form
    return render(request, 'backend/main/iptv/add.html', context=context)


def edit(request, id=None):
    context = {}
    iptv = Iptv.objects.get(id=id)
    # if id is not None:
    #     iptv = get_object_or_404(Iptv, id=id)
    context['data'] = iptv
    # else:
    #     iptv = None
    if request.method == 'POST':
        form = IptvAddForm(request.POST)
        if form.is_valid():
            form = IptvAddForm(request.POST, instance=iptv)
            form.save(commit=False)
            if form.data.get('image_base64'):
                year_month = f"{date.today().year}/{date.today().month}/"
                path = 'iptv/image/' + year_month
                os.makedirs(os.path.join('media', path), exist_ok=True)
                image_data = form.data.get('image_base64').split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
                image = image.resize((400, 225))
                datetime_str = datetime.now().strftime('%Y%M%d%H%M%S')
                user_picture_name = f"image-{datetime_str}-{uuid.uuid4()}.jpeg"
                picture_path = os.path.join(path, user_picture_name)
                with open('media/' + picture_path, 'wb') as f:
                    image.save(f, 'jpeg')
                form.instance.image = str(picture_path)
            form.save()
            return redirect('/iptv')
        else:
            form = IptvAddForm()

        context['form'] = form
    return render(request, 'backend/main/iptv/edit.html', context=context)
