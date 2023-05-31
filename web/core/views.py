from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_control
from django.views.generic import ListView, TemplateView, CreateView, FormView
from .models import Employee, Message, Reply
from .forms import RequestLeaveForm


class UserDashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user.employee

        result = Reply.objects.filter(
            Q(message__receiver=user, message__is_reply=True) | Q(receiver=user, is_done=False),
        ).aggregate(
            nm=Count('message__id'),
            rm=Count('id')
        )

        context['number_message'] = result['nm'] + result['rm']

        return context


class InboxView(ListView):
    template_name = 'core/inbox.html'
    context_object_name = 'inbox'

    def get_queryset(self):
        user = self.request.user.employee

        new_msg = Message.objects.filter(receiver=user, is_reply=False)
        reply = Reply.objects.filter(message__sender=user, is_done=False)

        return {'reply': reply, 'new_msg': new_msg}


class OutBoxView(ListView):
    model = Reply
    template_name = 'core/outbox.html'
    context_object_name = 'outbox'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user.employee
        messages = queryset.select_related('message').filter(message__sender=user)
        return {'messages': messages}


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
def message_detail(request, id):
    msg = get_object_or_404(Message, id=id)
    if msg.is_reply:
        reply = Reply.objects.filter(message_id=msg.id).order_by('id')[0]
        return render(request, 'core/message_detail.html', {'reply': reply})
    else:
        form = CHOICES()
        return render(request, 'core/message_detail.html', {'msg': msg,
                                                            'form': form})


def done_message_status(request, id):
    if request.method == "POST":
        msg = Reply.objects.get(id=id)
        msg.message.is_done = True
        msg.is_done = True
        msg.save()
        return redirect('core:inbox')
    else:
        return redirect('core:message_detail', id)


class CreateRequestView(FormView):
    model = Message
    template_name = 'core/index.html'
    form_class = RequestLeaveForm
    success_url = reverse_lazy('core:dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):

        start_msg = form.cleaned_data['start']
        end_msg = form.cleaned_data['end']
        description = form.cleaned_data['description']
        substitute = form.cleaned_data['substitute']

        employee = Employee.objects.get(user_id=self.request.user.id)

        if employee.parent and (employee.is_manager or employee.is_expert):
            receiver = Employee.objects.get(user=employee.parent)
        else:
            receiver = employee

        Message.objects.create(sender=employee,
                               receiver=receiver,
                               start=start_msg,
                               end=end_msg,
                               description=description,
                               substitute=substitute)

        return super().form_valid(form)


@login_required()
def reply(request, id):
    user = request.user
    employee = Employee.objects.get(user=user)
    if request.method == 'POST':
        msg = Message.objects.get(id=id)
        form = CHOICES(request.POST)
        if form.is_valid():
            selected = form.cleaned_data.get("choice")
            msg.manager_choice = selected
            reply_msg = Reply.objects.create(
                message=msg,
                manager_choice=selected,
                is_done=False
            )
            msg.is_reply = True
            msg.save()
        return redirect('core:inbox')
    else:
        return redirect('core:message_detail', id)
