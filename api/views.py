from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q

from telegram import Bot

bot = Bot(
    token="1383879665:AAEemz4FwuG_MauuwXQGWx3i_PT863TKl0I"
)

front_end_url = 'http://wiki.ecoferma56.ru'


def send_message(title, desc, username):
    channel_layer = get_channel_layer()
    message = {"title": title, "desc": desc}
    async_to_sync(channel_layer.group_send)("liveData", {
        "type": 'refresh_data',
        'message': message,
        'to_user': username,
    })

# class MenuViewSet(viewsets.ModelViewSet):
#     queryset = Menu.objects.none()
#     serializer_class = MenuSerializer
#
#     def get_queryset(self):
#         if self.request.method == 'DELETE':
#             return Menu.objects.all()
#         if self.request.method == 'PATCH':
#             return Menu.objects.all()
#         return Menu.objects.filter(top_menu=None)
#
#     def create(self, request, *args, **kwargs):
#         if request.user.can_edit_data:
#             menu = Menu.objects.create(name=request.data.get("name"),
#                                        top_menu_id=request.data.get("top_menu", None))
#             order = len(Menu.objects.all())
#             menu.order = order + 1
#             menu.save()
#             return Response(data="Меню успешно создано.")
#
#     def update(self, request, *args, **kwargs):
#         if request.user.can_edit_data:
#             menu = self.get_object()
#             print(request.data)
#             if 'top_menu' in request.data:
#                 if request.data.get("top_menu") == 'blank':
#                     menu.top_menu_id = None
#                 elif request.data.get("top_menu") is not None:
#                     menu.top_menu_id = request.data.get("top_menu", None)
#             if 'name' in request.data:
#                 menu.name = request.data.get('name', menu.name)
#             if 'order' in request.data:
#                 top_menu = Menu.objects.filter(Q(top_menu=menu.top_menu) & ~Q(name=menu.name))
#                 i = 0
#                 menu.order = request.data.get('order')
#                 for ord in top_menu:
#                     i += 1
#                     if ord.order == request.data.get('order'):
#                         if request.data.get('order') == 0:
#                             i += 1
#                             ord.order = i
#                         else:
#                             ord.order = i
#                             i += 2
#                         ord.save()
#                     else:
#                         ord.order = i
#                         ord.save()
#             # if 'permissions' in request.data:
#             #     menu.permissions.clear()
#             #     menu.permissions.set(request.data.get('permissions', None))
#             # for perm in request.data.get('permissions'):
#             #     print(PositionInGroup.objects.get(id=perm))
#             #     menu.permissions.add(PositionInGroup.objects.get(id=perm))
#             menu.save()
#             return Response(data="Меню успешно обновлено.")
#
#
# class AccountShortViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Account.objects.all()
#     serializer_class = AccountShortSerializer
