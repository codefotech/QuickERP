from system.enums import CustomEnum

import enum


class PaymentMethodEnumClass(CustomEnum):
    pass


class PaymentTypeEnumClass(CustomEnum):
    pass


class ExpenseTypeEnumClass(CustomEnum):
    pass


PaymentMethodEnum = PaymentMethodEnumClass(cash=1, bkash=2, sslcommerz=3)
PaymentTypeEnum = PaymentTypeEnumClass(wallet_payment=1, add_balance=2, seller_package_payment=3)
ExpenseTypeEnum = ExpenseTypeEnumClass(add_balance=1, pay_pppoe_bill=2, staff_manager_bill=3)
