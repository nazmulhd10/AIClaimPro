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