from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    title = models.CharField(max_length=35)

    def __str__(self):
        return f"{self.title}"


class Position(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='employee')
    department = models.ForeignKey(Department,
                                   on_delete=models.CASCADE,
                                   related_name='employee_department')
    position = models.ForeignKey(Position,
                                 on_delete=models.CASCADE,
                                 related_name='employee_position')
    is_manager = models.BooleanField(default=False)
    is_expert = models.BooleanField(default=True)
    parent = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               related_name='parent')

    def __str__(self):
        return f"{self.user}"


class Message(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='message_sender')
    receiver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='message_receiver')
    substitute = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='message_substitute')
    description = models.TextField()
    is_reply = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    CHOICE = [
        ('Agree', 'agree'),
        ('DisAgree', 'disagree')
    ]
    manager_choice = models.CharField(max_length=8, choices=CHOICE)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

    class Meta:
        ordering = ('-created',)


class Reply(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='replies')
    manager_choice = models.CharField(max_length=10)
    is_done = models.BooleanField(default=False)
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reply_sender')
    receiver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reply_receiver')

    def __str__(self):
        return f"Reply from {self.sender} to {self.receiver}"
