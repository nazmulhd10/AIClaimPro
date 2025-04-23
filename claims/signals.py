import os
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from claims.services.RAG.vector_service import generate_and_save_vector
from .models import Claim, ClaimContractDocument

@receiver(pre_delete, sender=Claim)
def delete_claim_related_files(sender, instance, **kwargs):
    for doc in instance.documents.all():
        try:
            os.remove(doc.document.path)
        except FileNotFoundError:
            pass

@receiver(pre_delete, sender=ClaimContractDocument)
def delete_contract_doc_files(sender, instance, **kwargs):
    if instance.contract_documents:
        try:
            os.remove(instance.contract_documents.path)
        except FileNotFoundError:
            pass
        # build_initial_vector_store()  # Use this only if necessary (e.g., via a management command)

@receiver(post_save, sender=ClaimContractDocument)
def create_vector_on_upload(sender, instance, created, **kwargs):
    if created and instance.contract_documents:
        generate_and_save_vector(instance)
        # build_initial_vector_store()  # Optional; avoid if generate_and_save_vector is enough
