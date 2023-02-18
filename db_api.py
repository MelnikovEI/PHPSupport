import datetime

from django.shortcuts import get_object_or_404
from PHP_support_admin.models import Order, Question, Contractor, Client, Rate


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
    """Если клиент не подписан или не зарегистрирован, вернет None.
    Возвращает id созданного заказа"""
    if not (is_subscription_active(tg_account)):
        return
    client = get_object_or_404(Client, tg_account=tg_account)
    order = Order.objects.create(client=client, request=request, access_info=access_info, client_chat_id=client_chat_id,
                                 contractor_chat_id=contractor_chat_id)
    return order.id


def get_active_orders(tg_account):
    """Возвращает только не закрытые клиентом заказы"""
    client = get_object_or_404(Client, tg_account=tg_account)
    return list(client.orders.filter(is_finished_by_client=False).values())  # здесь можно ограничить выдачу полей


def get_order_info(order_id: int):
    """Возвращает статус заказа: определен ли подрядчик, список сообщений к заказу"""
    order = get_object_or_404(Order, id=order_id)
    order_status = {
        'is_contractor_defined': bool(order.contractor),
        'message_history': list(order.question.all().values_list('question', flat=True))
    }
    return order_status


def add_message(order_id: int, message: str):
    """Добавить сообщение в переписку между клиентом и подрядчиком"""
    order = get_object_or_404(Order, id=order_id)
    question = Question.objects.create(question=message)
    order.question.add(question)


def get_order(order_id: int):
    order = get_object_or_404(Order, id=order_id)
    return order


def close_order_by_client(order_id):
    """Закрывает заказ, когда клиент его акцептует"""
    order = get_object_or_404(Order, id=order_id)
    order.is_finished_by_client = True
    order.date_closed = datetime.date.today()
    order.save()


def close_order_by_contractor(order_id):
    """Закрывает заказ, когда клиент его акцептует"""
    order = get_object_or_404(Order, id=order_id)
    order.is_finished_by_contractor = True
    order.save()


def get_order_rate():
    """Возвращает фиксированную ставку за заказ, последнюю, в которой были изменения"""
    return Rate.objects.latest("order_rate").order_rate


# =============================================================
# TBD

def get_summary(): # возвращает сумму ставку за месяц
    pass

def get_active_contracnor_orders(tg_account): # возвращает список открытых заказов по контракторуб типа get_active_orders
    pass
