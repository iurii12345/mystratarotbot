from django.db import models

CARD_TYPES = [
    ('major', 'Старший аркан'),
    ('minor', 'Младший аркан'),
]

SUITS = [
    ('wands', 'Жезлы'),
    ('cups', 'Кубки'),
    ('swords', 'Мечи'),
    ('pentacles', 'Пентакли'),
]

class Card(models.Model):
    name = models.CharField("Название карты", max_length=100)
    url = models.SlugField("URL", unique=True)
    image = models.ImageField("Изображение", upload_to='cards/')
    desc = models.TextField("Описание прямого значения")
    message = models.CharField("Краткое послание", max_length=255, blank=True, null=True)
    rdesc = models.TextField("Описание перевёрнутого значения", blank=True, null=True)
    sequence = models.PositiveIntegerField("Номер карты в колоде")
    qabalah = models.CharField("Каббала", max_length=255, blank=True, null=True)
    hebrew_letter = models.CharField("Буква иврита", max_length=10, blank=True, null=True)
    cardtype = models.CharField("Тип карты", max_length=10, choices=CARD_TYPES)
    suit = models.CharField("Масть", max_length=10, choices=SUITS, blank=True, null=True)

    class Meta:
        ordering = ['sequence']
        verbose_name = "Карта Таро"
        verbose_name_plural = "Карты Таро"

    def __str__(self):
        return f"{self.name} ({self.cardtype})"