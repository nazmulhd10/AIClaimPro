import requests
from django.core.cache import cache
import json

def fetch_hospital_list():
    cache_key = "hospital_list"
    hospital_list = cache.get(cache_key)

    if not hospital_list:
        try:
            response = requests.post('https://ai-eccs.pragatilife.com/api/v1/hospital-list')
            response.raise_for_status()
            # data = response.json()
            # Assuming the API returns a list of hospitals in the format: [{"id": "Apollo", "name": "Apollo Hospital"}, ...]
            hospital_list = response.json()
            # print("API Data is:", hospital_list)
            cache.set(cache_key, hospital_list, timeout=3600)  # Cache for 1 hour
        except requests.exceptions.RequestException as e:
            print(f"Error fetching hospital list: {e}")
            # Default hospital list if API call fails
            hospital_list = [
                ('Apollo', 'Apollo Hospital'),
                ('Fortis', 'Fortis Hospital'),
                ('AIIMS', 'AIIMS'),
                ('CMC', 'Christian Medical College'),
                ('Other', 'Other'),
            ]

    return hospital_list


def fetch_member_info_by_memberId(org_id, offset, limit, mem_id):
    """Fetch member information by member ID."""
    url = "https://ai-eccs.pragatilife.com/api/v1/hi-members"  # Replace with your actual API URL
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "org_id": org_id,
        "offset": offset,
        "limit": limit,
        "mem_id": mem_id,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        print("API Response is:", response.json())
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
# def fetch_member_info_by_memberId():
#     cache_key = "member_list"
#     member_list = cache.get(cache_key)

#     if not member_list:
#         try:
#             response = requests.post('https://ai-eccs.pragatilife.com/api/v1/hi-members')
#             response.raise_for_status()
#             # data = response.json()
#             # Assuming the API returns a list of hospitals in the format: [{"id": "Apollo", "name": "Apollo Hospital"}, ...]
#             member_list = response.json()
#             # print("API Data is:", member_list)
#             cache.set(cache_key, member_list, timeout=3600)  # Cache for 1 hour
#         except requests.exceptions.RequestException as e:
#             print(f"Error fetching hospital list: {e}")
#             # Default list if API call fails

#     return member_list