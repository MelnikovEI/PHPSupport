import datetime
import PHPSupport_DB
from django.shortcuts import get_object_or_404
from PHP_support_admin.models import Order, Question, Contractor, Client, Rate


def get_order(order_id: int):
    order = get_object_or_404(Order, id=order_id)
    return order


def add_message(order_id: int, message: str):
    """Добавить сообщение в переписку между клиентом и подрядчиком"""
    order = get_object_or_404(Order, id=order_id)
    question = Question.objects.create(question=message)
    order.question.add(question)


# client block ============================================================================================
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


def create_order(tg_account, request, access_info, client_chat_id, contractor_chat_id):
    """Если клиент не подписан или не зарегистрирован, вернет None.
    Возвращает id созданного заказа"""
    if not (is_subscription_active(tg_account)):
        return
    client = get_object_or_404(Client, tg_account=tg_account)
    order = Order.objects.create(client=client, request=request, access_info=access_info, client_chat_id=client_chat_id,
                                 contractor_chat_id=contractor_chat_id)
    return order.id


def get_active_client_orders(tg_account):
    """Возвращает только не закрытые клиентом заказы"""
    client = get_object_or_404(Client, tg_account=tg_account)
    return list(client.orders.filter(is_finished_by_client=False).values())
    # здесь можно ограничить выдачу полей, в зависимости от того, что нужно?


def get_order_info(order_id: int):
    """Возвращает статус заказа: определен ли подрядчик, список сообщений к заказу"""
    order = get_object_or_404(Order, id=order_id)
    order_status = {
        'is_contractor_defined': bool(order.contractor),
        'message_history': list(order.question.all().values_list('question', flat=True))
    }
    return order_status


def close_order_by_client(order_id):
    """Закрывает заказ, когда клиент его акцептует"""
    order = get_object_or_404(Order, id=order_id)
    order.is_finished_by_client = True
    order.date_closed = datetime.date.today()
    order.save()


# contractor block ============================================================================================
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


def close_order_by_contractor(order_id):
    """Закрывает заказ, когда клиент его акцептует"""
    order = get_object_or_404(Order, id=order_id)
    order.is_finished_by_contractor = True
    order.save()


def get_order_rate():
    """Возвращает фиксированную ставку за заказ, последнюю, в которой были изменения"""
    return Rate.objects.latest("order_rate").order_rate


def get_current_month_closed_orders(tg_account):
    """Возвращает кол-во принятых клиентом заказов за текущий месяц"""
    contractor = get_object_or_404(Contractor, tg_account=tg_account)
    today = datetime.date.today()
    the_first_day_in_cur_month = datetime.date(today.year, today.month, 1)
    finished_orders_quantity = contractor.orders.filter(is_finished_by_client=True,
                                                        date_closed__gte=the_first_day_in_cur_month,
                                                        date_closed__lte=today,
                                                        ).count()
    return finished_orders_quantity


def get_current_month_salary(tg_account):
    """Возвращает заработанную подрядчиком сумму за текущий месяц"""
    return get_order_rate() * get_current_month_closed_orders(tg_account)


def get_active_contractor_orders(tg_account):
    """возвращает список открытых заказов по контрактору типа get_active_orders"""
    contractor = get_object_or_404(Contractor, tg_account=tg_account)
    return list(contractor.orders.filter(is_finished_by_client=False).values())
    # здесь можно ограничить выдачу полей, в зависимости от того, что нужно?


# =============================================================
# TBD

def take_order(tg_account, order_id):
    pass


def get_avaliable_orders():
    """возвращает список доступных заказов (новых заказов над которыми еще не началась работа"""
    return []