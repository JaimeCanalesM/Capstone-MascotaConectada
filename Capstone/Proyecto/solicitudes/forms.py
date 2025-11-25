from django import forms
from .models import Solicitud
from mascota.models import Mascota


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['tipo', 'asunto', 'descripcion', 'mascota', 'archivo_adjunto']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Solicitud de edición de datos de mi mascota'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe tu solicitud con el mayor detalle posible...'
            }),
            'mascota': forms.Select(attrs={'class': 'form-select'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'tipo': 'Tipo de solicitud',
            'asunto': 'Asunto',
            'descripcion': 'Descripción',
            'mascota': 'Mascota relacionada (opcional)',
            'archivo_adjunto': 'Adjuntar archivo (opcional)',
        }
        help_texts = {
            'mascota': 'Selecciona una mascota si tu solicitud está relacionada con ella',
            'archivo_adjunto': 'Puedes adjuntar capturas de pantalla, documentos, etc. (Máx 5MB)',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrar mascotas solo del usuario actual
        if user:
            self.fields['mascota'].queryset = Mascota.objects.filter(DUENO=user)
        else:
            self.fields['mascota'].queryset = Mascota.objects.none()

        # Hacer mascota opcional con opción vacía
        self.fields['mascota'].required = False
        self.fields['mascota'].empty_label = "Ninguna (No aplica)"

    def clean_archivo_adjunto(self):
        archivo = self.cleaned_data.get('archivo_adjunto')
        if archivo:
            # Validar tamaño (máx 5MB)
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo no debe exceder 5MB.')

            # Validar tipo de archivo (permitir imágenes y PDFs)
            ext = archivo.name.lower().split('.')[-1]
            if ext not in ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'txt']:
                raise forms.ValidationError(
                    'Tipo de archivo no permitido. Formatos aceptados: PDF, JPG, PNG, DOC, DOCX, TXT'
                )

        return archivo

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '').strip()
        if len(descripcion) < 20:
            raise forms.ValidationError('La descripción debe tener al menos 20 caracteres.')
        return descripcion
