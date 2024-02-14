import ipaddress
from django.http import HttpResponse
from django.utils.module_loading import import_string
from passlib.hash import sha256_crypt
import random
import ipaddress
from datetime import datetime, timedelta
from django.apps import apps
from django.urls import get_resolver
import hashlib

from apps.user.models import UserTypes
from system.config import _thread_local
from django.urls import reverse
from django.core.paginator import Paginator

# from captcha.client import submit
# from django.conf import settings
# from django.contrib import messages
# from django.http import JsonResponse
# from django.utils import timezone
#
# from apps.company_association.models import CompanyAssociationMaster
# from apps.globals.models import LogoInformation
# from apps.user.models import FailedLoginHistory
# from apps.globals.models import EmailTemplates
# from apps.user.validate import login_validator
# from django.shortcuts import redirect
# from django.template.loader import render_to_string
# from system.notification_web_service import NotificationWebService
# from apps.globals.models import Configuration, EmailQueue
# from system.config import _thread_local
# from apps.company_profile.models import CompanyInfo
# from django.db import connection
# from collections import namedtuple
# from system.config import GlobalConfig
# from django.utils.crypto import get_random_string
# from apps.user.models import UserLogs
# from django.core import serializers
# import re
#
#
# class SecurityChecker:
#     def __init__(self, request):
#         self.request = request
#
#     def captcha_checker(self):
#         hit = self.request.session.get('hit')
#         if hit and hit >= 3:
#             response = submit(
#                 self.request.POST.get('g_recaptcha_response'),
#                 private_key=settings.RECAPTCHA_PRIVATE_KEY,
#                 remoteip=self.request.META.get('REMOTE_ADDR')
#             )
#             if response.is_valid:
#                 data = {
#                     'email': self.request.POST.get('email'),
#                     'password': self.request.POST.get('password')
#                 }
#                 try:
#                     login_validator(data)
#                 except ValueError as e:
#                     error_msg = str(e)
#                     return JsonResponse({
#                         'success': False,
#                         'msg': error_msg,
#                         'hit': hit
#                     }, status=200)
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'msg': 'Please check the captcha.',
#                     'hit': hit
#                 }, status=200)
#
#     def check_attack(self, request=None):
#         if request:
#             self.request = request
#         try:
#             user_ip_address = self.get_visitor_real_ip(request=request)
#             count = FailedLoginHistory.objects.filter(
#                 remote_address=user_ip_address,
#                 is_archive=0,
#                 created_at__gte=timezone.now() - timedelta(minutes=20)
#             ).count()
#             if count > 20:
#                 messages.error(request,
#                                'Invalid Login session. Please try after 10 to 20 minute [LC6091], Please contact with '
#                                'system admin.')
#                 return False
#             else:
#                 count = FailedLoginHistory.objects.filter(
#                     remote_address=user_ip_address,
#                     is_archive=0,
#                     created_at__gte=timezone.now() - timedelta(minutes=60)
#                 ).count()
#                 if count > 40:
#                     messages.error(request,
#                                    'Invalid Login session. Please try after 30 to 60 minute [LC6092], Please contact '
#                                    'with system admin.')
#                     return False
#                 else:
#                     count = FailedLoginHistory.objects.filter(
#                         remote_address=user_ip_address,
#                         is_archive=0,
#                         created_at__gte=timezone.now() - timedelta(minutes=10)
#                     ).count()
#                     if count > 6:
#                         messages.error(request,
#                                        'Invalid Login session. Please try after 5 to 10 minute 1002,Please contact '
#                                        'with system admin.')
#                         return False
#         except Exception as e:
#             print(e)
#             messages.warning(request,
#                              "Login session exception. Please try after 5 to 10 minute 1003, Please contact with "
#                              "system admin. ")
#             return False
#         return True
#
#     @staticmethod
#     def get_visitor_real_ip(request):
#
#         client = None
#         forward = None
#         remote = None
#         if request.META.get('HTTP_CF_CONNECTING_IP'):
#             request.META['REMOTE_ADDR'] = request.get('HTTP_CF_CONNECTING_IP')
#             request.META['HTTP_CLIENT_IP'] = request.get('HTTP_CF_CONNECTING_IP')
#             request.META['HTTP_X_FORWARDED_FOR'] = request.get('HTTP_CF_CONNECTING_IP')
#         else:
#             client = request.META.get('HTTP_CLIENT_IP')
#             forward = request.META.get('HTTP_X_FORWARDED_FOR')
#             remote = request.META.get('REMOTE_ADDR')
#
#         if client:
#             ipaddress.ip_address(client)
#             valid_ip = client
#         elif forward:
#             ipaddress.ip_address(forward)
#             valid_ip = forward
#         else:
#             valid_ip = remote
#         return valid_ip
#
#     def failed_login(self, email):
#         ip_address = self.get_visitor_real_ip(request=self.request)
#         failed_log_in = FailedLoginHistory()
#         failed_log_in.remote_address = ip_address
#         failed_log_in.user_email = email
#         failed_log_in.save()
#
#
# class CommonFunction:
#
#     @staticmethod
#     def get_user_all_company_ids_with_zero(user=None):
#         if user:
#             company_ids = CompanyAssociationMaster.objects.values('id').filter(
#                 is_active=1,
#                 status=25,
#                 is_archive=0,
#                 request_from_user_id=user.id
#             )
#             return company_ids
#
#         else:
#             return False
#
#     @staticmethod
#     def global_setting(request=None):
#         logo_info = LogoInformation.objects.values(
#             'logo',
#             'title',
#             'manage_by',
#             'help_link'
#         ).order_by('-id').first()
#
#         return logo_info
#
#     @staticmethod
#     def cc_email():
#         return Configuration.objects.get(caption='CC_EMAIL').value
#
#     @staticmethod
#     def send_email_sms(request, caption=None, app_info=None, receiver_info=None):
#         config = GlobalConfig()
#         tracking_number = '{$trackingNumber}'
#         code_string = '{$code}'
#         server_name = '{$serviceName}'
#         try:
#             template = EmailTemplates.objects.filter(caption=caption).first()
#
#             if caption not in ['TWO_STEP_VERIFICATION', 'ACCOUNT_ACTIVATION', 'CONFIRM_ACCOUNT', 'APPROVE_USER',
#                                'REJECT_USER', 'PASSWORD_RESET_REQUEST', 'APP_APPROVE_PIN_NUMBER',
#                                'USER_VERIFICATION_EMAIL', 'NEW_PASSWORD', 'PASSWORD_RESET_REQUEST',
#                                'ONE_TIME_PASSWORD']:
#
#                 template.email_content = template.email_content.replace(tracking_number,
#                                                                         app_info.get('tracking_no'))
#                 template.email_content = template.email_content.replace(server_name,
#                                                                         app_info.get('process_type_name'))
#                 template.email_content = template.email_content.replace('{$remarks}', app_info.get('remarks'))
#                 template.sms_content = template.sms_content.replace(server_name, app_info.get('process_type_name'))
#                 template.sms_content = template.sms_content.replace(tracking_number, app_info.get('tracking_no'))
#             elif caption == 'CONFIRM_ACCOUNT':
#                 template.email_content = template.email_content.replace('{$verificationLink}',
#                                                                         app_info.get('verification_link'))
#
#             elif caption == 'ONE_TIME_PASSWORD':
#                 template.email_content = template.email_content.replace(code_string, app_info.get('one_time_password'))
#             elif caption == 'TWO_STEP_VERIFICATION':
#                 template.email_content = template.email_content.replace(code_string, app_info.get('code'))
#                 template.sms_content = template.sms_content.replace(code_string, app_info.get('code'))
#
#                 if app_info.get('verification_type') == 'mobile_no':
#                     template.email_active_status = 0
#                     template.sms_active_status = 1
#                 else:
#                     template.email_active_status = 1
#                     template.sms_active_status = 0
#             elif caption == 'REJECT_USER':
#                 template.email_content = template.email_content.replace('{$rejectReason}',
#                                                                         app_info.get('reject_reason'))
#             elif caption == 'PASSWORD_RESET_REQUEST':
#                 template.email_content = template.email_content.replace('{$reset_password_link}',
#                                                                         app_info.get('reset_password_link'))
#
#             if caption == 'APP_APPROVE_PIN_NUMBER':
#                 template.email_content = template.email_content.replace('{$pinNumber}', app_info.get('code'))
#                 template.sms_content = template.sms_content.replace('{$pinNumber}', app_info.get('code'))
#             elif caption == 'APP_APPROVE':
#                 template.email_content = template.email_content.replace(tracking_number,
#                                                                         app_info.get('tracking_no'))
#                 template.email_content = template.email_content.replace(server_name,
#                                                                         app_info.get('process_type_name'))
#                 template.sms_content = template.sms_content.replace(tracking_number, app_info.get('tracking_no'))
#                 template.sms_content = template.sms_content.replace(server_name, app_info.get('process_type_name'))
#
#             email_content = render_to_string(template_name='email_template/message.html', context={'header': template.
#                                              email_subject, 'param': template.email_content}, request=request)
#             cc_email_from_configuration = CommonFunction().cc_email()
#             notification_web_service = NotificationWebService()
#
#             if template.email_active_status == 1 or template.sms_active_status == 1:
#                 email_queue_data = []
#
#                 for receiver in receiver_info:
#                     email_queue = {
#                         'process_type_id': app_info.get('process_type_id', 0),
#                         'app_id': app_info.get('app_id', 0),
#                         'status_id': app_info.get('status_id', 0),
#                         'caption': template.caption,
#                         'email_content': email_content
#                     }
#
#                     if template.email_active_status == 1:
#                         email_queue['email_to'] = receiver.get('user_email')
#                         email_queue[
#                             'email_cc'] = template.email_cc if template.email_cc else cc_email_from_configuration
#                     email_queue['email_subject'] = template.email_subject
#                     if receiver.get('user_mobile') and receiver.get(
#                             'user_mobile').strip() and template.sms_active_status == 1:
#                         email_queue['sms_content'] = template.sms_content
#                         email_queue['sms_to'] = receiver.get('user_mobile')
#
#                         # Instant SMS Sending
#                         sms_sending_response = notification_web_service.send_sms(receiver.get('user_mobile'),
#                                                                                  template.sms_content)
#                         email_queue['sms_response'] = sms_sending_response.get('msg', '')
#                         if sms_sending_response.get('status', 0) == 1:
#                             email_queue['sms_status'] = 1
#                             email_queue['sms_response_id'] = sms_sending_response.get('message_id', None)
#                         email_queue['sms_no_of_try'] = 1
#                         # End of Instant SMS Sending
#
#                     email_queue['attachment'] = app_info.get('attachment', '')
#                     email_queue['attachment_certificate_name'] = app_info.get('attachment_certificate_name', '')
#                     email_queue['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                     email_queue['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#                     # Instant Email sending
#                     if not email_queue['attachment_certificate_name'] and template.email_active_status == 1:
#                         email_sending_response = notification_web_service.send_email(
#                             {'header_text': config.project_name,
#                              'recipient': receiver.get('user_email'),
#                              'subject': template.email_subject,
#                              'bodyText': '',
#                              'bodyHtml': email_content,
#                              'email_cc': email_queue.get('email_cc')
#                              }
#                         )
#                         email_queue['email_no_of_try'] = 1
#                         email_queue['email_response'] = email_sending_response.get('msg', '')
#                         if email_sending_response.get('status', 0) == 1:
#                             email_queue['email_status'] = 1
#                             email_queue['email_response_id'] = email_sending_response.get('message_id', None)
#
#                     email_queue['web_notification'] = 0
#
#                     # End of Instant Email sending
#                     email_queue_data.append(email_queue)
#
#                 EmailQueue.objects.bulk_create([EmailQueue(**data) for data in email_queue_data])
#
#                 last_id = EmailQueue.objects.last().id
#                 return last_id
#             return True
#         except Exception as e:
#             messages.error(request, str(e) + '[Utils-1005]')
#             return redirect('sign_up')
#
#     @staticmethod
#     def check_eligibility():
#         company_id = _thread_local.user.working_company_id
#         data = 0
#         if company_id:
#             data = CompanyInfo.objects.filter(id=company_id, company_status=1).count()
#         if data > 0:
#             return 1
#         else:
#             return 0
#
#     @staticmethod
#     def model_to_dict(model=None, key=None, value=None, query=None, order_by=None):
#         # Here this process will return a key value dict , where we have used value_list() against all() and
#         # data prepare with static index because when we want to get specific data by retrieve model then
#         # value_list() is more efficient than all()
#
#         if query:
#             data = {getattr(data, key): getattr(data, value) for data in query}
#             return data
#
#         elif model:
#             if key and value:
#                 blank_keyword = {value: ''}
#                 none_keyword = {value: None}
#                 query = model.objects.exclude(**blank_keyword).exclude(**none_keyword).values_list(key, value)
#                 if order_by:
#                     query = query.order_by(order_by)
#                 data = {data[0]: data[1] for data in query}
#                 return data
#                 """Here this process will return a key value dict , where we have used value_list() against all() and
#                 data prepare with static index because when we want to get specific data by retrieve model then
#                 value_list() is more efficient than all() """
#
#     @staticmethod
#     def get_notice(flag=0):
#         if flag == 1:
#             query = """
#                 SELECT date_format(updated_at,'%d %M, %Y') `Date`,heading,details,importance,id, case when importance='Top'
#                 then 1 else 0 end Priority FROM notice where status='public' or status='private'
#                 order by Priority desc, updated_at desc LIMIT 10
#             """
#             with connection.cursor() as cursor:
#                 cursor.execute(query)
#                 columns = [col[0] for col in cursor.description]
#                 Row = namedtuple('Row', columns)
#                 lists = [Row(*row) for row in cursor.fetchall()]
#         else:
#             query = """
#                 SELECT date_format(updated_at,'%d %M, %Y') `Date`,heading,details,importance,id, case when importance='Top'
#                 then 1 else 0 end Priority FROM notice where status='public' order by Priority desc, updated_at desc LIMIT 10
#             """
#             with connection.cursor() as cursor:
#                 cursor.execute(query)
#                 columns = [col[0] for col in cursor.description]
#                 Row = namedtuple('Row', columns)
#                 lists = [Row(*row) for row in cursor.fetchall()]
#         return lists
#
#     @staticmethod
#     def entry_access_log(request):
#         str_random = get_random_string(length=10)
#         user_id = request.user.id
#         login_dt = timezone.now()
#         updated_at = timezone.now()
#         ip_address = SecurityChecker.get_visitor_real_ip(request)
#         access_log_id = str_random
#         access_log = UserLogs(user_id=user_id, login_dt=login_dt, updated_at=updated_at, ip_address=ip_address,
#                               access_log_id=access_log_id)
#         access_log.save()
#         request.session['access_log_id'] = access_log_id
#
#     @staticmethod
#     def entry_access_logout(request):
#         access_log_id = request.session.get('access_log_id')
#         if access_log_id:
#             logout_dt = timezone.now()
#             updated_at = timezone.now()
#             access_log = UserLogs.objects.filter(access_log_id=access_log_id).first()
#             access_log.logout_dt = logout_dt
#             access_log.updated_at = updated_at
#             access_log.save()
#
#
# def convert_date_string_to_django_date(date_string):
#     date_formats = ['%d-%b-%Y', '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b %d, %Y', '%b %d %Y', '%B %d, %Y', '%B %d %Y']
#     for date_format in date_formats:
#         try:
#             date = datetime.strptime(date_string, date_format)
#             return date.strftime('%Y-%m-%d')
#             # Convert the date to Django model format and return it as a string
#         except ValueError:
#             pass
#
#
# def convert_time_string_to_django_time(time_string):
#     time_formats = ['%I:%M %p', '%H:%M:%S', '%I:%M:%S %p', '%H:%M']
#     for time_format in time_formats:
#         try:
#             time = datetime.strptime(time_string, time_format)
#             return time.strftime('%H:%M:%S')
#             # Convert the time to Django model format and return it as a string
#         except ValueError:
#             pass
#
#
# def model_to_json(model_instance):
#     json_data = serializers.serialize('json', [model_instance])
#     return json_data
#
#
# def queryset_to_json(queryset):
#     json_data = serializers.serialize('json', list(queryset))
#     return json_data
#
#
# def remove_special_characters(text):
#     pattern = r"[^\w\s]"
#     cleaned_text = re.sub(pattern, "", text)
#     return cleaned_text
#
# def search_value_in_list(value, value_list):
#     search_value = f"{value}"
#     for i in value_list:
#         if re.search(search_value, i):
#             return True
#     return False

