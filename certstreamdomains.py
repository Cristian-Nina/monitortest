import certstream
import datetime

def print_callback(message, context):
    # Ignora los mensajes de "heartbeat"
    if message['message_type'] == "heartbeat":
        return

    # Procesamos los mensajes de actualización de certificados
    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']
        timestamp = datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')

        if all_domains:
            domain = all_domains[0]  # Dominio principal
            san_domains = ", ".join(all_domains[1:])  # Otros dominios SAN

            # Excluimos dominios que comienzan con '*' o '.'
            if not (domain.startswith('*') or domain.startswith('.')):
                with open('domains.txt', 'a') as f:
                    f.write(f"{domain}\n")
                print(f"[{timestamp}] Dominio guardado: {domain} (SAN: {san_domains})")
        else:
            print(f"[{timestamp}] Dominio: NULL")

def main():
    print("Conectando a Certstream...")
    certstream.listen_for_events(print_callback, url='wss://certstream.calidog.io/')
    print("Escuchando dominios en tiempo real...")

if __name__ == "__main__":
    main()
