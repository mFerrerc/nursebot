import psycopg2 as psy
import os
from opcua_server import OpcuaServer
import time

def conectar_bd():
    try:
        # Asegúrate de definir DATABASE_URL en las variables de entorno locales si usas esta opción.
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:GCIXkuhMxvKMnwDKlfSzJXRgxuQRbTiI@junction.proxy.rlwy.net:26123/railway")
        conexion = psy.connect(db_url)
        print("Conexión exitosa a la base de datos en Railway.")
        return conexion

    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
        
      
def med_pac(conexion, nombre):
    try:
        cursor = conexion.cursor()
        # Busca la receta
        cursor.execute("""
            SELECT r.id_receta
            FROM pacientes p
            JOIN recetas r ON p.id_paciente = r.id_paciente
            WHERE p.nombre = %s;
            """, (nombre,))
        receta = cursor.fetchone()
        if receta is None:
            return []
        id_receta = receta[0]
        # Busca los medicamentos
        cursor.execute("""
            SELECT m.id_medicamento, m.nombre, m.dosis, m.frecuencia, m.tipo
            FROM rec_med rm
            JOIN medicamentos m ON rm.id_medicamento = m.id_medicamento
            WHERE rm.id_receta = %s;        
            """, (id_receta,))
        medicamentos = cursor.fetchall()
        return medicamentos 

    except Exception as e:
        print(f"Error al consultar los medicamentos: {e}")      
        return []

def envioDatos(medicamentos):
    envio_id = [medicamento[0] for medicamento in medicamentos]
    envio_dosis = [medicamento[2] for medicamento in medicamentos]
    envio_medicamento = [medicamento[1] for medicamento in medicamentos]
    return envio_id, envio_dosis, envio_medicamento


def leer_nombre(file_path):
    try:
        with open(file_path, "r") as file:
            nombre = file.readline().strip()
            if not nombre:
                print("Archivo vacío")
                return None
            return nombre
    except FileNotFoundError:
        print("Archivo no existente")
        return None	

def main():
    conexion = conectar_bd()  # Conectamos la base de datos
    file_path = "persona.txt"  # Path de archivo
    salir = False  # Centinela de salida
    nombres_anteriores = [] 

    opcua_server = OpcuaServer("opc.tcp://192.168.18.107:4840")  # HAY QUE CAMBIAR LA IP
    opcua_server.start_server()

    try:
        while not salir:
            nombre_nuevo = leer_nombre(file_path)  # Leemos el nombre del archivo
            if nombre_nuevo not in nombres_anteriores:  # Si el nombre es distinto a los ya medicados
                medicamentos = med_pac(conexion, nombre_nuevo)  # Sacamos sus medicamentos
                if medicamentos:
                    envio_id, envio_dosis, envio_medicamento = envioDatos(medicamentos)  # Almacenamos sus medicamentos
                    print(f"\nSuministrando al paciente: {nombre_nuevo}")
                    for i in range(len(envio_id)):  # Variables de envío a la simulación
                        while not opcua_server.get_ready():
                            #print("Esperando...")
                            time.sleep(0.1)  # Puede dar error si el servidor no está listo
                        opcua_server.enviar_datos_paciente(int(envio_id[i]), int(envio_dosis[i]))
                        print(f"Enviando ID: {envio_id[i]}")
                        print(f"Enviando dosis: {envio_dosis[i]}")
                        print(f"Suministrando {envio_medicamento[i]}...\n")
                        time.sleep(1.2)
                        #print(opcua_server.get_ready())

                    nombres_anteriores.append(nombre_nuevo)  # Actualizamos los nombres
            else:
                print(f"El paciente {nombre_nuevo} ya ha sido medicado.")

            user_input = input("Esperando nuevo paciente... ('N' para limpiar la lista de pacientes medicados) ")  # Cambiar
            if user_input.lower() == 'n':
                nombres_anteriores = []  # Limpiamos la lista

    except KeyboardInterrupt:
        print("\nServidor detenido.")

    finally:
        # Detener el servidor cuando se cierre
        if conexion:
            conexion.close()
        opcua_server.stop_server()

if __name__ == '__main__':
    main()

