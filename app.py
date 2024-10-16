import logging
import sys
import datetime
import certstream

def print_callback(message, context):
    include = ["Icbc","icbc", "lcbc", "icdc", "lcdc", "Icdc", "accessbanking", "beneficionline", "perssonalpoint", "icb", "lcb", "cbc", "plurisoe", "bxsceoms", "csb", "uropaser", "urbaconstructora", "pwifasry", "globalfirecontrol", "utpfqsuf", "iingresoenllinea", "pwifasry", "iingresoenllinea", "sconlinebo", "argnetn1", "hombpm", "promociones-", "-clientes", "onnliincbc", "onlineicbc", "onlinelcbc", "accesshome", "ingresopeersonas", "ingresopersonas", "hombpm", "onlinebanking", "osagisu", "argentinaonline", "webadorsite", "redlinkd"]
    #include = ["icbc", "lcbc", "icdc", "banking", "accessbanking"]

    logging.debug("Message -> {}".format(message))

    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

        if len(all_domains) == 0:
            domain = "NULL"
        else:
            domain = all_domains[0]
        if ".cn" in domain and "icbc" in domain:
            print("icbc.cn domain, ignorado")
        else:
            for i in include:
                if i in domain:
                    with open("potentialphishing.txt", "a") as file:  
                        file.write(f'https://{domain}\n')
                    sys.stdout.write(u"[{}] {} (SAN: {})\n".format(datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'), domain, ", ".join(message['data']['leaf_cert']['all_domains'][1:])))
                    sys.stdout.flush()

logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.INFO)

certstream.listen_for_events(print_callback, url='wss://certstream.calidog.io/')
