from django.db import models
# Create your models here.
class News(models.Model):
    CATEGORY_CHOICES = [
        ('sports', 'Sports'),
        ('technology', 'Technology'),
        ('politics', 'Politics'),
        # Agrega más categorías según sea necesario
    ]
    title = models.CharField(max_length=900)
    description = models.TextField(blank=True, null=True)
    url = models.URLField()
    published_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=500)
    url_to_image = models.URLField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=250, choices=CATEGORY_CHOICES, default='sports')
    
    def __str__(self):
        return self.title
