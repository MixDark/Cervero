import os
import re
import sys
import json
import base64
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import csv

# GLOBAL CONSTANTS
BRAVE_PATH_LOCAL_STATE = os.path.normpath(r"%s\AppData\Local\BraveSoftware\Brave-Browser\User Data\Local State" % (os.environ['USERPROFILE']))
BRAVE_PATH = os.path.normpath(r"%s\AppData\Local\BraveSoftware\Brave-Browser\User Data" % (os.environ['USERPROFILE']))

EDGE_PATH_LOCAL_STATE = os.path.normpath(r"%s\AppData\Local\Microsoft\Edge\User Data\Local State" % (os.environ['USERPROFILE']))
EDGE_PATH = os.path.normpath(r"%s\AppData\Local\Microsoft\Edge\User Data" % (os.environ['USERPROFILE']))

CHROME_PATH_LOCAL_STATE = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Local State" % (os.environ['USERPROFILE']))
CHROME_PATH = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data" % (os.environ['USERPROFILE']))

def is_browser_installed(browser_path_local_state, browser_path):
    #Verifica si el navegador está instalado.
    return os.path.exists(browser_path_local_state) and os.path.exists(browser_path)

def get_secret_key(browser_path_local_state):
    try:
        #Obtiene la clave secreta
        with open(browser_path_local_state, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        # Remueve el sufijo DPAPI
        secret_key = secret_key[5:]
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
        return secret_key
    except Exception as e:
        print("%s" % str(e))
        print(f"[ERR] {browser_path_local_state} No se pudo encontrar la clave secreta.")
        return None

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(ciphertext, secret_key):
    try:
        # Vector de inicialización para el descifrado AES
        initialisation_vector = ciphertext[3:15]
        # Obtener la contraseña encriptada eliminando los bytes del sufijo (últimos 16 bits)
        # La contraseña cifrada es de 192 bits
        encrypted_password = ciphertext[15:-16]
        # Construye el cifrado para descifrar el texto cifrado
        cipher = generate_cipher(secret_key, initialisation_vector)
        decrypted_pass = decrypt_payload(cipher, encrypted_password)
        decrypted_pass = decrypted_pass.decode()
        return decrypted_pass
    except Exception as e:
        print("%s" % str(e))
        print("[ERR] No se puede descifrar, la versión del navegador inferior a la 80 no es compatible.")
        return ""

def get_db_connection(browser_path_login_db):
    try:
        print(browser_path_login_db)
        shutil.copy2(browser_path_login_db, "Loginvault.db")
        return sqlite3.connect("Loginvault.db")
    except Exception as e:
        print("%s" % str(e))
        print("[ERR] No se pudo encontrar la base de datos del navegador")
        return None

def get_browser_choice():
    print("\nNavegadores disponibles:")
    print("1. Brave")
    print("2. Microsoft Edge")
    print("3. Google Chrome")
    print("4. Salir")
    choice = input("\nElige una opción: ")
    return choice

def process_browser(browser_name, browser_path_local_state, browser_path):
    try:
        # Verificar si el navegador está instalado
        if not is_browser_installed(browser_path_local_state, browser_path):
            print(f"\n[INFO] {browser_name} no está instalado en este dispositivo.")
            return

        # Crear archivo CSV para almacenar las contraseñas
        with open(f'decrypted_password_{browser_name}.csv', mode='w', newline='', encoding='utf-8') as decrypt_password_file:
            csv_writer = csv.writer(decrypt_password_file, delimiter=',')
            csv_writer.writerow(["index", "url", "username", "password"])
            # Obtener la clave secreta
            secret_key = get_secret_key(browser_path_local_state)
            # Buscar perfiles de usuario o la carpeta predeterminada
            folders = [element for element in os.listdir(browser_path) if re.search("^Profile*|^Default$", element) != None]
            for folder in folders:
                # Obtener el texto cifrado de la base de datos SQLite
                browser_path_login_db = os.path.normpath(r"%s\%s\Login Data" % (browser_path, folder))
                conn = get_db_connection(browser_path_login_db)
                if (secret_key and conn):
                    cursor = conn.cursor()
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                    for index, login in enumerate(cursor.fetchall()):
                        url = login[0]
                        username = login[1]
                        ciphertext = login[2]
                        if (url != "" and username != "" and ciphertext != ""):
                            # Filtrar el vector de inicialización y la contraseña cifrada
                            # Usar el algoritmo AES para descifrar la contraseña
                            decrypted_password = decrypt_password(ciphertext, secret_key)
                            print("\nId: %d" % (index))
                            print("URL: %s\nNombre de usuario: %s\nContraseña: %s\n" % (url, username, decrypted_password))
                            print("*" * 50)
                            # Guardar en CSV
                            csv_writer.writerow([index, url, username, decrypted_password])
                    # Cerrar la conexión a la base de datos
                    cursor.close()
                    conn.close()
                    # Eliminar la base de datos temporal
                    os.remove("Loginvault.db")
    except Exception as e:
        print("[ERR] %s" % str(e))

if __name__ == '__main__':
    while True:
        choice = get_browser_choice()
        if choice == "1":
            print("\nProcesando Brave...")
            process_browser("Brave", BRAVE_PATH_LOCAL_STATE, BRAVE_PATH)
        elif choice == "2":
            print("\nProcesando Microsoft Edge...")
            process_browser("Edge", EDGE_PATH_LOCAL_STATE, EDGE_PATH)
        elif choice == "3":
            print("\nProcesando Google Chrome...")
            process_browser("Chrome", CHROME_PATH_LOCAL_STATE, CHROME_PATH)
        elif choice == "4":
            print("\nSaliendo del programa...")
            break
        else:
            print("\nOpción no válida. Intenta de nuevo.")