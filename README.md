# Cervero

## Descripción
Un script creado para descifrar las credenciales que se guardan en los navegadores, con este metodo se pueden ver en texto plano y también realiza el envio al correo electronico en un archivo de excel protegido por contraseña.

## Capturas de pantalla
![Cervero](https://github.com/user-attachments/assets/27e12b76-d5de-45db-b6c3-ab72e405505e)

![image](https://github.com/user-attachments/assets/63d03dcf-3571-4218-a7b8-0fad86f89057)


## Características
- Es compatible con Windows
- Soporte para navegadores como Microsoft Edge, Google Chrome y Brave
- Guardar la información en un archivo CSV por cada navegador protegido por contraseña
- Envia el reporte al correo electrónico
- Interfaz simple e intuitiva


## Requerimientos
- Python 3.x 
- pycryptodome
- pywin32
- msoffcrypto-tool
- colorama
- openpyxl
- python-dotenv
- win32crypt

## Configuración del archivo .env
Crea el archivo .env en la misma carpeta del script con la estructura que se muestra en el ejemplo, reemplaza los valores con los datos solicitados, para crear la contraseña de aplicación en Gmail sigue los pasos del video https://www.youtube.com/watch?v=xnbGakU7vhE

EMAIL_USER=tucorreodeorigen
EMAIL_PASSWORD=tucontrasenadeaplicacion
EMAIL_RECEIVER=tucorreodedestino

## Instalación desde CLI
1. Clona el repositorio: 
git clone https://github.com/MixDark/Cervero.git
2. Instala las dependencias:
pip install -r requirements.txt
3. Ejecuta la aplicación:
python cervero.py

## Uso
1. Ejecuta el script y selecciona una opción 
2. Escribe una contraseña para proteger el archivo (opcional)
3. El archivo de Excel se envia al correo electronico

## Descargo de responsabilidad
Este script fue creado para simular una situación en la que la gran mayorias de usuarios guardan las contraseñas en el navegador, su uso es para fines educativos y en caso de ser usado con fines maliciosos puede traer consecuencias legales en base a la leyes existentes en cada país.
