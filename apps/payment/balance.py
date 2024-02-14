from django.db import transaction
from django.shortcuts import redirect

from apps.payment.models import WalletHistory
from apps.seller.models import Seller
from django.contrib import messages


@transaction.atomic
def final_add_balance(request, payment_data, payment_details):
    with transaction.atomic():
        user = request.user
        user.wallet_balance = round(float(user.wallet_balance), 2) + round(float(payment_data['amount']), 2)
        user.save()

        WalletHistory.objects.create(user_id=user.id,
                                     admin_id=Seller.objects.filter(
                                         user_id=user.id).first().admin_id if Seller.objects.filter(
                                         user_id=user.id).first() else user.id,
                                     amount=payment_data['amount'],
                                     payment_method=payment_data['payment_method'],
                                     payment_type=request.session.get('payment_type'),
                                     payment_details=payment_details,
                                     approved=1
                                     )

        request.session.pop('payment_data', None)
        request.session.pop('payment_type', None)
        messages.success(request, 'Payment completed')

        return redirect('dashboard')