import random
import string

from main import settings
import json
import os


def generate_salt_with_text(text):
    # Generate a random string to use as a custom salt
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    # Combine the salt and the provided text
    salted_text = salt

    return salted_text


def hash_password(password):
    hashed_password = sha256_crypt.hash(password, salt=generate_salt_with_text('erp123bd23seam'))
    return hashed_password


def verify_password(password, stored_hash):
    return sha256_crypt.verify(password.encode('utf-8'), stored_hash)


class CommonFunction:
    @staticmethod
    def model_to_dict(model=None, key=None, value=None, query=None, order_by=None, relational_value=''):
        # Here this process will return a key value dict , where we have used value_list() against all() and
        # data prepare with static index because when we want to get specific data by retrieve model then
        # value_list() is more efficient than all()

        if query:
            data = {}
            for item in query:
                if relational_value:
                    data[getattr(item, key)] = getattr(getattr(item, value), relational_value)
                else:
                    data[getattr(item, key)] = getattr(item, value)

            return data

        elif model:
            if key and value:
                blank_keyword = {value: ''}
                none_keyword = {value: None}
                query = model.objects.exclude(**blank_keyword).exclude(**none_keyword).values_list(key, value)
                if order_by:
                    query = query.order_by(order_by)
                data = {data[0]: data[1] for data in query}
                return data
                """Here this process will return a key value dict , where we have used value_list() against all() and 
                data prepare with static index because when we want to get specific data by retrieve model then 
                value_list() is more efficient than all() """


