from django.contrib import admin
from .models import Amenity, User, Property, Car, Job, Classifieds, Picture
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class PictureInline(admin.TabularInline):  # Or admin.StackedInline for a preview-like layout
    model = Picture
    extra = 3  # Number of extra blank image fields shown


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'mobile_number', 'is_staff')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'mobile_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'mobile_number', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

admin.site.register(User, UserAdmin)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'location', 'user', 'created_at')
    search_fields = ('title', 'location')
    list_filter = ('category',)
    inlines = [PictureInline]

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'price', 'category', 'user', 'created_at')
    search_fields = ('make', 'model')
    list_filter = ('category', 'year')
    inlines = [PictureInline]

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'location', 'category', 'user', 'created_at')
    search_fields = ('title', 'company_name', 'location')
    list_filter = ('category',)
    inlines = [PictureInline]

@admin.register(Classifieds)
class ClassifiedsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'contact_number', 'user', 'created_at')
    search_fields = ('title',)
    list_filter = ('category',)


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'car', 'job', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

admin.site.register(Amenity)


