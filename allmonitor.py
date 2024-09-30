import certstream
import datetime
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Lista de palabras clave
keywords = ["icbc","access banking"]

# Función para obtener el título de una página
def get_title(url, timeout=10):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "La etiqueta <title> está vacía."
        return url, title
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return url, None

# Callback de Certstream
def print_callback(message, executor, result_file):
    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']
        timestamp = datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')

        if all_domains:
            domain = all_domains[0]
            san_domains = ", ".join(all_domains[1:])

            if not (domain.startswith('*') or domain.startswith('.')):
                print(f"[{timestamp}] Dominio guardado: {domain} (SAN: {san_domains})")
                future = executor.submit(get_title, f"http://{domain}")
                future.add_done_callback(lambda f: process_result(f, result_file, domain))

def process_result(future, result_file, domain):
    url, title = future.result()
    
    if title and isinstance(title, str) and title != "La etiqueta <title> está vacía.":
        print(f"🎉 Título de {url}: {title}")
        if any(keyword.lower() in title.lower() for keyword in keywords):
            result_file.write(f"{url} - {title}\n")
            print(f"✅ Guardado: {url} - {title}")
    else:
        print(f"❌ No se encontró título en {domain} o hubo un error.")

def main():
    with open('resultados.txt', 'a') as result_file:
        print("Conectando a Certstream...")
        with ThreadPoolExecutor(max_workers=80) as executor:
            certstream.listen_for_events(lambda msg, ctx: print_callback(msg, executor, result_file), url='wss://certstream.calidog.io/')
            print("Escuchando dominios en tiempo real...")

if __name__ == "__main__":
    main()
