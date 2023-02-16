from django.shortcuts import get_object_or_404

from PHP_support_admin.models import Order, Question, Contractor, Client


def is_subscription_active(tg_account: str):
    """
    :param tg_account: account of a client
    :return: None - client is not registered
    True - client's subscription is active
    False - client is registered, but subscription is not active
    """
    try:
        client = Client.objects.get(tg_account=tg_account)
    except Client.DoesNotExist:
        return None
    return client.is_subscription_active()


def is_contractor_verified(tg_account: str):
    """
    :param tg_account: tg account of contractor
    :return: None - contractor is not registered
    True - contractor's is verified and can take orders
    False - contractor is registered, but has no rights to take orders
    """
    try:
        contractor = Contractor.objects.get(tg_account=tg_account)
    except Contractor.DoesNotExist:
        return None
    return contractor.is_verified


def create_order(tg_account, request, access_info):
    """Если клиент не подписан или не зарегистрирован, вернет None"""
    if not(is_subscription_active(tg_account)):
        return
    client = get_object_or_404(Client, tg_account=tg_account)
    return Order.objects.create(client=client, request=request, access_info=access_info)
