from django.shortcuts import render

def index(request):
    return render(request, 'call/index.html')

def room(request):
    room_key = request.GET.get('key')  # Get 'key' from query params
    if not room_key:
        return render(request, 'call/index.html')  # Fallback if no key
    return render(request, 'call/room.html', {'room_key': room_key})