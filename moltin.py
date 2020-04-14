import requests


def get_oauth_access_token(client_id, client_secret):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token


def get_products(token, product_id=None):
    
    headers = {'Authorization': f'Bearer {token}'}
    if product_id:
        url = f'https://api.moltin.com/v2/products/{product_id}'
    else:
        url = 'https://api.moltin.com/v2/products'
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def add_product_to_cart(token, user_id, product_id, quantity):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": quantity
        }
    }

    url = f'https://api.moltin.com/v2/carts/{user_id}/items'
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['data']


def get_a_cart(token, user_id):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.moltin.com/v2/carts/{user_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_image_url(token, image_id):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.moltin.com/v2/files/{image_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']
