import requests

ID = "326db938-e220-4eba-8a0a-1c9deb20e205"
#326db938-e220-4eba-8a0a-1c9deb20e205
#879c2191-04b0-41ca-aa4d-91e2a3dcd942
POST = f"prediction/{ID}"
DEL = f"chatmessage/{ID}"
API = "http://localhost:3000/api/v1/"
KEY = "QLEJv8OJ_m-HlRopIdOgXsndISN8rc7j4qZNGwQjciY"

def post_(payload):
    try:
        response = requests.post(
            f"{API}{POST}",
            headers={"Authorization": f"Bearer {KEY}"},
            json=payload
        )
        response.raise_for_status()  # Lanza excepción para códigos de estado HTTP >= 400
        return response.json().get('text', None)
    except requests.ConnectionError:
        print("Error: No se pudo conectar con la API.")
        return None
    except requests.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        return None
    except Exception as err:
        print(f"Error inesperado: {err}")
        return None

def delete_():
    try:
        response = requests.delete(
            f"{API}{DEL}",
            headers={"Authorization": f"Bearer {KEY}"}
        )
        response.raise_for_status()  # Lanza excepción para códigos de estado HTTP >= 400
        return response.json()
    except requests.ConnectionError:
        print("Error: No se pudo conectar con la API.")
        return None
    except requests.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        return None
    except Exception as err:
        print(f"Error inesperado: {err}")
        return None