from django.views.decorators.csrf import csrf_exempt,ensure_csrf_cookie
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
import requests
from .models import ContactMessage, Property, Car, Job,Picture
from django.http import HttpResponse, JsonResponse
import json
from django.db.models import Q, F
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PropertyForm, CarForm, JobForm, CustomUserCreationForm, ContactSellerForm
from django.contrib.auth import logout,login
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .filters import PropertyFilter
import re
from twilio.twiml.messaging_response import MessagingResponse
from .wit_utils import extract_intent_entities



CATEGORY_MAP = {
                'IT & Software': 'it & software',
                'Construction': 'construction',
                'Education': 'education'
            }  
  

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('users/login.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def home(request):
    return render(request, 'listings/home.html')

#Get a list of properties and search query
def property_list(request):
    properties = Property.objects.all()
    query = request.GET.get('q')
    filters = {}

    if query:
        parsed = parse_query(query)
        filters.update(parsed)

    location = request.GET.get('location')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    status = request.GET.get('status')
    is_active = request.GET.get('is_active')

    # Parsed filters
    if 'location__icontains' in filters:
        properties = properties.filter(location__icontains=filters['location__icontains'])
    if 'max_price' in filters:
        properties = properties.filter(price__lte=filters['max_price'])

    # Manual filters
    if location:
        properties = properties.filter(location__icontains=location)
    if category:
        properties = properties.filter(category__icontains=category)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if status:
        properties = properties.filter(status__iexact=status)
    if is_active in ['true', 'false']:
        properties = properties.filter(is_active=(is_active == 'true'))

    combined_filters = {
        'location': location or filters.get('location__icontains', ''),
        'category': category,
        'min_price': min_price or filters.get('min_price', ''),
        'max_price': max_price or filters.get('max_price', ''),
        'status': status,
        'is_active': is_active
    }

    context = {
        'properties': properties,
        'filters': combined_filters,
        'query': query
    }
    return render(request, 'listings/property_list.html', context)



def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.views = F('views') + 1
    property.save(update_fields=['views'])
    property.refresh_from_db()  # get updated view count
    
    return render(request, 'listings/property_detail.html', {'property': property})

#Get a list of cars
def car_list(request):
    cars = Car.objects.all()
    query = request.GET.get('q')
    filters = {}

    if query:
        parsed = parse_query(query)
        filters.update(parsed)

    make = request.GET.get('make')
    model = request.GET.get('model')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    status = request.GET.get('status')
    is_active = request.GET.get('is_active')

    # Apply parsed filters first
    if 'make__icontains' in filters:
        cars = cars.filter(make__icontains=filters['make__icontains'])
    if 'model__icontains' in filters:
        cars = cars.filter(model__icontains=filters['model__icontains'])
    if 'location__icontains' in filters:
        cars = cars.filter(location__icontains=filters['location__icontains'])
    if 'max_price' in filters:
        cars = cars.filter(price__lte=filters['max_price'])

    # Manual filters from dropdown
    if make:
        cars = cars.filter(make__icontains=make)
    if model:
        cars = cars.filter(model__icontains=model)
    if min_price:
        cars = cars.filter(price__gte=min_price)
    if max_price:
        cars = cars.filter(price__lte=max_price)
    if status:
        cars = cars.filter(status__iexact=status)
    if is_active in ['true', 'false']:
        cars = cars.filter(is_active=(is_active == 'true'))

    # Combine manual + parsed filters for UI
    combined_filters = {
        'make': make or filters.get('make__icontains', ''),
        'model': model or filters.get('model__icontains', ''),
        'min_price': min_price or filters.get('min_price', ''),
        'max_price': max_price or filters.get('max_price', ''),
        'status': status,
        'is_active': is_active
    }

    context = {
        'cars': cars,
        'filters': combined_filters,
        'query': query
    }
    return render(request, 'listings/car_list.html', context)

    

def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    car.views = F('views') + 1
    car.save(update_fields=['views'])
    car.refresh_from_db()  # get updated view count
   
    return render(request, 'listings/car_detail.html', {'car': car})

#Get a list of job adverts
def job_list(request):
    jobs = Job.objects.all()
    query = request.GET.get('q')
    filters = {}

    if query:
        parsed = parse_query(query)
        filters.update(parsed)

    title = request.GET.get('title')
    category = request.GET.get('category')
    location = request.GET.get('location')
    min_salary = request.GET.get('min_salary')
    max_salary = request.GET.get('max_salary')
    status = request.GET.get('status')
    is_active = request.GET.get('is_active')

    # Parsed filters
    if 'location__icontains' in filters:
        jobs = jobs.filter(location__icontains=filters['location__icontains'])
    if 'title__icontains' in filters:
        jobs = jobs.filter(title__icontains=filters['title__icontains'])
    if 'max_salary' in filters:
        jobs = jobs.filter(salary__lte=filters['max_salary'])

    # Manual filters
    if title:
        jobs = jobs.filter(title__icontains=title)
    if category:
        jobs = jobs.filter(category__iexact=category)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if min_salary:
        jobs = jobs.filter(salary__gte=min_salary)
    if max_salary:
        jobs = jobs.filter(salary__lte=max_salary)
    if status:
        jobs = jobs.filter(status__iexact=status)
    if is_active in ['true', 'false']:
        jobs = jobs.filter(is_active=(is_active == 'true'))

    combined_filters = {
        'title': title or filters.get('title__icontains', ''),
        'category': category,
        'location': location or filters.get('location__icontains', ''),
        'min_salary': min_salary,
        'max_salary': max_salary or filters.get('max_salary', ''),
        'status': status,
        'is_active': is_active
    }

    context = {
        'jobs': jobs,
        'filters': combined_filters,
        'query': query
    }
    return render(request, 'listings/job_list.html', context)


   

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    job.views = F('views') + 1
    job.save(update_fields=['views'])
    job.refresh_from_db()  # get updated view count
    
    return render(request, 'listings/job_detail.html', {'job': job})

#JSON view function for a list of cars
def car_list_json(request):
    make_query = request.GET.get('make')  # get `make` from query parameters

    cars = Car.objects.all()

    if make_query:
        cars = cars.filter(make__icontains=make_query)  # case-insensitive partial match

    car_data = []
    for car in cars:
        car_data.append({
            'id': car.id,
            'make': car.make,
            'model': car.model,
            'year': car.year,
            'price': str(car.price),
            'mileage': car.mileage,
            'location': car.location,
            'contact_number': car.contact_number,
            'category': car.category,
            'created_at': car.created_at,
            'images': [pic.image.url for pic in car.pictures.all()]
        })

    return JsonResponse(car_data, safe=False)



@ensure_csrf_cookie
def car_models(request):
   
        try:
            data = json.loads(request.body)
            print("Received:", data)
            car_model_list=[]

            # Extract car make selection
            car_make = data['results']['car_make_selection']['category']  # "Toyota"
            car_model = data['results']['car_model_selection']['category']  # "Land Cruiser"
            print(car_make)
            print(car_model)
          # Get make from webhook payload
            model_obj = Car.objects.filter(make=car_make, model=car_model).exists()
            if model_obj:
                car_model_obj = Car.objects.filter(make=car_make, model=car_model)
                
            for car in car_model_obj:
                image_url = request.build_absolute_uri(car.image.url) if car.image else None
                car_obj=f"*{car.make}*\n{car.model}\n{car.year}\n{car.mileage}\n${car.price}\n\n-------------\n"
            if image_url:
                car_obj += f"\n📸 {image_url}"

                car_obj += "\n\n-------------\n"
                car_model_list.append(car_obj)
            else:
                print("Model does not exist")
            print(car_model_list)
            return JsonResponse({'cars': car_model_list}, safe=False)
        except Exception as e:
            print(str(e))

#Mapping for Property model
CATEGORY_LABEL_TO_VALUE = {
    'Houses for Sale': 'houses_for_sale',
    'Land for Sale': 'land_for_sale',
    'Houses to Rent': 'houses_to_rent',
}

@csrf_exempt
def property_models(request):
    try:
        data = json.loads(request.body)
        print("Received:", data)
        property_model_list = []

        # Extract category and location
        category_label = data['results']['property_category_selection']['category']
        location = data['results']['property_location_selection']['category']

        # Convert label to DB-friendly category value
        category = CATEGORY_LABEL_TO_VALUE.get(category_label)
        if not category:
            return JsonResponse({'error': 'Unknown category label'}, status=400)

        print(category)
        print(location)

        # Query database using normalized values
        if Property.objects.filter(category=category, location__iexact=location).exists():
            properties = Property.objects.filter(category=category, location__iexact=location)

            for prop in properties:
                image_url = request.build_absolute_uri(prop.image.url) if prop.image else None
                property_obj = (
                    f"*{prop.title}*\n"
                    f"{prop.description}\n"
                    f"{prop.location}\n"
                    f"{prop.surbub}\n"
                    f"${prop.price}\n"
                    f"{prop.contact_number}\n\n-------------\n"
                )
                if image_url:
                    property_obj += f"\n📸 {image_url}"

                property_obj += "\n\n-------------\n"
                property_model_list.append(property_obj)
        else:
            print("Model does not exist")

        print(property_model_list)
        return JsonResponse({'properties': property_model_list}, safe=False)
    except Exception as e:
        print(str(e))
        return JsonResponse({'error': str(e)}, status=500)


#Job model function
@ensure_csrf_cookie
def job_models(request):
   
        try:
            data = json.loads(request.body)
            print("Received:", data)
            job_model_list=[]

            #CATEGORY_MAP = {
                #'IT & Software': 'it & software',
                #'Construction': 'construction',
                #'Education': 'education'
            #}  
            
            job_category_label = data['results']['job_category_selection']['category']
            job_category = CATEGORY_MAP.get(job_category_label)
          
            print(job_category)
           
          # Get make from webhook payload
            model_obj = Job.objects.filter(category=job_category).exists()
            if model_obj:
                job_model_obj = Job.objects.filter(category=job_category)
                
                for job in job_model_obj:
                   job_obj=f"*{job.title}*\n{job.description}\n{job.company_name}\n{job.location}\n${job.salary}\n{job.contact_email}\n{job.contact_number}\n\n-------------\n"
           
                job_model_list.append(job_obj)
            else:
                print("Model does not exist")
            print(job_model_list)
            return JsonResponse({'jobs': job_model_list}, safe=False)
        except Exception as e:
            print(str(e))


def home(request):
    categories = [
        {
            'icon': 'bi-house-fill',
            'count': Property.objects.count(),
            'name': 'Property',
            'subcategories': [
                'Houses for Sale',
                'Land for Sale',
                'Houses to Rent',
                
            ]
        },
        {
            'icon': 'bi-car-front-fill',
            'count': Car.objects.count(),
            'name': 'Cars',
            
            'subcategories': [
                'Toyota',
                'Mercedes-Benz',
                'Mazda',
                'BMW',
                'Honda',
            ]
        },
        {
            'icon': 'bi-briefcase',
            'count': Job.objects.count(),
            'name': 'Jobs',
            'subcategories': [
                'IT & Software',
                'Construction',
                'Education',
                
            ]
        },
        
    ]

    return render(request, 'classifieds/home.html', {'categories': categories})
           

def listings_view(request):
    category = request.GET.get('category')  # e.g., "Property"
    subcategory = request.GET.get('type')   # e.g., "Houses for Sale"
    query = request.GET.get('q')            # Search input

    properties = Property.objects.none()
    cars = Car.objects.none()
    jobs = Job.objects.none()

    # 🟦 Search filter (if query present)
    if query:
        properties = Property.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(surbub__icontains=query)
        )
        cars = Car.objects.filter(
            Q(make__icontains=query) |
            Q(model__icontains=query)
        )
        jobs = Job.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )

    if category == "Property":
        properties = Property.objects.all()
        if subcategory:
            normalized = subcategory.replace(" ", "_").lower()
            properties = properties.filter(category__iexact=normalized)

    if category == "Cars":
        cars = Car.objects.all()
        if subcategory:
           normalized = subcategory.replace(" ", "_").lower()
        cars = cars.filter(category__iexact=normalized)

    if category == "Jobs":
        jobs = Job.objects.all()
        if subcategory:
            normalized = CATEGORY_MAP.get(subcategory, subcategory.lower())
        jobs = jobs.filter(category__iexact=normalized)

    context = {
        'properties': properties,
        'cars': cars,
        'jobs': jobs,
        'selected_category': category,
        'selected_type': subcategory,
        'search_query': query,
    }

    return render(request, 'classifieds/listings.html', context)


