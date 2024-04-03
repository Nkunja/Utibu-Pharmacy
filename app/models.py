from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group



class UserProfileManager(BaseUserManager):
    def create_user(self, email, password=None, role='patient', **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)

        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Assign user to appropriate group based on role
        if role == 'admin':
            admin_group, created = Group.objects.get_or_create(name='Admins')
            user.groups.add(admin_group)
        else:
            patient_group, created = Group.objects.get_or_create(name='Patients')
            user.groups.add(patient_group)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, role='admin', **extra_fields)

    def assign_role(self, user, role):
        """
        Assigns a role to a user profile.
        """
        user.role = role
        user.save(using=self._db)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True,default='patient')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=100, default='patient')  
    id_no = models.CharField(max_length=8, null=True)
    designation = models.CharField(max_length=50, null=True)
    profile_pic = models.ImageField(upload_to='images/', null=True)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
   
    

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


# class Category(models.Model):
#     name = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.name

# class Medication(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     quantity_available = models.PositiveIntegerField(default=0)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name
class Medication(models.Model):
    CATEGORY_CHOICES = [
        ('BP', 'Blood Pressure'),
        ('HIV', 'HIV/AIDS'),
        ('DIABETES', 'Diabetes'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name



class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order for {self.quantity} {self.medication.name} by {self.user.email}"
    



class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for Order ID: {self.order.id}"


class Payment(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Invoice ID: {self.invoice.id}"
