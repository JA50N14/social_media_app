from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from . models import Chat, Message, ChatViewed
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def chat_view(request, user_id):
    chat_with = get_object_or_404(User, id=user_id)
    try:
        chat = Chat.objects.get(Q(user1=request.user, user2=chat_with) | Q(user1=chat_with, user2=request.user))
    except Chat.DoesNotExist:
        if request.user.id < chat_with.id:
            chat = Chat.objects.create(user1=request.user, user2=chat_with)
        else:
            chat = Chat.objects.create(user1=chat_with, user2=request.user)

    #Used to display whether a message has been seen by the receiver
    ChatViewed.objects.update_or_create(user=request.user, chat=chat)
    chat_viewed_object = ChatViewed.objects.get(user=request.user, chat=chat)


    if request.user.id < chat_with.id:
        chat_group_id = f'{request.user.last_name}{chat_with.last_name}'
    else:
        chat_group_id = f'{chat_with.last_name}{request.user.last_name}'

    historic_messages = Message.objects.filter(chat=chat).order_by('timestamp')
    return render(request, 'chat.html', {'chat_with': chat_with, 'historic_messages': historic_messages, 'chat_group_id': chat_group_id})
