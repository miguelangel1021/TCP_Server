import threading
import hashlib
from socket import *
import os

# Dirección y puerto del servidor
serverAddress = ('localhost', 12000)
evento = threading.Event()
# Nombre del archivo a descargar


# Función que maneja la conexión
def handle_connection():
    try:
        i = 1
        # Establece la conexión con el servidor
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect(serverAddress)
        
        evento.wait()

        # Envia el nombre del archivo al servidor
        clientSocket.send(filename.encode())
        
        # Recibe la respuesta del servidor
        response = clientSocket.recv(1024).decode()
        
        # Si el servidor encontró el archivo, procede a descargarlo
        if response == "OK":
            # Recibe el valor hash del archivo
            file_hash = clientSocket.recv(1024).decode()

            # Recibe el tamaño del archivo
            file_size = int.from_bytes(clientSocket.recv(4), byteorder='big')

            # Crea un objeto hash para verificar la integridad del archivo
            hasher = hashlib.md5()

            # Descarga el archivo en paquetes de 1024 bytes y actualiza el objeto hash

            
            ruta_carpeta = "/Users/natha/Desktop/ArchivosRecibidos/"

            ruta_archivo = os.path.join(ruta_carpeta, filename + ".txt")

            if not os.path.exists(ruta_carpeta):
                os.makedirs(ruta_carpeta)

            with open(ruta_archivo, "wb") as f:
                received = 0
                while received < file_size:
                    buf = clientSocket.recv(1024)
                    received += len(buf)
                    f.write(buf)
                    hasher.update(buf)

            # Verifica la integridad del archivo descargado
            if hasher.hexdigest() == file_hash:
                print("El archivo", filename, "ha sido descargado con éxito")
            else:
                print("Error: el archivo descargado está corrupto")
        else:
            print("Error: el servidor no encontró el archivo")
        
        # Cierra la conexión con el servidor
        clientSocket.send("FIN".encode())
        clientSocket.close()
        
    except error:
        print("Error de conexión:", error)
    i += 1


numClientes = int(input("Ingrese el numero de clientes que desea:"))
filename = input("Ingrese el nombre del archivo que desea descargar:")

# Crea 5 hilos o subprocesos para manejar las conexiones concurrentes
for i in range(numClientes):
    client_handler = threading.Thread(target=handle_connection)
    client_handler.daemon = True
    client_handler.start()

evento.set()

# Espera a que los hilos o subprocesos terminen
for thread in threading.enumerate():
    if thread != threading.current_thread():
        thread.join()