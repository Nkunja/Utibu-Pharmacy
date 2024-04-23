from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Medication, Order,UserProfile
from django.core.exceptions import ObjectDoesNotExist
from .serializers import *
from rest_framework import generics
from .serializers import MedicationSerializer,UserLoginSerializer, UserProfileSerializer,OrderSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from django.db import transaction
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum  


def csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


def Index(request):
    return render(request, 'index.html')


@login_required(login_url='admin_login')
def Home(request):
    user = request.user
    medications = Medication.objects.all()
    orders = Order.objects.all()
    
    
    total_orders = orders.count()
    total_sales = orders.aggregate(total_sales=Sum('totalPrice'))['total_sales'] or 0
    patients_count = UserProfile.objects.filter(role='patient').count()
    
    
    # Serialize data
    medication_serializer = MedicationSerializer(medications, many=True)
    order_serializer = OrderSerializer(orders, many=True)
    
    # Pass data to template context
    context = {
        'medications': medications,
        'orders': orders,
        'user': user,
        'session': request.session.session_key,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_patients': patients_count
    }
    
    return render(request, 'home.html', context)

@login_required
@api_view(['GET'])
def homeApi(request):
    user = request.user
    medications = Medication.objects.all()
    orders = Order.objects.all()
    

    
    # Serialize data
    medication_serializer = MedicationSerializer(medications, many=True)
    order_serializer = OrderSerializer(orders, many=True)
    
    # Prepare response data
    data = {
        'medications': medication_serializer.data,
        'orders': order_serializer.data,
        'user': user.email,
        'session': request.session.session_key,
        
    }
    
    return Response(data)


@login_required
class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


@login_required
def PatientHome(request):
    user = request.user
    medication = medication.objects.all()
    return render(request, 'patient_home.html', {'user': user, 'medication': medication})

@login_required(login_url='admin_login')
def UsersView(request):
    users = UserProfile.objects.filter(role='patient')
    return render(request, 'users.html', {'users': users})

@login_required(login_url='admin_login')
def OrdersView(request):
    orders = Order.objects.all()
    return render(request, 'orders.html', {'orders': orders})

@login_required(login_url='admin_login')
def InvoicesView(request):
    invoices = Invoice.objects.all()
    return render(request, 'invoices.html', {'invoices': invoices})

@login_required
def MyInvoicesView(request):
    user = request.user  
    invoices = Invoice.objects.filter(user=user)  
    return render(request, 'invoices.html', {'invoices': invoices})

@login_required
def MyOrdersView(request):
    user = request.user  
    orders = Order.objects.filter(user=user)
    return render(request, 'orders.html', {'orders': orders})

