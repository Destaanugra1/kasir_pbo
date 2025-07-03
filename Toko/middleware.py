from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URL yang boleh diakses tanpa login
        exempt_urls = [
            reverse('login'),
            '/',  # Homepage/landing page
            '/home/',  # Alternatif landing page
            '/static/',  # Static files
            '/media/',  # Media files
        ]
        
        # Cek apakah URL saat ini diizinkan tanpa login
        path_is_exempt = False
        for url in exempt_urls:
            if request.path.startswith(url):
                path_is_exempt = True
                break
                
        # Redirect ke login jika belum terautentikasi dan bukan URL exempt
        if not request.user.is_authenticated and not path_is_exempt:
            return redirect(settings.LOGIN_URL)
        
        response = self.get_response(request)
        return response