import datetime
from django.db import models


class Client(models.Model):
    tg_account = models.CharField('telegram account for communication', max_length=200, unique=True)
    subscription_start_date = models.DateField(verbose_name='date of starting subscription', null=True, blank=True)
    subscription_end_date = models.DateField(verbose_name='date of ending subscription (inclusive)', null=True, blank=True)

    def __str__(self):
        return self.tg_account

    def is_subscription_active(self) -> bool:
        now = datetime.date.today()
        return self.subscription_start_date <= now <= self.subscription_end_date


class Contractor(models.Model):
    tg_account = models.CharField('telegram account for communication', max_length=200, unique=True)
    is_verified = models.BooleanField("permission to get orders is granted?", default=False)

    def __str__(self):
        return self.tg_account


class Question(models.Model):
    question = models.TextField('question about the task from contractor')
    answer = models.TextField('answer about the task from client', blank=True)

    def __str__(self):
        return self.question[:30]


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='client', related_name='order')
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, verbose_name='contractor', related_name='order', blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='question', related_name='order', blank=True)
    request = models.TextField('description of the request from client')
    access_info = models.CharField('web site access information', max_length=400)
    date_estimation = models.DateField(verbose_name='estimation date of completing job from contractor', null=True, blank=True)
    is_finished_by_contractor = models.BooleanField("is order finished from contractor's point of view", default=False)
    is_finished_by_client = models.BooleanField("is order finished from client's point of view", default=False)
    date_closed = models.DateField(verbose_name='date of closing the order by client', null=True, blank=True)
#========================================================
    client_chat_id = models.IntegerField()
    coder_chat_id = models.IntegerField()
    order_id = models.Index()
#=========================================================