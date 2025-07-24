# myapp/middleware/maintenance_middleware.py

from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow access to superusers and admin pages
        if settings.MAINTENANCE_MODE:
            if request.path.startswith('/admin/') and hasattr(request, "user") and request.user.is_superuser:
                return self.get_response(request)

            context = {
                "title" : "Kami sedang melakukan pemeliharaan sistem.",
                "message" : "Proses Merger Besar 3 Aplikasi (PMBP, Humas dan Piket) menjadi <strong>smait.albinaa.sch.id</strong>",
            }

            return render(request, 'maintenance.html', status=503, context=context)
        elif not settings.PIKET_MODE_ON and request.path.startswith('/piket/'):
            context = {
                "title" : "Aplikasi belum bisa digunakan!",
                "message" : "Aplikasi Piket tidak bisa digunakan apabila belum ada jadwal fix terbaru dari Kurikulum!",
            }
            return render(request, 'maintenance.html', status=503, context=context)

        return self.get_response(request)
