from django import forms
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
from .models import Product


class ProductForm(forms.ModelForm):
    """Форма для создания/редактирования товара"""

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'manufacturer',
            'supplier', 'price', 'unit', 'quantity', 'discount', 'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manufacturer': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем подсказки к полям
        self.fields['price'].help_text = 'Цена в рублях'
        self.fields['discount'].help_text = 'Скидка в процентах (0-100)'
        self.fields['quantity'].help_text = 'Количество на складе (не может быть отрицательным)'
        self.fields['image'].help_text = 'Изображение товара (опционально, не больше 300x200)'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        uploaded_image = Image.open(image)
        max_width = 300
        max_height = 200

        if uploaded_image.width <= max_width and uploaded_image.height <= max_height:
            image.seek(0)
            return image

        uploaded_image.thumbnail((max_width, max_height))
        buffer = io.BytesIO()
        image_format = uploaded_image.format or 'PNG'
        uploaded_image.save(buffer, format=image_format)
        buffer.seek(0)

        return InMemoryUploadedFile(
            file=buffer,
            field_name='image',
            name=image.name,
            content_type=image.content_type,
            size=buffer.getbuffer().nbytes,
            charset=None,
        )