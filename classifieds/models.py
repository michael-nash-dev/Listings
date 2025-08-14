from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.contrib.auth.models import User


CATEGORY_CHOICES = [
    ('car', 'Car Dealer'),
    ('real_estate', 'Real Estate Agent'),
    ('job', 'Job Recruiter'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]


    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, mobile_number, first_name, last_name, password=None):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            mobile_number=mobile_number,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile_number, first_name, last_name, password):
        user = self.create_user(email, mobile_number, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile_number', 'first_name', 'last_name']


    

    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"
    
class Classifieds(models.Model):
     user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='listings')
     title = models.CharField(max_length=200)
     description = models.TextField()
     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
     contact_number = models.CharField(max_length=15)
     whatsapp_link = models.URLField(blank=True)
     image = models.ImageField(upload_to='listing_images/', blank=True, null=True)
     created_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

# Property Subcategories
PROPERTY_CATEGORIES = [
    ('houses_for_sale', 'Houses for Sale'),
    ('land_for_sale', 'Land for Sale'),
    ('houses_to_rent', 'Houses to Rent'),
]

# Car Subcategories
CAR_CATEGORIES = [
    ('Toyota', 'Toyota'),
    ('BMW', 'BMW'),
    ('Mercedes-Benz', 'Mercedes-Benz'),
    ('Nissan', 'Nissan'),
    ('Honda', 'Honda'),
    ('Isuzu', 'Isuzu'),
    ('Mazda', 'Mazda'),
   
]

# Job Subcategories
JOB_CATEGORIES = [
    ('it & software', 'IT & Software'),
    ('construction', 'Construction'),
    ('education', 'Education'),
   
]

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='amenities/icons/')  # optional for custom icons

    class Meta:
        verbose_name_plural = "Amenities" 

    def __str__(self):
        return self.name

#Property Model
class Property(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='properties')
    category = models.CharField(max_length=20, choices=PROPERTY_CATEGORIES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    surbub = models.CharField(max_length=100, default='Unknown')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    contact_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    amenities = models.ManyToManyField(Amenity, blank=True)

    class Meta:
        verbose_name_plural = "Properties" 

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
    

#Car model
class Car(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='cars')
    category = models.CharField(max_length=20, choices=CAR_CATEGORIES)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    mileage = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=100, default='Unknown')
    contact_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='car_images/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.get_category_display()})"
    

#Jobs model
class Job(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='jobs')
    category = models.CharField(max_length=20, choices=JOB_CATEGORIES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company_name} ({self.get_category_display()})"


#Picture model to handle multiple pictures
class Picture(models.Model):
    property = models.ForeignKey(
        'Property',  
        on_delete=models.CASCADE,
        related_name='pictures',
        null=True,
        blank=True
    )
    car = models.ForeignKey(
        'Car',
        on_delete=models.CASCADE,
        related_name='pictures',
        null=True,
        blank=True
    )
    job = models.ForeignKey(
        'Job',
        on_delete=models.CASCADE,
        related_name='pictures',
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='listing_pictures/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property or self.car or self.job}"

#Manage adverts
class AdvertCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Advert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(AdvertCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} ({self.category.name})"
    
class ContactMessage(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    sender_name = models.CharField(max_length=100)
    sender_email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender_name} to {self.seller.username}"




