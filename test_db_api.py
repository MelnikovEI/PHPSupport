from PHPSupport_DB import setup

setup()

from db_api import is_subscription_active, is_contractor_verified


print(is_subscription_active('@TemWithFrog'))
print(is_contractor_verified('@kaser137'))
