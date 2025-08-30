from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Product, ProductImage, Availability, Booking, Service


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'image_preview', 'created_date']
    list_filter = ['name']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_date']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Anzahl Produkte'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "Kein Bild"
    image_preview.short_description = 'Vorschau'
    
    def created_date(self, obj):
        return obj.id  # Простое поле для сортировки
    created_date.short_description = 'ID'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'order', 'created_at']
    list_filter = ['product', 'created_at']
    search_fields = ['product__title', 'alt_text']
    list_editable = ['order']
    ordering = ['product', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 80px;" />',
                obj.image.url
            )
        return "Kein Bild"
    image_preview.short_description = 'Vorschau'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'is_active', 'image_preview', 'booking_count']
    list_filter = ['category', 'is_active', 'price']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'price']
    readonly_fields = ['image_preview', 'booking_count']
    
    fieldsets = (
        ('Grundinformationen', {
            'fields': ('title', 'slug', 'description', 'category')
        }),
        ('Preis & Status', {
            'fields': ('price', 'is_active')
        }),
        ('Bild', {
            'fields': ('image', 'image_preview')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "Kein Bild"
    image_preview.short_description = 'Vorschau'
    
    def booking_count(self, obj):
        count = obj.bookings.count()
        if count > 0:
            url = reverse('admin:catalog_booking_changelist') + f'?product__id__exact={obj.id}'
            return format_html('<a href="{}">{} Buchungen</a>', url, count)
        return "0 Buchungen"
    booking_count.short_description = 'Buchungen'





@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['product', 'start_date', 'end_date', 'is_available', 'duration_days']
    list_filter = ['is_available', 'start_date', 'end_date', 'product']
    search_fields = ['product__title']
    list_editable = ['is_available']
    
    def duration_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1
    duration_days.short_description = 'Dauer (Tage)'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'is_active', 'image_preview', 'created_at']
    list_filter = ['is_active', 'price']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'price']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "Kein Bild"
    image_preview.short_description = 'Vorschau'


# Настройка админки
admin.site.site_header = "Play & Jump Admin"
admin.site.site_title = "Play & Jump"
admin.site.index_title = "Willkommen in der Play & Jump Verwaltung"

# Добавляем ссылку на страницу управления бронированиями
from django.urls import reverse
from django.utils.html import format_html

class BookingAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'product', 'start_date', 'end_date', 'total_price', 'status', 'duration_days', 'booking_management_link']
    list_filter = ['status', 'start_date', 'product']
    search_fields = ['customer_name', 'customer_email', 'product__title']
    readonly_fields = ['duration_days', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    def booking_management_link(self, obj):
        url = reverse('catalog:booking_management')
        return format_html('<a href="{}" target="_blank">📅 Kalender öffnen</a>', url)
    booking_management_link.short_description = 'Kalender'
    
    actions = ['confirm_bookings', 'cancel_bookings']
    
    def confirm_bookings(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} Buchungen wurden bestätigt.')
    confirm_bookings.short_description = "Ausgewählte Buchungen bestätigen"
    
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} Buchungen wurden storniert.')
    cancel_bookings.short_description = "Ausgewählte Buchungen stornieren"

# Регистрируем Booking с обновленным админом
admin.site.register(Booking, BookingAdmin)

# Добавляем ссылку на страницу управления бронированиями в админ-панель
# (без замены стандартного admin.site)
