from django.db.models.functions import Concat
from django.shortcuts import render, redirect
from apps.hotspot_card.models import HotspotCard
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.contrib import messages
from system.all_utils.card_code_generator import generate_random_code
from system.utils import CommonFunction
from apps.hotspot_package.models import HotspotPackage, SellerHotspotPackage
from apps.seller.models import Seller
from django.db import transaction
from apps.user.models import Users
from django.db.models import F, Value, CharField, ExpressionWrapper
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def index(request, *args, **kwargs):
    return render(request, 'backend/main/hotspot_card/index.html')


def data(request, *args, **kwargs):
    if request.method == 'GET':
        columns = [None, 'code', 'validity']

        reverse = False
        query = HotspotCard.objects.filter(admin_id=request.user.id).all().order_by('-status', '-id')
        search_value = request.GET.get('search[value]')
        if search_value:
            query = HotspotCard.objects.search_by_data(search_value).filter(admin_id=request.user.id).order_by('-status', '-id')

        if request.user.user_type == "SA-2002":
            query = HotspotCard.objects.all().order_by('-status', '-id')
            if search_value:
                query = HotspotCard.objects.search_by_data(search_value).order_by('-status', '-id')

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
            checkbox = f'<input type="checkbox" class="row-checkbox" data-id="{data.id}" />'
            if data.status == 1:
                status = '<button class="btn btn-primary">Available</button>'
            else:
                status = (f'<button class="btn btn-warning">Used</button></br> '
                          f'<button class="btn btn-warning mt-2">{data.customer.mobile if data.customer else 0}</button>')

            response_data['data'].append({
                'checkbox': mark_safe(checkbox),
                'count': count,
                'code': ' '.join(data.code[i:i + 4] for i in range(0, len(data.code), 4)),
                'validity': str(data.validity) + ' Day',
                'created_at': data.created_at.strftime('%d %B %Y at %H:%M:%S %p'),
                'status': mark_safe(status),

            })

        return JsonResponse(response_data)


@transaction.atomic()
def generate_card(request):
    if request.user.user_type == 'RS-5005':
        seller_id = Seller.objects.filter(user_id=request.user.id).first().id
        package_list = SellerHotspotPackage.objects.filter(seller_id=seller_id).annotate(
            concated_name=Concat(
                'package__name', Value(' - '), ExpressionWrapper(F('price'), output_field=CharField()), Value(' TK'),
                output_field=CharField()
            )
        ).annotate(
            h_package_id=F('package__id')
        )
        context = {'package_list': CommonFunction.model_to_dict(model=None, query=package_list, key='h_package_id',
                                                                value='concated_name')}

    else:
        query = HotspotPackage.objects.filter(admin_id=request.user.id).all()
        context = {'package_list': CommonFunction.model_to_dict(model=None, query=query, key='id', value='name')}

    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        package_id = request.POST.get('package_id')
        if request.user.user_type != 'GA-4004':
            package = SellerHotspotPackage.objects.filter(package_id=package_id).first()
            total_price = float(package.price) * float(quantity)
            if float(request.user.wallet_balance) < float(total_price):
                messages.error(request, 'Your wallet balance is very low. Please try again after add balance.')
                return render(request, 'backend/main/hotspot_card/generate_card.html', context)
            else:
                data_list = []
                if int(quantity) > 0:
                    for i in range(0, int(quantity)):
                        data_dict = {}
                        data_dict['validity'] = package.package.day
                        while True:
                            code = generate_random_code()
                            exist_code = HotspotCard.objects.filter(code=code)
                            if not exist_code:
                                break

                        data_dict['code'] = code
                        data_dict['status'] = 1
                        data_dict['admin_id'] = request.user.id
                        data_list.append(data_dict)

                    instances = [HotspotCard(**data) for data in data_list]
                    HotspotCard.objects.bulk_create(instances)
                    user = Users.objects.get(pk=request.user.id)
                    user.wallet_balance = float(request.user.wallet_balance) - float(total_price)
                    user.save()

                    messages.success(request, 'Card Generated Successfully.')
                    return redirect('hotspot_card_list')

        else:
            package = HotspotPackage.objects.get(id=package_id)
            if package:
                data_list = []
                if int(quantity) > 0:
                    for i in range(0, int(quantity)):
                        data_dict = {}
                        data_dict['validity'] = package.day
                        while True:
                            code = generate_random_code()
                            exist_code = HotspotCard.objects.filter(code=code)
                            if not exist_code:
                                break

                        data_dict['code'] = code
                        data_dict['status'] = 1
                        data_dict['admin_id'] = request.user.id
                        data_list.append(data_dict)

                    instances = [HotspotCard(**data) for data in data_list]
                    HotspotCard.objects.bulk_create(instances)
                    messages.success(request, 'Card Generated Successfully.')
                    return redirect('hotspot_card_list')

    else:

        return render(request, 'backend/main/hotspot_card/generate_card.html', context=context)




def generate_pdf(request):
    # Your logic to generate or fetch HTML content goes here
    context = {'data': 'Hello, this is a test PDF!'}

    # Render the HTML content using a Django template
    template = get_template('backend/main/hotspot_card/report/card_print.html')
    html_content = template.render(context)

    # Create a file-like buffer to receive PDF data
    pdf_file = HttpResponse(content_type='application/pdf')
    pdf_file['Content-Disposition'] = 'inline; filename="output.pdf"'

    # Use pisa to generate the PDF
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

    if pisa_status.err:
        return HttpResponse('Error during PDF generation: {}'.format(pisa_status.err))

    return pdf_file