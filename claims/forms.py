from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

from claims.utils import fetch_hospital_list
from .models import Claim, ClaimContractDocument, UserProfile


class CustomUserCreationForm(UserCreationForm):
    imid = forms.CharField(
        max_length=50,
        required=True,
        label="IMID",
        help_text="Enter your unique Insurance Member ID."
    )

    phone_number = forms.CharField(
        max_length=20,
        required=True,
        label="Phone Number",
        help_text="Enter your phone number."
    )

    def clean_imid(self):
        imid = self.cleaned_data.get('imid')
        if UserProfile.objects.filter(imid=imid).exists():
            raise ValidationError("This IMID is already registered.")
        return imid

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'imid', 'phone_number']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UserCreationForm.Meta.model
        fields = UserCreationForm.Meta.fields + ('email',)

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username_or_email = self.cleaned_data.get('username_or_email')
        password = self.cleaned_data.get('password')

        if not username_or_email or not password:
            raise ValidationError("Both fields are required.")

        user = None
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                username = user_obj.get_username()
                user = authenticate(username=username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(username=username_or_email, password=password)

        if user is None:
            raise ValidationError("Invalid credentials.")
        if not user.is_active:
            raise ValidationError("This account is inactive.")

        self.user_cache = user
        return self.cleaned_data

    def get_user(self):
        return self.user_cache

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'timezone'] # timezone ফিল্ড যোগ করুন

class ClaimSubmissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set choices for hospital_clinic_provider_name
        self.fields['hospital_clinic_provider_name'].choices = fetch_hospital_list()
        
    class Meta:
        model = Claim
        fields = ['description', 'incident_date', 'location', 'total_claim_amount', 'admission_date', 'hospital_clinic_provider_name', 'claim_type', 'consultation', 'medication', 'others']
        widgets = {

            'claim_type': forms.RadioSelect(attrs={
                'class': 'form-check-input',  # form-check-inline যোগ করা হয়েছে
            }),

            'admission_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),

            'incident_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),

            'hospital_clinic_provider_name': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the name of the hospital/clinic/provider'
            }),

            'consultation': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Consultation amount (TK)'
            }),

            'medication': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medication amount (TK)'
            }),

            'others': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Other expenses (TK)'
            }),

            'total_claim_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Claim amount',
                'value': 0,  # ডিফল্ট মান 0 সেট করা হয়েছে
                'disabled': 'disabled'  # এই ফিল্ডটি অক্ষম করা হয়েছে
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter a detailed description'
            }),

            # 'medical_record': forms.FileInput(attrs={
            #     'class': 'form-control'
            # }),

            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the location of the incident'
            }),
        }


class ClaimContractDocumentSubmissionForm(forms.ModelForm):        
    class Meta:
        model = ClaimContractDocument
        fields = ['document_name', 'contract_documents']
        widgets = {
            'document_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'placeholder': 'Enter the Contract document name'
            }),

            'contract_documents': forms.FileInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'placeholder': 'Upload the contract document'
            }),
        }