from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Employee, Message, Reply
from .forms import TimeForm, CHOICES


@login_required()
def dashboard(request):
    user = request.user
    reply = Reply.objects.filter(
        receiver=user,
        is_done=False
    ).count()
    new_msg = Message.objects.filter(
        receiver=user,
        is_reply=False
    ).count()
    number_message = reply + new_msg
    return render(request, 'core/dashboard.html', {'number_message': number_message})

@login_required()
def inbox(request):
    user = request.user
    employee = Employee.objects.filter(user=user).first()
    reply = Reply.objects.filter(
        receiver=employee,
        is_done=False
    )
    new_msg = Message.objects.filter(
        receiver=employee,
        is_reply=False
    )
    return render(request, 'core/inbox.html', {'reply': reply,
                                          'new_msg': new_msg})


@login_required()
def message_detail(request, id):
    msg = Message.objects.get(id=id)

    if msg.is_reply:
        reply = Reply.objects.get(message_id=msg.id)
        return render(request, 'core/message_detail.html', {'reply': reply})
    else:
        form = CHOICES()
        return render(request, 'core/message_detail.html', {'msg': msg,
                                                       'form': form})


def done_message_status(request, id):
    if request.method == "POST":
        msg = Reply.objects.get(id=id)
        msg.is_done = True
        msg.save()
        return redirect('inbox')
    else:
        return redirect('message_detail', id)


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
        return HttpResponse('Message successfully send')
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
                message_id=msg.id,
                receiver=msg.sender,
                start=msg.start,
                end=msg.end,
                sender=employee,
                description=msg.description,
                manager_choice=selected,
                is_done=True
            )
            msg.is_reply = True
            msg.save()
        return redirect('core:inbox')
    else:
        return redirect('core:message_detail', id)
