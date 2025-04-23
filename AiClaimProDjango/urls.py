from django.contrib import admin
from django.urls import path
from claims import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('submit_claim/', views.submit_claim, name='submit_claim'),
    path('submit_claim_contract_document/', views.submit_claim_contract_documents, name='submit_claim'),
    path('claim_submitted_success/', views.claim_submitted_success, name='claim_submitted_success'),
    path('claim_history/', views.claim_history, name='claim_history'),
    path('claim/<str:claim_id>/', views.view_claim, name='view_claim'), # নতুন URL প্যাটার্ন
    # path("chat/", views.chat_view, name="chat"),
    # path("chat/", views.chatbot_view, name="chatbot"),
    path('chat/', views.chat, name='chatbot'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)