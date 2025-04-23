import os
import uuid
from django.db import models
from django.contrib.auth.models import User
import pytz

from claims.utils import fetch_hospital_list

class Claim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    submission_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)  # এটা করলে required থাকবেনা
    # medical_record = models.FileField(upload_to='medical_records/', blank=True, null=True)
    incident_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    # amount_claimed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fraud_score = models.FloatField(blank=True, null=True) # ফ্রড ডিটেকশনের জন্য স্কোর
    is_fraudulent = models.BooleanField(default=False) # জালিয়াতিপূর্ণ কিনা

    # new fields for future use
    admission_date = models.DateTimeField(blank=True, null=True)

    # New fields
    CLAIM_TYPE_CHOICES = [
        ('IPD', 'IPD'),
        ('OPD', 'OPD'),
        ('Dental', 'Dental'),
        ('Eye', 'Eye'),
        ('Maternity', 'Maternity'),
    ]

    claim_type = models.CharField(max_length=20, choices=CLAIM_TYPE_CHOICES, default='IPD')  # Claim Type (Radio Button)
    consultation = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Consultation Amount
    medication = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Medication Amount
    others = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Other Expenses
    total_claim_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Total Claim Amount (Read-only)
    hospital_clinic_provider_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default=None
    )

    def __str__(self):
        return f"Claim ID: {self.claim_id} by {self.user.username}"

    def save(self, *args, **kwargs):
        # Automatically calculate total claim amount before saving
        self.total_claim_amount = (self.consultation or 0) + (self.medication or 0) + (self.others or 0)
        if not self.claim_id:
            self.claim_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

class ClaimDocument(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='claim_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for Claim ID: {self.claim.claim_id}"

    def delete(self, *args, **kwargs):
        # ফাইল সিস্টেম থেকে ফাইল ডিলিট করো
        if self.document and os.path.isfile(self.document.path):
            os.remove(self.document.path)
        super().delete(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.all_timezones],
        blank=True,
        default='UTC'
    )
    imid = models.CharField(max_length=50, unique=True, blank=False)  # IMID (Insurance Member ID)
    # ভবিষ্যতে আরো ফিল্ড যোগ করা হবে (যেমন medical_history, preferences ইত্যাদি)

    def __str__(self):
        return f"Profile of {self.user.username}"
    

class ClaimContractDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim_contract_document_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    submission_date = models.DateTimeField(auto_now_add=True)
    document_name = models.CharField(max_length=255, blank=True)
    contract_documents = models.FileField(upload_to='contract_documents/', blank=True, null=True)

    def __str__(self):
        return f"Claim Contract ID: {self.claim_contract_document_id} by {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.claim_contract_document_id:
            self.claim_contract_document_id = str(uuid.uuid4())
        super().save(*args, **kwargs)