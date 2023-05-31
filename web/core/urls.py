from django.urls import path
from .views import (
    CreateRequestView,
    reply,
    InboxView,
    message_detail,
    UserDashboardView,
    done_message_status,
    OutBoxView
)

app_name = 'core'

urlpatterns = [
    path('dashboard/', UserDashboardView.as_view(), name='dashboard'),
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('outbox/', OutBoxView.as_view(), name='outbox'),
    path('leave_request/', CreateRequestView.as_view(), name='leave_request'),
    path('reply/<int:id>/', reply, name='reply'),
    path('message_detail/<int:id>/', message_detail, name='message_detail'),
    path('done_message_status/<int:id>/', done_message_status, name='done_message_status')
]
