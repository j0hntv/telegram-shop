import requests


def get_products(token):
    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://api.moltin.com/v2/products'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']

def add_product_to_cart():
    pass

def get_a_cart():
    pass
