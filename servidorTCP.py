import hashlib
import socketserver
import os
from datetime import datetime 
import datetime

base_dir= "/Users/natha/OneDrive - Universidad de los Andes/"

class FileRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):

        print(f'Cliente conectado desde {self.client_address[0]}:{self.client_address[1]}')


        # Recibe el nombre del archivo
        filename = self.request.recv(1024).decode()
        
        # Intenta abrir el archivo
        try:
            with open(base_dir+filename, 'rb') as f:
                start_time = datetime.datetime.now()
                # Envia una respuesta positiva al cliente
                self.request.sendall(b'OK')

                # Calcula el hash del archivo y envíalo al cliente
                hasher = hashlib.md5()
                buf = f.read(1024)
                while buf:
                    hasher.update(buf)
                    buf = f.read(1024)
                self.request.sendall(hasher.hexdigest().encode())
                file_hash = hasher.hexdigest()
                
                # Envía el tamaño del archivo
                f.seek(0, 2)
                file_size = os.path.getsize(base_dir + filename)
                self.request.sendall(file_size.to_bytes(4, byteorder='big'))

                # Envía el archivo en paquetes de 1024 bytes
                f.seek(0)
                while True:
                    buf = f.read(1024)
                    if not buf:
                        break
                    self.request.sendall(buf)

                # Espera la confirmación del cliente
                confirm = self.request.recv(1024).decode()
                if confirm == 'FIN':
                    print(f'El archivo {filename} ha sido enviado con éxito al cliente {self.client_address}')
                else:
                    print(f'Error: confirmación inesperada del cliente {self.client_address}')  

                end_time = datetime.datetime.now()         
                
        # Si el archivo no se puede abrir, envía una respuesta negativa al cliente
        except FileNotFoundError:
            self.request.sendall(b'ERROR')

        # Registrar la transferencia en el archivo de log
        tiempo = end_time - start_time
        nombreArchivo = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f-log.txt")

        ruta_carpeta = "/Users/natha/Desktop/Logs/"

        ruta_archivo = os.path.join(ruta_carpeta, nombreArchivo + ".txt")

        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

        with open(ruta_archivo, "w") as f:
            f.write('Cliente: ' + str(self.client_address[0]) +'\n')
            f.write('Archivo: ' + filename +'\n')
            f.write('Tamaño: ' + str(file_size) + ' bytes\n')
            f.write('Hash: ' +str(file_hash) +'\n')
            f.write('Tiempo: ' +str(tiempo) +'\n')

# Dirección y puerto del servidor
serverAddress = ('localhost', 12000)

# Crea el servidor y asigna el manejador de solicitudes
server = socketserver.ThreadingTCPServer(serverAddress, FileRequestHandler)
server.max_threads=25
print("El servidor está listo para recibir conexiones")

file_list = os.listdir(base_dir)

print("Archivos disponibles para enviar:")
for filename in file_list:
    if os.path.isfile(base_dir + filename):
        print(filename)

# Inicia el servidor y corre indefinidamente
server.serve_forever()

