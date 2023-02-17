from django.shortcuts import get_object_or_404
import PHPSupport_DB
from PHP_support_admin.models import Order, Question, Contractor, Client


def is_subscription_active(tg_account: str) -> bool:
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


def is_contractor_verified(tg_account: str) -> bool:
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


def create_order(tg_account, request, access_info, client_chat_id, contractor_chat_id):
    """Если клиент не подписан или не зарегистрирован, вернет None
    Возвращает идентификатор созданного заказа в формате tg_account_id заказа"""
    if not (is_subscription_active(tg_account)):
        return
    client = get_object_or_404(Client, tg_account=tg_account)
    order = Order.objects.create(client=client, request=request, access_info=access_info, client_chat_id=client_chat_id, contractor_chat_id=contractor_chat_id)
    return order.id


def get_active_orders(tg_account):
    """Возвращает только не закрытые клиентом заказы"""
    client = get_object_or_404(Client, tg_account=tg_account)
    return list(client.orders.filter(is_finished_by_client=False).values())  # здесь можно ограничить выдачу полей


def get_order_info(order_id: int):
    """Возвращает статус заказа: определен ли подрядчик, список сообщений к заказу"""
    order = get_object_or_404(Order, id=order_id)
    status = {
        'is_contractor_defined': bool(order.contractor),
        'message_history': list(order.question.all().values_list('question'))
    }
    return status
