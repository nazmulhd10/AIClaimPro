import json
import traceback
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import requests

from claims.models import Claim, ClaimContractDocument, ClaimDocument, UserProfile
# from claims.services.chatbot_engine import get_response_from_query
# from claims.services.chatbot_engine import get_response_from_query
from claims.services.RAG.chat_service import create_qa_chain, get_answer
from claims.services.RAG.init_embeddings import build_initial_vector_store
from claims.services.ask_service import get_answer_from_query
from claims.services.claim_processor import ClaimProcessor
from claims.utils import fetch_member_info_by_memberId
from .forms import ClaimContractDocumentSubmissionForm, ClaimSubmissionForm, CustomUserCreationForm, LoginForm, RegistrationForm, UserProfileForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


def verify_imid(request):
    """Verify IMID via API call."""
    if request.method == "POST":
        org_id = request.POST.get("org_id")
        offset = request.POST.get("offset")
        limit = request.POST.get("limit")
        mem_id = request.POST.get("mem_id")

        # Call the utility function
        result = fetch_member_info_by_memberId(org_id, offset, limit, mem_id)
        return JsonResponse(result, safe=False)  # Return the API response as JSON

    return JsonResponse({"error": "Invalid request method"}, status=400)


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user but don't commit yet
            user = form.save(commit=False)
            user.save()  # Save User model

            # Create UserProfile and assign fields
            imid = form.cleaned_data.get('imid')
            phone_number = form.cleaned_data.get('phone_number')  # যদি form এ থাকে

            UserProfile.objects.create(
                user=user,
                imid=imid,
                phone_number=phone_number
            )

            return redirect('login')  # Redirect after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'claims/register.html', {'form': form})

# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('dashboard')
#     else:
#         form = RegistrationForm()
#     return render(request, 'claims/register.html', {'form': form})

@login_required
def dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()
    claims = Claim.objects.filter(user=request.user).order_by('-submission_date')
    return render(request, 'claims/dashboard.html', {'user_profile': user_profile, 'claims': claims})

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

@login_required
def profile_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()
    return render(request, 'claims/profile.html', {'user_profile': user_profile})

