from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from citas.models import Cita


class Command(BaseCommand):
    help = 'Envía recordatorios por correo electrónico para las citas del día siguiente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra las citas que se procesarían sin enviar correos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Calcular el rango de fechas para mañana (día siguiente)
        ahora = timezone.now()
        inicio_manana = (ahora + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        fin_manana = inicio_manana + timedelta(days=1)

        # Buscar citas para mañana que estén PENDIENTES o CONFIRMADAS
        citas_manana = Cita.objects.filter(
            fecha_hora__gte=inicio_manana,
            fecha_hora__lt=fin_manana,
            estado__in=[Cita.PENDIENTE, Cita.CONFIRMADA]
        ).select_related('mascota', 'mascota__DUENO', 'clinica', 'veterinario')

        total_citas = citas_manana.count()

        if total_citas == 0:
            self.stdout.write(self.style.WARNING('No hay citas para mañana que requieran recordatorio.'))
            return

        self.stdout.write(f'Encontradas {total_citas} citas para mañana.')

        enviados = 0
        errores = 0

        for cita in citas_manana:
            dueno = cita.dueno
            mascota = cita.mascota

            # Preparar contexto para el template
            contexto = {
                'nombre_dueno': dueno.get_full_name() or dueno.username,
                'nombre_mascota': mascota.nombre,
                'especie_mascota': mascota.especie,
                'fecha_hora': cita.fecha_hora,
                'motivo': cita.motivo,
                'notas': cita.notas,
                'clinica': cita.clinica.nombre if cita.clinica else 'No especificada',
                'direccion_clinica': cita.clinica.direccion if cita.clinica else None,
                'telefono_clinica': cita.clinica.telefono if cita.clinica else None,
                'veterinario': cita.veterinario.get_full_name() if cita.veterinario else 'Por asignar',
                'estado': cita.get_estado_display(),
            }

            asunto = f'Recordatorio: Cita de {mascota.nombre} mañana - MascotaConectada'

            if dry_run:
                self.stdout.write(f'  [DRY-RUN] Correo a: {dueno.email} - Cita: {cita}')
                enviados += 1
            else:
                try:
                    # Renderizar el template
                    mensaje_html = render_to_string('emails/recordatorio_cita.html', contexto)

                    # Enviar correo
                    send_mail(
                        subject=asunto,
                        message='',  # Vacío porque usamos HTML
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[dueno.email],
                        html_message=mensaje_html,
                        fail_silently=False,
                    )

                    self.stdout.write(self.style.SUCCESS(f'  ✓ Correo enviado a: {dueno.email} - Cita: {cita}'))
                    enviados += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error enviando a {dueno.email}: {str(e)}'))
                    errores += 1

        # Resumen final
        if dry_run:
            self.stdout.write(self.style.WARNING(f'\n[DRY-RUN] Se procesaron {enviados} citas (no se enviaron correos reales)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Recordatorios enviados exitosamente: {enviados}'))
            if errores > 0:
                self.stdout.write(self.style.ERROR(f'✗ Errores: {errores}'))
