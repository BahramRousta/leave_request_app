from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.cache import cache_control
from .models import Employee, Message, Reply
from .forms import TimeForm, CHOICES


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
def dashboard(request):
    user = request.user
    reply = Reply.objects.filter(
        message__sender=user,
        is_done=False
    ).count()
    new_msg = Message.objects.filter(
        receiver=user,
        is_reply=False
    ).count()
    number_message = reply + new_msg
    return render(request, 'core/dashboard.html', {'number_message': number_message})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
def inbox(request):
    user = request.user
    reply = Reply.objects.filter(
        message__sender=user,
        is_done=False
    )
    new_msg = Message.objects.filter(
        receiver=user,
        is_reply=False
    )
    return render(request, 'core/inbox.html', {'reply': reply,
                                               'new_msg': new_msg})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
def outbox(request):
    messages = None
    replies = None
    user = request.user
    employee = Employee.objects.filter(user=user).first()
    if not employee.parent:
        messages = Reply.objects.filter(message__receiver=employee)
    elif employee.parent and employee.is_manager:
        messages = Message.objects.filter(sender=employee)
        replies = Reply.objects.filter(message__receiver=employee)
    elif employee.parent and employee.is_expert:
        messages = Message.objects.filter(sender=employee)
    return render(request, 'core/outbox.html', {'messages': messages,
                                                'replies': replies})


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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
def leave_request_view(request):
    form = TimeForm()
    subtitue = Employee.objects.all().exclude(user=request.user)
    return render(request, 'core/index.html', {'subtitue': subtitue,
                                               'form': form})


@login_required()
def send(request):
    if request.method == 'POST':
        user = request.user
        employee = Employee.objects.filter(user=user).first()

        start_msg = request.POST['startday']
        end_msg = request.POST['endday']
        description = request.POST['description']

        if employee.parent and employee.is_manager:
            receiver = Employee.objects.get(user_id=employee.parent.id)
            msg = Message.objects.create(sender=employee,
                                         receiver=receiver,
                                         start=start_msg,
                                         end=end_msg,
                                         description=description,
                                         is_reply=False)
        elif employee.parent and employee.is_expert:
            receiver = Employee.objects.get(user_id=employee.parent.id)
            msg = Message.objects.create(sender=employee,
                                         receiver=receiver,
                                         start=start_msg,
                                         end=end_msg,
                                         description=description,
                                         is_reply=False)
        else:
            receiver = Employee.objects.get(user_id=employee.user.id)
            msg = Message.objects.create(sender=employee,
                                         receiver=receiver,
                                         start=start_msg,
                                         end=end_msg,
                                         description=description,
                                         is_reply=False)
        return render(request, 'core/send_message.html')
    else:
        return HttpResponse('leave_request_view')


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