@login_required
def profile_edit(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'claims/profile_edit.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'claims/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def submit_claim(request):
    if request.method == 'POST':
        form = ClaimSubmissionForm(request.POST, request.FILES)
        files = request.FILES.getlist('file[]')  # মাল্টিপল ফাইল হ্যান্ডল করা হচ্ছে
        print("Result is", files)

        if form.is_valid():
            try:
                # Step 1: Save the claim
                claim = form.save(commit=False)
                claim.user = request.user
                claim.save()

                # Step 2: Save all documents
                documents = []
                for file in files:
                    # Step 1: Save the document properly
                    doc = ClaimDocument.objects.create(claim=claim, document=file)
                    documents.append(doc)

                    # Step 3: Initialize the processor with ClaimDocument instance
                    processor = ClaimProcessor(claim=claim, document_instances=documents)

                    # Step 4: Process all documents together
                    try:
                        processor.process_all()
                        print(f"✅ Successfully processed: {doc.document.name}")
                    except Exception as e:
                        print(f"❌ Error processing {doc.document.name}: {e}")

                return redirect('claim_submitted_success')
            except Exception as e:
                print("💥 Exception occurred while saving claim:", e)
                traceback.print_exc()
        else:
            print("❌ Form invalid:", form.errors)
    else:
        form = ClaimSubmissionForm()

    return render(request, 'claims/submit_claim.html', {'form': form})

@login_required
def view_claim(request, claim_id):
    claim = get_object_or_404(Claim, claim_id=claim_id, user=request.user)
    return render(request, 'claims/view_claim.html', {'claim': claim})

@login_required
def claim_submitted_success(request):
    return render(request, 'claims/claim_submitted_success.html')

@login_required
def claim_history(request):
    claims = Claim.objects.filter(user=request.user).order_by('-submission_date')
    return render(request, 'claims/claim_history.html', {'claims': claims})

@login_required
def eligibility_validation(request):
    # claims = Claim.objects.filter(user=request.user).order_by('-submission_date')
    # return render(request, 'claims/eligibility_validation.html', {'claims': claims})
    claims = Claim.objects.filter(user=request.user).order_by('-submission_date')
    return render(request, 'claims/eligibility_validation.html', {'claims': claims})
    # return render(request, 'claims/eligibility_validation.html')

@login_required
def submit_claim_contract_documents(request):
    if request.method == 'POST':
        form = ClaimContractDocumentSubmissionForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Save the contract document
                contract_document = form.save(commit=False)
                contract_document.user = request.user
                contract_document.save()

                # ✅ Webhook Call Start
                webhook_url = "http://localhost:5678/webhook-test/83483438-c3a0-4a35-ba55-5f9b38ead927"

                # Fetch file information from the uploaded file in request.FILES
                uploaded_file = request.FILES['contract_documents']
                
                upload_image = [
                    {
                        'filename': uploaded_file.name,  # File name from request.FILES
                        'mimetype': uploaded_file.content_type,  # MIME type from request.FILES
                        'size': uploaded_file.size  # Size from request.FILES
                    }
                ]
                # print("Upload Image:", upload_image[0]['mimetype'])


                # Prepare the data to send to the webhook
                data = {
                    'Upload_Image': upload_image,  # Include file information
                    # 'submittedAt': form.cleaned_data['submittedAt'],  # Add the submission time
                    'formMode': 'test',  # Keep form mode as test
                    'mimeType': uploaded_file.content_type,  # MIME type from request.FILES
                    'document_name': form.cleaned_data['document_name'],  # Document name from the form
                }


                # Combine JSON and file into multipart form-data
                # multipart_data = {
                #     'json_data': (None, json.dumps(data), 'application/json'),
                #     'contract_documents': (uploaded_file.name, uploaded_file, uploaded_file.content_type)
                # }

                # Define 'files' dictionary to send the file
                files = {
                    'contract_documents': (
                        uploaded_file.name,                     # ফাইলের নাম
                        uploaded_file.file,                     # ফাইলের বাইনারি কন্টেন্ট (InMemoryUploadedFile or TemporaryUploadedFile)
                        uploaded_file.content_type              # MIME টাইপ (যেমন 'application/pdf')
                    )
                }


                try:
                    # Send the data and file in the webhook request
                    response = requests.post(webhook_url, data=data, files=files)
                    # response = requests.post(
                    #     webhook_url,
                    #     data=json.dumps(data),  # JSON স্ট্রিং আকারে পাঠাতে হবে
                    #     headers={'Content-Type': 'application/json'},
                    #     files=files
                    # )
                    print("✅ Webhook Response:", response.status_code, response.text)
                except Exception as we:
                    print("🚨 Webhook call failed:", we)
                # Webhook Call End

                # Redirect to the same page after successful submission
                return redirect('submit_claim_contract_documents')  # Page reload with fresh data
            except Exception as e:
                print("💥 Exception occurred while saving contract document:", e)
        else:
            print("❌ Form invalid:", form.errors)
    else:
        form = ClaimContractDocumentSubmissionForm()

    # 🔥 Always load user-specific submitted data
    ClaimContractDocuments = ClaimContractDocument.objects.filter(user=request.user).order_by('-submission_date')

    return render(
        request,
        'claims/submit_claim_contract_document.html',
        {
            'form': form,
            'ClaimContractDocuments': ClaimContractDocuments  # Always sent to template
        }
    )


@csrf_exempt
def chat(request):
    if request.method == "POST":
        global qa_chain
        query = request.POST.get("message")
        if not query:
            return JsonResponse({"response": "Empty prompt."})
        if not qa_chain:
            return JsonResponse({"response": "QA Chain not initialized."})
        answer = get_answer(query, qa_chain)
        return JsonResponse({"response": answer})
    return render(request, "claims/chat.html")


# vector_store = build_initial_vector_store()
# qa_chain = create_qa_chain(vector_store)

# @csrf_exempt
# def chat(request):
#     if request.method == "POST":
#         query = request.POST.get("message")
#         if not query:
#             return JsonResponse({"response": "Empty prompt."})
#         answer = get_answer(query, qa_chain)
#         return JsonResponse({"response": answer})
#     return render(request, "claims/chat.html")

vector_store = None
qa_chain = None

@csrf_exempt
def initialize_vector_store(request):
    global vector_store, qa_chain
    if request.method == "POST":
        try:
            vector_store = build_initial_vector_store()
            qa_chain = create_qa_chain(vector_store)
            return JsonResponse({"status": "success", "message": "The AI model's intelligence has been successfully updated and optimized."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "invalid", "message": "Only POST allowed."})

# def chatbot_view(request):
#     if request.method == "POST":
#         user_query = request.POST.get("query")
#         if user_query:
#             result = get_answer_from_query(user_query)
#             print("RAG Result:", result)  # এই লাইনটি যোগ করুন
#             return JsonResponse({
#                 "answer": result["answer"],
#                 "documents": result["documents"],
#                 "metadatas": result["metadatas"]
#             })
#     return render(request, "claims/chat.html")


# @login_required
# def claim_contract_document_list(request):
#     ClaimContractDocument = ClaimContractDocument.objects.filter(user=request.user).order_by('-submission_date')
#     return render(request, 'claims/submit_claim_contract_document.html', {'ClaimContractDocuments': ClaimContractDocument})

@csrf_exempt
def receive_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("📥 Received data:", data)

            # Data processing logic here

            return JsonResponse({"message": "Data received successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)