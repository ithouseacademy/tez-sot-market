import json
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings
from .models import Chat, Message, Mahsulot, SotibOlish, PushSubscription

try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None
    WebPushException = Exception


@login_required
def my_chats(request):
    chats = Chat.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).order_by('-updated_at')

    for chat in chats:
        chat.last_msg = chat.last_message()
        chat.unread = chat.unread_count(request.user)

    return render(request, 'my_chats.html', {'chats': chats})


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.buyer, chat.seller] and not request.user.is_superuser:
        messages.error(request, "Siz bu chatga kira olmaysiz")
        return redirect('my_chats')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        if text or image or video:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text,
                image=image,
                video=video,
            )
            chat.save()
        return redirect('chat_detail', chat_id=chat.id)

    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    messages_list = chat.messages.all()

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    return render(request, 'chat_detail.html', {
        'chat': chat,
        'messages': messages_list,
        'other_user': chat.seller if request.user == chat.buyer else chat.buyer,
        'today': today,
        'yesterday': yesterday,
    })


@login_required
def start_chat(request, product_id, seller_id):
    mahsulot = get_object_or_404(Mahsulot, id=product_id)
    seller = get_object_or_404(User, id=seller_id)

    if request.user == seller:
        messages.warning(request, "O'zingiz bilan chat yarata olmaysiz")
        return redirect('mahsulot_detail', mahsulot_id=product_id)

    chat, created = Chat.objects.get_or_create(
        mahsulot=mahsulot,
        buyer=request.user,
        seller=seller,
    )
    return redirect('chat_detail', chat_id=chat.id)


@login_required
def api_send_message(request, chat_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST kerak'})

    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.buyer, chat.seller]:
        return JsonResponse({'success': False, 'error': 'Ruxsat yo\'q'})

    text = request.POST.get('text', '').strip()
    image = request.FILES.get('image')
    video = request.FILES.get('video')

    if not text and not image and not video:
        return JsonResponse({'success': False, 'error': 'Xabar matni yoki fayl kerak'})

    msg = Message.objects.create(chat=chat, sender=request.user, text=text, image=image, video=video)
    chat.save()

    other_user = chat.seller if request.user == chat.buyer else chat.buyer
    body = text or ("Rasm" if image else "Video")
    send_push_notification(other_user, f"📩 {request.user.username}", body, f"/chat/{chat.id}/")

    return JsonResponse({
        'success': True,
        'message': {
            'id': msg.id,
            'text': msg.text,
            'image': msg.image.url if msg.image else None,
            'video': msg.video.url if msg.video else None,
            'created_at': msg.created_at.isoformat(),
            'is_mine': True,
        }
    })


@login_required
def api_chat_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.buyer, chat.seller]:
        return JsonResponse({'success': False, 'error': 'Ruxsat yo\'q'})

    since = request.GET.get('since')
    messages_qs = chat.messages.all()
    if since:
        from django.utils.dateparse import parse_datetime
        dt = parse_datetime(since)
        if dt:
            messages_qs = messages_qs.filter(created_at__gt=dt)

    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return JsonResponse({
        'success': True,
        'messages': [{
            'id': m.id,
            'text': m.text,
            'image': m.image.url if m.image else None,
            'video': m.video.url if m.video else None,
            'sender_id': m.sender.id,
            'sender_name': m.sender.username,
            'is_mine': m.sender == request.user,
            'is_read': m.is_read,
            'created_at': m.created_at.isoformat(),
        } for m in messages_qs]
    })


@login_required
def api_unread_count(request):
    total_unread = Message.objects.filter(
        chat__in=Chat.objects.filter(Q(buyer=request.user) | Q(seller=request.user))
    ).exclude(sender=request.user).filter(is_read=False).count()

    return JsonResponse({'unread': total_unread})


def send_push_notification(user, title, body, url='/'):
    if not webpush:
        return
    subs = PushSubscription.objects.filter(user=user)
    if not subs.exists():
        return
    payload = json.dumps({'title': title, 'body': body, 'url': url})
    for sub in subs:
        try:
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims=settings.VAPID_CLAIMS,
            )
        except WebPushException:
            sub.delete()


@login_required
def api_push_subscribe(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST kerak'})
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON xato'})
    sub, created = PushSubscription.objects.update_or_create(
        user=request.user,
        endpoint=data.get('endpoint'),
        defaults={
            'p256dh': data.get('keys', {}).get('p256dh', ''),
            'auth': data.get('keys', {}).get('auth', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:255],
        }
    )
    return JsonResponse({'success': True})


@login_required
def api_push_unsubscribe(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST kerak'})
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON xato'})
    PushSubscription.objects.filter(user=request.user, endpoint=data.get('endpoint')).delete()
    return JsonResponse({'success': True})


@login_required
def api_unread_details(request):
    """Eng oxirgi o'qilmagan xabar haqida ma'lumot"""
    chats = Chat.objects.filter(Q(buyer=request.user) | Q(seller=request.user))
    msg = Message.objects.filter(chat__in=chats).exclude(sender=request.user).filter(is_read=False).order_by('-created_at').first()
    if not msg:
        return JsonResponse({'has_unread': False})
    body = msg.text[:120] if msg.text else ('Rasm' if msg.image else 'Video')
    return JsonResponse({
        'has_unread': True,
        'sender': msg.sender.username,
        'text': body,
        'chat_id': msg.chat.id,
    })


def api_new_products(request):
    """Yangi qo'shilgan mahsulotlar (since_id dan keyingilari)"""
    try:
        since_id = int(request.GET.get('since_id', 0))
    except (ValueError, TypeError):
        since_id = 0

    products = Mahsulot.objects.filter(id__gt=since_id, aktiv=True).order_by('-id')[:5]
    if not products.exists():
        return JsonResponse({'has_new': False, 'products': []})

    result = []
    for p in products:
        img = p.asosiyimg.url if p.asosiyimg else None
        if img and not img.startswith('http'):
            img = request.build_absolute_uri(img)
        result.append({
            'id': p.id,
            'name': p.name,
            'narx': p.narx,
            'image': img,
            'user': p.user.username,
        })
    return JsonResponse({'has_new': True, 'products': result})