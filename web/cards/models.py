from django.db import models

class Card(models.Model):
    name = models.CharField(max_length=100)  # Название карты
    description = models.TextField()  # Описание карты
    image = models.ImageField(upload_to='cards/')  # Путь хранения картинки в MEDIA_ROOT

    def __str__(self):
        return self.name