def convert_date_string_to_django_date(date_string):
    date_formats = ['%d-%b-%Y', '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b %d, %Y', '%b %d %Y', '%B %d, %Y', '%B %d %Y']
    for date_format in date_formats:
        try:
            date = datetime.strptime(date_string, date_format)
            return date.strftime('%Y-%m-%d')
            # Convert the date to Django model format and return it as a string
        except ValueError:
            pass


def convert_time_string_to_django_time(time_string):
    time_formats = ['%I:%M %p', '%H:%M:%S', '%I:%M:%S %p', '%H:%M']
    for time_format in time_formats:
        try:
            time = datetime.strptime(time_string, time_format)
            return time.strftime('%H:%M:%S')
            # Convert the time to Django model format and return it as a string
        except ValueError:
            pass


def get_app_urls():
    apps_url_data = {}
    for app_name in settings.INSTALLED_APPS:
        url_names_list = []
        try:
            urls_module = f"{app_name}.urls"
            urls = import_string(urls_module)
            for url_pattern in urls.urlpatterns:
                if hasattr(url_pattern, 'name') and url_pattern.name:
                    url_names_list.append(url_pattern.name)

        except ImportError:
            pass

        if url_names_list:
            apps_url_data[app_name.replace('apps.', '')] = url_names_list

    return apps_url_data


