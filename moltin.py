import requests


def get_oauth_access_token(db, client_id, client_secret, expires=3000):
    access_token = db.get('moltin_token')

    if access_token:
        return access_token

    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    access_token = response.json()['access_token']
    db.set('moltin_token', access_token, ex=expires)
    return access_token


def get_products(token, product_id=None):
    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://api.moltin.com/v2/products/'

    if product_id:
        url += product_id
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def add_product_to_cart(token, cart, product_id, quantity):
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

    url = f'https://api.moltin.com/v2/carts/{cart}/items'
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['data']


def get_a_cart(token, cart):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.moltin.com/v2/carts/{cart}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_cart_items(token, cart):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.moltin.com/v2/carts/{cart}/items'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def remove_cart_item(token, cart, product_id):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.moltin.com/v2/carts/{cart}/items/{product_id}'
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_formatted_cart_items(cart, cart_items):
    items = []
    for item in cart_items:
        name = item['name']
        description = item['description']
        quantity = item['quantity']
        cost = item['meta']['display_price']['with_tax']['value']['formatted']
        items.append(f'{name}: *{quantity}* шт.\n_{description}_\n*{cost}*')

    total_cost = cart['meta']['display_price']['with_tax']['formatted']
    items.append(f'\nИтого: *{total_cost}*')

    return '\n\n'.join(items)


def get_image_url(token, image_id):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.moltin.com/v2/files/{image_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


def get_product_markdown_output(product):
    name = product['name']
    description = product['description']
    weight = product['weight']['kg']
    price = product['meta']['display_price']['with_tax']['formatted']
    output = f'*{name}*\n_{description}_\n{weight} kg\n\n*{price}*'
    return output


def create_customer(token, name, email, customer_type='customer'):
    url = 'https://api.moltin.com/v2/customers'
    headers = {'Authorization': f'Bearer {token}'}
    payload = {
        "data": {
            "name": name,
            "email": email,
            "type": customer_type
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
