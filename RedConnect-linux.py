
import os
import time
import json
import subprocess

def existe():
    return os.path.exists("redes.json")

def abrir():
    with open("redes.json", "r", encoding="utf-8") as archivo:
        redes = json.load(archivo)
        return redes
    
if existe():
    networks = abrir()

else:
    cantidad = int(input("Ingresa cuantas redes quieres verificar: "))
    networks = {}
    while cantidad > 0:
        ssid = input("Ingresa el SSID de la red: ")
        contrasena = input("Ingresa la contraseña: ")
        networks[ssid] = contrasena
        cantidad -= 1

def is_connected():
    # Verificar la conectividad utilizando 'nmcli' (si está disponible)
    try:
        result = subprocess.run(['nmcli', 'dev', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'connected' in result.stdout.decode()
    except FileNotFoundError:
        # Si nmcli no está disponible, comprobar con 'iwconfig'
        result = subprocess.run(['iwconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'ESSID' in result.stdout.decode()

def connect_to_network(ssid, password, interface):
    print(f'Conectando a la red {ssid}...')
    
    try:
        # Intentar usar 'nmcli' para conectar
        result = subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print(f'Conectado a {ssid} exitosamente.')
        else:
            print(f'Error al conectar a {ssid} con nmcli: {result.stderr.decode()}')
    except FileNotFoundError:
        # Si no está disponible, intentar usar wpa_supplicant + iwconfig
        print(f'Intentando conexión manual con iwconfig y wpa_supplicant...')
        
        # Primero, desconectarse de cualquier red
        subprocess.run(["sudo", "ifconfig", interface, "down"], check=True)
        subprocess.run(["sudo", "ifconfig", interface, "up"], check=True)
        
        # Crear archivo de configuración WPA para wpa_supplicant
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
            f.write(f"""
network={{
    ssid="{ssid}"
    psk="{password}"
}}
            """)
        
        subprocess.run(["sudo", "wpa_supplicant", "-B", "-i", interface, "-c", "/etc/wpa_supplicant/wpa_supplicant.conf"], check=True)
        subprocess.run(["sudo", "dhclient", interface], check=True)

        print(f'Conectado a {ssid} usando wpa_supplicant.')

def main():
    interface = input("Por favor, introduce el nombre de tu interfaz de red Wi-Fi (ej. wlan0, wlp3s0), usa el comando 'ip a' o 'ifconfig' si no estás seguro: ")
    
    while True:
        if not is_connected():
            print('Conexión perdida. Intentando reconectar...')
            for ssid, password in networks.items():
                connect_to_network(ssid, password, interface)
                time.sleep(5)  
                if is_connected():
                    print('Conexión exitosa.')
                    break
        else:
            print('Conexión establecida.')
        time.sleep(10)  

if __name__ == '__main__':
    main()
