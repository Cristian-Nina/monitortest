import certstream
import datetime
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Lista de palabras clave a buscar en el HTTP title
keywords = ['icbc', 'access banking']

def fetch_title(domain):
    """Intenta obtener el título HTTP de un dominio."""
    # Limpiar el dominio eliminando el asterisco
    domain = domain.replace('*', '').strip()
    
    for scheme in ['http', 'https']:
        try:
            response = requests.get(f"{scheme}://{domain}", timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.title.string.strip() if soup.title else 'No Title'
            else:
                print(f"[{datetime.datetime.now()}] Error al acceder a {domain}: Código de estado {response.status_code}")
        except requests.RequestException as e:
            print(f"[{datetime.datetime.now()}] Error al acceder a {domain}: {e}")
    return None

def print_callback(message, context):
    """Callback para manejar mensajes de Certstream."""
    if message['message_type'] != "certificate_update":
        return

    all_domains = message['data']['leaf_cert']['all_domains']
    if all_domains:
        # Limpiar los dominios antes de usarlos
        for domain in all_domains:
            title = fetch_title(domain)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if title:
                formatted_output = f"{timestamp} - Dominio: {domain}, Title: {title}"
                print(formatted_output)
                if any(keyword in title.lower() for keyword in keywords):
                    with open('results.txt', 'a') as f:
                        f.write(f"{domain}\n")
            else:
                print(f"[{timestamp}] No se pudo obtener el título para: {domain}")

def main():
    """Función principal para iniciar la escucha de Certstream."""
    print("Conectando a Certstream...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        certstream.listen_for_events(print_callback, url='wss://certstream.calidog.io/')
        print("Escuchando dominios en tiempo real...")

if __name__ == "__main__":
    main()
