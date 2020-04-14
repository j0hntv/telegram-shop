import requests


def get_products(token):
    headers = {'Authorization': f'Bearer {token}'}
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


def get_a_cart():
    pass
