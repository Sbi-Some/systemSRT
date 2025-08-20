from django import forms
from django.core.exceptions import ValidationError
from .models import IntelligenceReport, ThreatCategory, HostileGroup

class IntelligenceReportForm(forms.ModelForm):
    threat_categories = forms.ModelMultipleChoiceField(
        queryset=ThreatCategory.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    hostile_groups = forms.ModelMultipleChoiceField(
        queryset=HostileGroup.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = IntelligenceReport
        fields = [
            'title', 'description', 'report_type', 'classification_level',
            'source_type', 'latitude', 'longitude', 'location_description',
            'threat_categories', 'hostile_groups', 'threat_level',
            'confidence_level', 'priority', 'tags'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Titre du rapport'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 6,
                'placeholder': 'Description détaillée du renseignement'
            }),
            'report_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'classification_level': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'source_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': 'any',
                'placeholder': 'ex: 48.8566'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': 'any',
                'placeholder': 'ex: 2.3522'
            }),
            'location_description': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Description de la localisation'
            }),
            'threat_level': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'confidence_level': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': 1,
                'max': 100,
                'placeholder': 'Niveau de confiance (1-100%)'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }, choices=[(i, f'Priorité {i}') for i in range(1, 6)]),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Tags séparés par des virgules'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        location_description = cleaned_data.get('location_description')
        
        # Validation: au moins une localisation doit être fournie
        if not any([latitude, longitude, location_description]):
            raise ValidationError(
                "Veuillez fournir soit des coordonnées GPS, soit une description de localisation."
            )
        
        # Validation: si une coordonnée est fournie, l'autre doit l'être aussi
        if (latitude is not None) != (longitude is not None):
            raise ValidationError(
                "Si vous fournissez des coordonnées GPS, veuillez renseigner à la fois la latitude et la longitude."
            )
        
        return cleaned_data
    
    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if tags:
            # Convertir la chaîne de tags en liste
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            return tag_list
        return []