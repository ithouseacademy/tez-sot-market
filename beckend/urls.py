from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render
import os


import mimetypes


def google_verification(request):
    from django.http import HttpResponse
    return HttpResponse("google-site-verification: google1a9e14b907f2d5a8.html", content_type="text/html")

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /auth/",
        "Sitemap: https://tezsotmarket-production.up.railway.app/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    from fronend.models import Mahsulot, Category
    from django.utils import timezone
    
    now = timezone.now().strftime("%Y-%m-%d")
    
    urls = []
    
    # Static pages
    static_pages = [
        ("", "0.9", "daily"),
        ("index/", "0.7", "daily"),
        ("barcha-mahsulotlar/", "0.8", "daily"),
        ("bizhaqimizda/", "0.3", "monthly"),
        ("boglanish/", "0.3", "monthly"),
        ("qoidalar/", "0.2", "monthly"),
        ("maxfiyliksiyosati/", "0.2", "monthly"),
        ("reklama/", "0.4", "weekly"),
        ("premium-mahsulotlar/", "0.7", "daily"),
    ]
    
    base_url = "https://tezsotmarket-production.up.railway.app"
    
    for path, priority, changefreq in static_pages:
        urls.append(f"""
  <url>
    <loc>{base_url}/{path}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>""")
    
    # Product pages (latest 100 products)
    products = Mahsulot.objects.filter(aktiv=True).order_by('-sana')[:100]
    for product in products:
        urls.append(f"""
  <url>
    <loc>{base_url}/mahsulot/{product.id}/</loc>
    <lastmod>{product.sana.strftime("%Y-%m-%d") if product.sana else now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>""")
    
    # Category pages
    categories = Mahsulot.CATEGORY_CHOICES
    for cat_key, cat_label in categories:
        urls.append(f"""
  <url>
    <loc>{base_url}/kategoriya/{cat_key}/</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.5</priority>
  </url>""")
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {"".join(urls)}
</urlset>"""
    
    return HttpResponse(xml, content_type="application/xml")

def media_serve(request, path):
    import os.path
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Length'] = os.path.getsize(file_path)
        response['Cache-Control'] = 'public, max-age=86400'
        return response
    raise Http404("Media file not found")

# 404 sahifa
def custom_404(request, exception):
    return render(request, '404.html', status=404)

handler404 = custom_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('google1a9e14b907f2d5a8.html', google_verification),
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('', include('fronend.urls')),  # asosiy app
    path('auth/', include('authentication.urls')),  # auth app
]

# Media fayllarni serving qilish
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', media_serve),
]

