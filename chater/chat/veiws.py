from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .chat import get_response


def home(request):
    if request.method == 'POST':
        sentence = request.POST.get('message')
        bot_response = get_response(sentence)
        return JsonResponse({'message': sentence, 'botResponse': bot_response})
    visitor_message = """Welcome to Vigilant Site, your guardian in workplace safety! I'm here to guide you through our world of safety solutions. Whether you're curious about our services, need advice on safety practices, or have any other questions, I've got you covered. How can I assist you today?"""
    return render(request, 'index.html', {'visitor_message': visitor_message})
