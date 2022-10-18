from django.urls import path
from .views import (
    leave_request_view,
    send,
    reply,
    inbox,
    message_detail,
    dashboard,
    done_message_status,
    outbox
)

app_name = 'core'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('inbox/', inbox, name='inbox'),
    path('outbox/', outbox, name='outbox'),
    path('leave_request/', leave_request_view, name='leave_request'),
    path('send/', send, name='send'),
    path('reply/<int:id>/', reply, name='reply'),
    path('message_detail/<int:id>/', message_detail, name='message_detail'),
    path('done_message_status/<int:id>/', done_message_status, name='done_message_status')
]