def RegisterView(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            password = form.cleaned_data['password']

            user = UserProfile.objects.create_user(
                email=form.cleaned_data['email'],
                password=password,  
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role=form.cleaned_data['role'],
            )

            if user:
                return redirect('admin_login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

@api_view(['POST'])
def registerApi(request):
    if request.method == 'POST':
        serializer = PatientRegistrationSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    print(serializer.errors)


@login_required(login_url='admin_login')
def AddPatientView(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            password = form.cleaned_data['password']

            user = UserProfile.objects.create_user(
                email=form.cleaned_data['email'],
                password=password,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role=form.cleaned_data['role'],
            )

            if user:
                return redirect('login')
    else:
        form = PatientRegistrationForm()

    return render(request, 'patient_register.html', {'form': form})



def PatientRegisterView(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            if user:
                return redirect('users')  
    else:
        form = PatientRegistrationForm()

    return render(request, 'patient_register.html', {'form': form})



@api_view(['POST'])
def LoginView(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        # username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            # Check the user's role and redirect accordingly
            if user.role == 'admin':
                return Response({'redirect_url': '/api/admin/home/'}, status=status.HTTP_200_OK)
            else:
                return Response({'redirect_url': '/patient/home/'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def AdminLoginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Check the user's role and redirect accordingly
            if user.role == 'admin':
                return redirect('home')
            elif user.role == 'patient':
                return redirect('patient')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})



@login_required
@api_view(['GET'])
def user_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@login_required 
@api_view(['GET', 'POST'])
def medication_list(request):
    if request.method == 'GET':
        medications = Medication.objects.all()
        serializer = MedicationSerializer(medications, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = MedicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@login_required
@api_view(['GET', 'POST'])
def medication_details(request, medication_id):
    if request.method == 'GET':
        try:
            medication = Medication.objects.get(pk=medication_id)
            serializer = MedicationSerializer(medication)
            return Response(serializer.data)
        except Medication.DoesNotExist:
            return Response({"error": "Medication does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                medication_instance = Medication.objects.select_for_update().get(id=medication_id)
                
                # Get the quantity from the request body
                quantity = int(request.data.get('quantity', 0))
                totalPrice = request.data.get('totalPrice')
                
                if quantity <= medication_instance.quantity_available:
                    # Update the quantity available
                    medication_instance.quantity_available -= quantity
                    medication_instance.save()
                    
                    # Create the order
                    order = Order.objects.create(
                        medication=medication_instance,
                        user=request.user,
                        quantity=quantity, 
                        totalPrice=totalPrice
                    )
                    
                    total_amount = totalPrice
                    
                    # Create invoice
                    invoice = Invoice.objects.create(order=order, total_amount=total_amount)
                    invoice_serializer = InvoiceSerializer(invoice)

                    data = {
                        'order': OrderSerializer(order).data,
                        'invoice': invoice_serializer.data
                    }
                    
                    return Response(data, status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse({'error': 'Not enough quantity available'}, status=status.HTTP_400_BAD_REQUEST)
        except Medication.DoesNotExist:
            error_message = f"Medication with ID '{medication_id}' not found."
            return JsonResponse({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('Error:', e)  
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


        
@login_required
def MedicationsView(request):
    if request.method == 'GET':
        medications = Medication.objects.all()
        form = MedicationForm()
        return render(request, 'medications.html', {'medications': medications, 'form': form})
    elif request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('medication_list') 
        else:
            medications = Medication.objects.all()
            return render(request, 'medications.html', {'medications': medications, 'form': form})

@login_required
@api_view(['GET', 'POST'])
def order_list(request):
    if request.method == 'GET':
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return HttpResponse(serializer.data)
    elif request.method == 'POST':
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

def LogoutView(request):
    logout(request)
    return redirect('index')

class LogoutAPI(APIView):
    def get(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

    
@login_required
@api_view(['POST'])
def submit_orderApi(request):
    if request.method == 'POST':
        try:
            medication_id = request.data.get('medication')
            quantity = request.data.get('quantity') 

            if not medication_id or not quantity:
                raise ValueError("These fields are required")

            medication_instance = Medication.objects.get(id=medication_id)
            # save
            order = Order.objects.create(
                medication=medication_instance,
                user=request.user,
                quantity=quantity,
            )

            # Serialize the order instance
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            error_message = f"Medication with ID '{medication_id}' not found."
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@login_required(login_url='admin_login')
def add_medication(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home') 
    else:
        form = MedicationForm()
    return render(request, 'add_medication.html', {'form': form})


@login_required(login_url='admin_login')
def edit_medication(request, medication_id):
    # Retrieve the medication object to edit
    medication = get_object_or_404(Medication, pk=medication_id)
    
    if request.method == 'POST':
        form = MedicationForm(request.POST, request.FILES, instance=medication)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MedicationForm(instance=medication)
    
    return render(request, 'edit_medication.html', {'form': form})

@login_required(login_url='admin_login')
def delete_medication(request, medication_id):
    # Retrieve the medication object to delete
    medication = get_object_or_404(Medication, pk=medication_id)
    
    if request.method == 'POST':
        medication.delete()
        return redirect('home')
    
    return render(request, 'delete_medication.html', {'medication': medication})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)




@api_view(['GET'])
def generate_invoice_pdf(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        invoice = Invoice.objects.get(order=order)
        user = order.user

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'

        # Creating a PDF
        p = canvas.Canvas(response, pagesize=letter)

        # Add header
        p.drawString(100, 750, "Invoice")
        p.drawString(100, 730, f"Order Date: {invoice.date.strftime('%Y-%m-%d %H:%M:%S')}")
        p.drawString(100, 710, f"Customer Name: {user.first_name} {user.last_name}")
        p.drawString(100, 690, f"Amount: Ksh {invoice.total_amount}")

        # Add table with order details
        table_data = [
            ["Item Name", "Quantity", "Unit Price", "Total Amount"],
        ]
        order_items = Order.objects.filter(id=order_id)
        for item in order_items:
            medication = item.medication
            table_data.append([
                medication.name,
                str(item.quantity),
                f"Ksh {medication.price}",
                f"Ksh {item.totalPrice}"
            ])

        table = Table(table_data, colWidths=[200, 100, 100, 100], hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), 'gray'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, 'black'),
            ('BOX', (0, 0), (-1, -1), 0.25, 'black'),
        ]))

        table.wrapOn(p, 0, 0)
        table.drawOn(p, 100, 650)

        p.showPage()
        p.save()

        return response
    except Order.DoesNotExist:
        return Response({"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)
    except Invoice.DoesNotExist:
        return Response({"error": "Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


