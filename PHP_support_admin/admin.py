import datetime

from django.contrib import admin
from PHP_support_admin.models import Order, Question, Contractor, Client, Rate
import db_api

admin.site.register(Order)
admin.site.register(Question)
# admin.site.register(Contractor)
admin.site.register(Client)
admin.site.register(Rate)


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    # search_fields = ['town', 'address']
    # readonly_fields = ['created_at']
    list_display = ['tg_account', 'current_month_finished_orders_count', 'current_month_salary']
    # list_editable = ['new_building']
    # list_filter = ['new_building', 'rooms_number', 'has_balcony']
    # raw_id_fields = ('liked_by',)
    # inlines = [        ContractorOrderInline,    ]

    def current_month_finished_orders_count(self, obj):
        today = datetime.date.today()
        the_first_day_in_cur_month = datetime.date(today.year, today.month, 1)
        finished_orders_quantity = obj.orders.filter(is_finished_by_client=True,
                                                     date_closed__gte=the_first_day_in_cur_month,
                                                     date_closed__lte=today,
                                                     ).count()
        return finished_orders_quantity

    def current_month_salary(self, obj):
        return db_api.get_order_rate() * self.current_month_finished_orders_count(obj)