def prepare_menu_item():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file_path = os.path.join(base_dir, 'system', 'menu', 'main.json')

    with open(json_file_path, 'r') as menu_file:
        menu_data = json.load(menu_file)

    updated_menu = []

    if hasattr(_thread_local.user, 'user_type'):
        user_type = _thread_local.user.user_type
    else:
        user_type = None

    if not user_type == 'SA-2002' and user_type is not None:
        permission = UserTypes.objects.filter(code=user_type).first().permission
        for value in menu_data['menuItems']:
            if value.get('parent') == True:
                updated_menu.append(value)
            else:
                if value.get('app') in list(permission):
                    if len(value.get('subMenu')) > 0:
                        new_dict = {}
                        loop_count = 1
                        for submenu in value.get('subMenu'):
                            if submenu.get('link') in permission.get(value.get('app')):
                                if loop_count == 1:
                                    new_dict = {
                                        "label": value.get('label'),
                                        "icon": value.get('icon'),
                                        "link": "#",
                                        "subMenu": []
                                    }
                                submenu['link'] = reverse(submenu['link'])
                                new_dict.get('subMenu').append(submenu)
                                loop_count += 1
                        if new_dict:
                            updated_menu.append(new_dict)
                    else:
                        try:
                            value['link'] = reverse(value['link'])
                            updated_menu.append(value)
                        except Exception as e:
                            pass

    else:
        for value in menu_data['menuItems']:
            if value.get('parent') == True:
                updated_menu.append(value)
            else:
                if len(value.get('subMenu')) > 0:
                    new_dict = {
                        "label": value.get('label'),
                        "icon": value.get('icon'),
                        "link": "#",
                        "subMenu": []
                    }
                    for submenu in value.get('subMenu'):
                        try:
                            submenu['link'] = reverse(submenu['link'])
                            new_dict.get('subMenu').append(submenu)
                        except Exception as e:
                            pass
                    updated_menu.append(new_dict)
                else:
                    value['link'] = reverse(value['link'])
                    updated_menu.append(value)
    return updated_menu


