import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Lista de palabras clave
keywords = [
    "ción"  # Añade tus palabras clave aquí
]

# Función para obtener el título de una página
def get_title(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)  # Timeout de 10 segundos
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "La etiqueta <title> está vacía."
        return url, title
    except requests.exceptions.RequestException:
        return url, None  # Retorna None si hay un error

# Función principal
def main():
    # Cargar las URLs desde el archivo domains.txt
    with open('domains.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    # Abrir el archivo para guardar resultados
    with open('resultados.txt', 'a') as result_file:
        # Usar ThreadPoolExecutor para realizar solicitudes en paralelo
        max_workers = 80  # Ajusta según tu entorno
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(get_title, f"http://{url}"): url for url in urls}
            
            for future in as_completed(future_to_url):
                url, title = future.result()
                
                if title and isinstance(title, str) and title != "La etiqueta <title> está vacía.":
                    print(f"🎉 Título de {url}: {title}")
                    # Verificar si el título contiene alguna palabra clave
                    if any(keyword.lower() in title.lower() for keyword in keywords):
                        result_file.write(f"{url} - {title}\n")  # Guardar solo si hay coincidencia
                        print(f"✅ Guardado: {url} - {title}")
                else:
                    print(f"❌ No se encontró título en {url} o hubo un error.")

if __name__ == '__main__':
    main()
