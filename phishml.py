import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from urllib.parse import urlparse
import certstream
import threading
import re
import numpy as np

# Cargar datos desde el archivo CSV para entrenar el modelo
df = pd.read_csv('phishingdataset.csv')

# Seleccionar características relevantes
feature_columns = [
    'length',  # Longitud de la URL
]

# Asegúrate de que las etiquetas sean adecuadas
y = df['label']  # Asegúrate de que 'label' esté definido en tu dataset

# Entrenar el modelo con las características seleccionadas
X = df[feature_columns]
model = DecisionTreeClassifier()
model.fit(X, y)

# Función para extraer características de una URL
def extract_features(url):
    parsed_url = urlparse(url)
    features = {
        'length': len(url),
    }
    return features

# Función para analizar un dominio
def analyze_domain(domain):
    # Características adicionales a evaluar
    suspicious_keywords = ['beneficio', 'acceso', 'login', 'cbc', 'accessbanking', 'incio']
    has_suspicious_keyword = any(keyword in domain for keyword in suspicious_keywords)
    
    # Análisis de caracteres repetidos
    has_repeated_chars = bool(re.search(r'(.)\1{2,}', domain))  # Busca 3 o más caracteres iguales consecutivos

    # Proporción de caracteres alfanuméricos
    alphanumeric_chars = re.sub(r'[^a-zA-Z0-9]', '', domain)
    alpha_numeric_ratio = len(alphanumeric_chars) / len(domain) if len(domain) > 0 else 0

    # Longitud del dominio y del TLD
    domain_parts = domain.split('.')
    domain_length = len(domain_parts[0])  # Longitud del nombre del dominio
    tld_length = len(domain_parts[-1]) if len(domain_parts) > 1 else 0  # Longitud del TLD

    # Devuelve características adicionales
    return {
        'has_suspicious_keyword': has_suspicious_keyword,
        'has_repeated_chars': has_repeated_chars,
        'alpha_numeric_ratio': alpha_numeric_ratio,
        'domain_length': domain_length,
        'tld_length': tld_length
    }

# Función para analizar una URL y predecir si es phishing
def analyze_url(url):
    features = extract_features(url)
    domain_features = analyze_domain(urlparse(url).netloc)

    # Combinar características
    features.update(domain_features)

    # Convertir a DataFrame para hacer la predicción
    features_df = pd.DataFrame([features])
    
    # Hacer la predicción
    prediction = model.predict(features_df[['length']])[0]

    # Evaluar el resultado de la predicción
    result = 'Phishing' if prediction == 1 else 'Legítima'
    print(f'{url}: {result}')

    # Guardar URL phishing en un archivo
    if result == 'Phishing':
        with open('phishing_urls.txt', 'a') as f:
            f.write(url + '\n')

# Función para manejar las actualizaciones de CertStream
def certstream_handler(msg, client):
    if 'data' in msg and 'leaf_cert' in msg['data']:
        leaf_cert = msg['data']['leaf_cert']
        if 'all_domains' in leaf_cert:
            for domain in leaf_cert['all_domains']:
                analyze_url(domain)

# Conectar a CertStream
def run_certstream():
    certstream.listen_for_events(certstream_handler, url='wss://certstream.calidog.io')

# Iniciar CertStream en un hilo
certstream_thread = threading.Thread(target=run_certstream)
certstream_thread.start()

print("Escuchando certificados emitidos en tiempo real...")

# Mantener el programa en ejecución
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Deteniendo el programa...")
