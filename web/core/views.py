from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, FormView, DetailView
from .models import Employee, Message, Reply
from .forms import RequestLeaveForm, ManagerChoiceForm


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


class MessageDetailView(DetailView):

    template_name = 'core/message_detail.html'

    def get_object(self):
        message = Message.objects.filter(pk=self.kwargs['pk']).first()
        if message:
            return message
        else:
            return Reply.objects.filter(pk=self.kwargs['pk']).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if isinstance(self.object, Message):
            context['message'] = self.object
            context['form'] = ManagerChoiceForm()
        elif isinstance(self.object, Reply):
            context['reply'] = self.object
        return context


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


class ReplyOnMessageView(CreateView):
    model = Reply
    fields = ['manager_choice']
    success_url = reverse_lazy('core:inbox')

    def form_valid(self, form):
        message = Message.objects.get(id=self.kwargs['pk'])

        form.instance.message = message
        form.instance.sender = self.request.user.employee
        form.instance.receiver = message.receiver

        message.is_reply = True
        message.manager_choice = form.cleaned_data['manager_choice']
        message.save()
        return super().form_valid(form)

