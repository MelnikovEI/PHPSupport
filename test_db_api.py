from PHPSupport_DB import setup

setup()

from db_api import is_subscription_active, is_contractor_verified, create_order

print(is_subscription_active('@TemWithFrog'))
print(is_contractor_verified('@kaser137'))
print(create_order('@TemWithFrog', "Это новое описание запроса", "Реквизиты для сайта admin, admin"))