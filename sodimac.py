import requests

print('se incia desde el bot')

url = 'https://pamoback-nexuspamo.up.railway.app/products/set_inventory_sodimac'
response = requests.get(url)

if response.status_code == 200:
    print(f"Solicitud GET exitosa: {response.text}")

else:
    print(f"Error al enviar solicitud GET: {response.status_code}")