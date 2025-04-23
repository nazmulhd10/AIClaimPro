from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Claim, ClaimContractDocument, UserProfile

# Inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

# Extend the default UserAdmin
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'get_phone_number', 'get_imid', 'is_staff', 'is_active'
    )

    def get_phone_number(self, obj):
        return obj.userprofile.phone_number
    get_phone_number.short_description = 'Phone Number'

    def get_imid(self, obj):
        return obj.userprofile.imid
    get_imid.short_description = 'IMID'


# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_id', 'user', 'submission_date', 'incident_date', 'total_claim_amount', 'is_fraudulent')
    list_filter = ('user', 'submission_date', 'incident_date', 'is_fraudulent')
    search_fields = ('claim_id', 'description', 'user__username')
    date_hierarchy = 'submission_date'
    ordering = ('-submission_date',)
    readonly_fields = ('claim_id', 'submission_date', 'fraud_score')  # এই ফিল্ডগুলো এডিট করা যাবে না

@admin.register(ClaimContractDocument)
class ClaimContractDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'claim_contract_document_id', 'submission_date', 'document_name', 'contract_documents')
    search_fields = ('document_name', 'claim_contract_document_id', 'submission_date')