#dashboard counts for multiple models
def dashboard_counts(request):
    data = [
        {
            'icon': 'bi-house-fill',
            'count': Property.objects.count(),
            'name': 'Property',
        },
        {
            'icon': 'bi-car-front-fill',
            'count': Car.objects.count(),
            'name': 'Cars',
        },
        {
            'icon': 'bi-person-workspace',
            'count': Job.objects.count(),
            'name': 'Jobs',
        },
    ]
    return JsonResponse({'dashboard': data})

@login_required
def upload_listing(request):
    listing_type = request.GET.get('type')
    form = None

    if request.method == 'POST':
        listing_type = request.POST.get('type')  # get from form submission

        if listing_type == 'property':
            form = PropertyForm(request.POST, request.FILES)
        elif listing_type == 'car':
            form = CarForm(request.POST, request.FILES)
        elif listing_type == 'job':
            form = JobForm(request.POST)

        if form and form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()

            # ✅ Handle multiple images for property or car
            images = request.FILES.getlist('pictures')
            if listing_type == 'car':
                for image in images:
                    Picture.objects.create(car=instance, image=image)
            elif listing_type == 'property':
                for image in images:
                    Picture.objects.create(property=instance, image=image)

            return redirect('home')  

    else:
        # Show empty form when user selects type
        if listing_type == 'property':
            form = PropertyForm()
        elif listing_type == 'car':
            form = CarForm()
        elif listing_type == 'job':
            form = JobForm()

    return render(request, 'upload_listing.html', {
        'form': form,
        'type': listing_type,
    })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')  
    else:
        form = AuthenticationForm()
    
    return render(request, 'base/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  

#List User's own listings
@login_required
def my_adverts(request):
    properties = Property.objects.filter(user=request.user)
    cars = Car.objects.filter(user=request.user)
    jobs = Job.objects.filter(user=request.user)

    paginator_p = Paginator(properties, 3)
    paginator_c = Paginator(cars, 3)
    paginator_j = Paginator(jobs, 3)

    page_number = request.GET.get('page')

    context = {
        'properties': paginator_p.get_page(page_number),
        'cars': paginator_c.get_page(page_number),
        'jobs': paginator_j.get_page(page_number)
    }
    return render(request, 'users/my_adverts.html', context)

@login_required
def edit_property(request, pk):
    advert = get_object_or_404(Property, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=advert)
        if form.is_valid():
            form.save()
            return redirect('my_adverts')
    else:
        form = PropertyForm(instance=advert)
    return render(request, 'users/edit_property_advert.html', {'form': form})

@login_required
def edit_car(request, pk):
    advert = get_object_or_404(Car, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=advert)
        if form.is_valid():
            form.save()
            return redirect('my_adverts')
    else:
        form = CarForm(instance=advert)
    return render(request, 'users/edit_car_advert.html', {'form': form})

@login_required
def edit_job(request, pk):
    advert = get_object_or_404(Job, pk=pk, user=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=advert)
        if form.is_valid():
            form.save()
            return redirect('my_adverts')
    else:
        form = JobForm(instance=advert)
    return render(request, 'users/edit_job_advert.html', {'form': form})

@login_required
def delete_property(request, pk):
    ad = get_object_or_404(Property, pk=pk, user=request.user)
    ad.delete()
    messages.success(request, "Property listing deleted.")
    return redirect('my_adverts')

@login_required
def delete_car(request, pk):
    ad = get_object_or_404(Car, pk=pk, user=request.user)
    ad.delete()
    messages.success(request, "Car listing deleted.")
    return redirect('my_adverts')

@login_required
def delete_job(request, pk):
    ad = get_object_or_404(Job, pk=pk, user=request.user)
    ad.delete()
    messages.success(request, "Job listing deleted.")
    return redirect('my_adverts')

@login_required
def toggle_visibility_property(request, pk):
    ad = get_object_or_404(Property, pk=pk, user=request.user)
    ad.is_active = not ad.is_active
    ad.save()
    return redirect('my_adverts')

@login_required
def toggle_visibility_car(request, pk):
    ad = get_object_or_404(Car, pk=pk, user=request.user)
    ad.is_active = not ad.is_active
    ad.save()
    return redirect('my_adverts')

@login_required
def toggle_visibility_job(request, pk):
    ad = get_object_or_404(Job, pk=pk, user=request.user)
    ad.is_active = not ad.is_active
    ad.save()
    return redirect('my_adverts')

#Send email when form is submitted
def contact_seller(request, property_id):
    property = get_object_or_404(Property, pk=property_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        from_email = request.POST['email']
        message = request.POST['message']
        
        subject = f"Interest in: {property.title}"
        full_message = f"{message}\n\nFrom: {name} ({from_email})"

        send_mail(
            subject,
            full_message,
            from_email,  # ⬅️ comes from the visitor
            [property.user.email],  # ⬅️ seller email
            fail_silently=False,
        )
        print(request.POST)


        return render(request, 'thanks.html')
    
    return render(request, 'contact_form.html', {'property': property})


def contact_car_seller(request, pk):
    car = get_object_or_404(Car, pk=pk)
    
    if request.method == 'POST':
        form = ContactSellerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Save message
            ContactMessage.objects.create(
                seller=car.user,
                sender_name=name,
                sender_email=email,
                message=message
            )

            # Send email
            send_mail(
                subject=f"Car Enquiry from {name}",
                message=message,
                from_email=email,
                recipient_list=[car.user.email],
                fail_silently=False,
            )

            return render(request, 'thanks.html')

    else:
        form = ContactSellerForm()
    return render(request, 'contact_form.html', {'form': form, 'item': car})

def contact_job_advertiser(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    if request.method == 'POST':
        form = ContactSellerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Save message
            ContactMessage.objects.create(
                seller=job.user,
                sender_name=name,
                sender_email=email,
                message=message
            )

            # Send email
            send_mail(
                subject=f"Job Enquiry from {name}",
                message=message,
                from_email=email,
                recipient_list=[job.user.email],
                fail_silently=False,
            )

            return render(request, 'thanks.html')

    else:
        form = ContactSellerForm()
    return render(request, 'contact_form.html', {'form': form, 'item': job})

#NLP Parser
def parse_query(query):
    filters = {}

    # Price pattern: $500k, 20k, 150000
    price_match = re.search(r'\$?(\d+)(k)?', query.lower())
    if price_match:
        amount = int(price_match.group(1))
        if price_match.group(2) == 'k':
            amount *= 1000
        filters['max_price'] = amount

    # Property type/category keywords
    if 'rent' in query:
        filters['category'] = 'rent'
    elif 'sale' in query or 'buy' in query:
        filters['category'] = 'sale'
    
    # Example locations (you can expand this)
    location_keywords = ['borrowdale', 'avondale', 'harare', 'waterfalls']
    for loc in location_keywords:
        if loc in query.lower():
            filters['location__icontains'] = loc
            break

    return filters


WIT_AI_TOKEN = 'Bearer PXZKTJT2ZNPKIOSBGJVEZFOMK4UEBCAI'

@csrf_exempt
def chatbot_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    body = json.loads(request.body)
    user_message = body.get('message')

    response = requests.get(
        'https://api.wit.ai/message',
        headers={'Authorization': WIT_AI_TOKEN},
        params={'v': '20240728', 'q': user_message}
    )
    wit_response = response.json()

    print("\n------ WIT.AI RAW RESPONSE ------")
    print(json.dumps(wit_response, indent=2))
    print("---------------------------------\n")

    intents = wit_response.get('intents')
    entities = wit_response.get('entities', {})

    if not intents:
        return JsonResponse({'response': "Sorry, I didn't understand that."})

    intent_name = intents[0]['name']

    ### 1. FIND CAR ###
    if intent_name == 'find_car':
        car_make = car_model = location = None
        car_price = None
        

        for key, value in entities.items():
            if key.endswith(':car_make'):
                car_make = value[0].get('value')
            elif key.endswith(':car_model'):
                car_model = value[0].get('value')
            elif key.endswith(':location'):
                location = value[0].get('value')
            elif key.startswith('wit$amount_of_money'):
                car_price = value[0].get('value')
            

        cars = Car.objects.all()
        if car_make:
            cars = cars.filter(make__iexact=car_make)
        if car_model:
            cars = cars.filter(model__icontains=car_model)
        if location:
            cars = cars.filter(location__icontains=location)
        if car_price:
            try:
                cars = cars.filter(price__lte=float(car_price))
            except:
                pass

            

        if cars.exists():
            result = [str(car) for car in cars]
            return JsonResponse({'response': "Here are the cars I found: " + ", ".join(result)})
        return JsonResponse({'response': "Sorry, I couldn't find any cars matching your criteria."})

    ### 2. FIND JOB ###
    elif intent_name == 'find_job':
        job_title = location = None
        salary = None

        for key, value in entities.items():
            if key.endswith(':job_title'):
                job_title = value[0].get('value')
            elif key.endswith(':location'):
                location = value[0].get('value')
            elif key.startswith('wit$amount_of_money'):
                salary = value[0].get('value')

        jobs = Job.objects.all()
        if job_title:
            jobs = jobs.filter(title__icontains=job_title)
        if location:
            jobs = jobs.filter(location__icontains=location)
        if salary:
            try:
                jobs = jobs.filter(salary__gte=float(salary))
            except:
                pass

        if jobs.exists():
            result = [str(job) for job in jobs]
            return JsonResponse({'response': "Here are some job listings: " + ", ".join(result)})
        return JsonResponse({'response': "No jobs match that description."})

    ### 3. FIND PROPERTY ###
    elif intent_name == 'find_property':
        property_type = location = None
        price = None
        category = None

        for key, value in entities.items():
            if key.endswith(':property_type'):
                property_type = value[0].get('value')
            elif key.endswith(':location'):
                location = value[0].get('value')
            elif key.endswith('category'):
                category = value[0].get('value')
            elif key.startswith('wit$amount_of_money'):
                price = value[0].get('value')
            

        props = Property.objects.all()
        if property_type:
            props = props.filter(property_type__icontains=property_type)
        if location:
            props = props.filter(location__icontains=location)
        if category:
            props = props.filter(category__icontains=category)

        if price:
            try:
                props = props.filter(price__lte=float(price))
            except:
                pass

        if props.exists():
            result = [str(p) for p in props]
            return JsonResponse({'response': "Here are some properties I found: " + ", ".join(result)})
        return JsonResponse({'response': "No properties found for that search."})

    ### Unknown Intent ###
    return JsonResponse({'response': "Sorry, I didn't understand your request."})

def dashboard_home(request):
    return render(request, 'listings/home.html')










    
    




          







