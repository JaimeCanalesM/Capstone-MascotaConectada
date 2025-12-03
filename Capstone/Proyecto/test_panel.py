import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')
django.setup()

from panel.views import DashboardView
from django.test import RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()

# Crear request simulado
factory = RequestFactory()
request = factory.get('/panel/')

# Crear usuario admin simulado
try:
    user = User.objects.filter(is_staff=True).first()
    if not user:
        # Crear usuario temporal
        user = User.objects.create_superuser('testadmin', 'test@test.com', 'test123')
        print("Usuario admin temporal creado")

    request.user = user

    # Intentar obtener el contexto
    view = DashboardView()
    view.request = request
    context = view.get_context_data()
    print("[OK] Contexto generado correctamente")
    print(f"[OK] Cohortes: {len(context.get('cohortes_retencion', []))}")
    print(f"[OK] Segmentacion RFM: {context.get('segmentacion_rfm', {})}")
    print(f"[OK] Clusters: {context.get('clusters', {})}")
    print(f"[OK] Horarios pico: {len(context.get('horarios_pico', []))}")
    print(f"[OK] Patrones dia: {len(context.get('patrones_dia_semana', []))}")
    print(f"[OK] Total usuarios: {context.get('total_usuarios', 0)}")
    print(f"[OK] Total mascotas: {context.get('total_mascotas', 0)}")
    print(f"[OK] Total citas: {context.get('total_citas', 0)}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
