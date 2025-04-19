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

    with open("redes.json", "w", encoding="utf-8") as archivo:
        json.dump(networks, archivo, indent=4)

def is_connected():
    # Ejecutar el comando ping para verificar la conectividad
    result = subprocess.run(['ping', '8.8.8.8', '-n', '1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def connect_to_network(ssid, password):
    print(f'Conectando a la red {ssid}...')
    # Crear el perfil de red temporal
    profile = f"""
    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
        <name>{ssid}</name>
        <SSIDConfig>
            <SSID>
                <name>{ssid}</name>
            </SSID>
        </SSIDConfig>
        <connectionType>ESS</connectionType>
        <connectionMode>auto</connectionMode>
        <MSM>
            <security>
                <authEncryption>
                    <authentication>WPA2PSK</authentication>
                    <encryption>AES</encryption>
                    <useOneX>false</useOneX>
                </authEncryption>
                <sharedKey>
                    <keyType>passPhrase</keyType>
                    <protected>false</protected>
                    <keyMaterial>{password}</keyMaterial>
                </sharedKey>
            </security>
        </MSM>
    </WLANProfile>
    """

    # Guardar el perfil temporalmente
    profile_path = f"{ssid}.xml"
    with open(profile_path, 'w') as file:
        file.write(profile)

    # Conectar a la red usando netsh
    subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}"], check=True)
    subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], check=True)

    # Eliminar el perfil temporal
    os.remove(profile_path)

def main():
    while True:
        if not is_connected():
            print('Conexión perdida. Intentando reconectar...')
            for ssid, password in networks.items():
                connect_to_network(ssid, password)
                time.sleep(5)  
                if is_connected():
                    print('Conectado exitosamente.')
                    break
        else:
            print('Conexión establecida.')
        time.sleep(10)  

if __name__ == '__main__':
    main()