def paginate_data(model, data, request):
    search_value = request.GET.get('search[value]')

    if search_value:
        data = data.objects.search_by_data(search_value)

    order_column = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')

    if order_column:
        column_name = request.GET.get(f'columns[{order_column}][data]')
        reverse_data = False
        if order_dir == 'desc':
            reverse_data = True
        data = sorted(data, key=lambda p: getattr(p, column_name), reverse=reverse_data)
    if request.method == 'POST':
        start = request.POST.get('start')
        length = request.POST.get('length')
    else:
        start = request.GET.get('start')
        length = request.GET.get('length')

    if start and length:
        page = int(start) // int(length) + 1
    else:
        page = 0

    per_page = str(length if length else 25)
    paginator = Paginator(list(data), per_page)
    page_data = paginator.get_page(page)

    response_data = {
        'draw': request.GET.get('draw'),
        'recordsTotal': data.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }
    if request.method == 'POST':
        response_data['draw'] = request.POST.get('draw')
    return response_data, page_data


def paginate_data_with_raw_query(data, request):
    order_column = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')

    if order_column:
        column_name = request.GET.get(f'columns[{order_column}][data]')
        reverse_data = False
        if order_dir == 'desc':
            reverse_data = True
        data = sorted(data, key=lambda p: getattr(p, column_name), reverse=reverse_data)
    if request.method == 'POST':
        start = request.POST.get('start')
        length = request.POST.get('length')
    else:
        start = request.GET.get('start')
        length = request.GET.get('length')

    if start and length:
        page = int(start) // int(length) + 1
    else:
        page = 0

    per_page = str(length if length else 25)
    paginator = Paginator(list(data), per_page)
    page_data = paginator.get_page(page)

    response_data = {
        'draw': request.POST.get('draw') if request.method == 'POST' else request.GET.get('draw'),
        'recordsTotal': len(data),
        'recordsFiltered': paginator.count,
        'data': []
    }
    return response_data, page_data
