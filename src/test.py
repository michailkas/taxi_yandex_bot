import requests

url = "https://cchgeu.ru"

try:
    response = requests.get(url, timeout=10)  # Adjust the timeout value as needed
    response.raise_for_status()  # Raise an exception for bad responses (4xx and 5xx)
    print(response.text)
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
