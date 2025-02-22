import os
import time
import subprocess

# Lista de redes y sus contraseñas
networks = {
    'SSID1': 'password1',
    'SSID2': 'password2',
    # Añade más redes y contraseñas según sea necesario
}

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
    os.system(f'netsh wlan add profile filename="{profile_path}"')
    os.system(f'netsh wlan connect name="{ssid}"')

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
