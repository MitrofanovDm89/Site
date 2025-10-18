from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor.fields import RichTextField


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = RichTextField(blank=True, config_name='product_description')
    image = models.ImageField(upload_to="products/")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/additional/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.product.title} - Image {self.order + 1}"


class News(models.Model):
    """Модель для новостей"""
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL")
    content = models.TextField(verbose_name="Содержание")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Краткое описание")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Главное изображение")
    video_url = models.URLField(blank=True, null=True, verbose_name="URL видео (YouTube/Vimeo)")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    featured = models.BooleanField(default=False, verbose_name="Рекомендуемая новость")
    
    class Meta:
        ordering = ['-published_at']
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('catalog:news_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Availability(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='availabilities')
    start_date = models.DateField()
    end_date = models.DateField()
    is_available = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        status = "verfügbar" if self.is_available else "nicht verfügbar"
        return f"{self.product.title} – {self.start_date} bis {self.end_date} – {status}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ausstehend'),
        ('confirmed', 'Bestätigt'),
        ('cancelled', 'Storniert'),
        ('completed', 'Abgeschlossen'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.product.title} ({self.start_date} bis {self.end_date})"
    
    @property
    def duration_days(self):
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days + 1
        return 0


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class MissingProduct(models.Model):
    """Модель для управления дополнительными товарами в разделе Zusätzliche Produkte"""
    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to="missing_products/", verbose_name="Изображение")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Цена")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Zusätzliche Produkte"
        verbose_name_plural = "Zusätzliche Produkte"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_missing_products(cls, limit=2):
        """Возвращает активные дополнительные товары (максимум 2)"""
        return cls.objects.filter(is_active=True).order_by('order', 'created_at')[:limit] 