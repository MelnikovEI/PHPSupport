from PHPSupport_DB import setup

setup()

from db_api import is_subscription_active, is_contractor_verified, create_order, get_active_orders, get_order_info

print(is_subscription_active('TemWithFrog'))
print(is_contractor_verified('kaser137'))
#print(create_order('TemWithFrog', "Это новое описание запроса", "Реквизиты для сайта admin, admin", 111, 222))
print(get_active_orders('TemWithFrog'))
print(get_order_info(12))
