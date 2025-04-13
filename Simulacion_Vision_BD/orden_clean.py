import os

def procesar_carpeta(ruta_carpeta):
    try:
        # Comprobar si la carpeta existe
        if not os.path.exists(ruta_carpeta):
            print(f"La ruta especificada '{ruta_carpeta}' no existe.")
            return

        # Obtener el nombre de la carpeta
        nombre_carpeta = os.path.basename(ruta_carpeta)

        # Listar todos los archivos en la carpeta
        archivos = os.listdir(ruta_carpeta)

        contador = 1

        for archivo in archivos:
            ruta_completa = os.path.join(ruta_carpeta, archivo)

            # Asegurarse de que es un archivo
            if os.path.isfile(ruta_completa):
                # Comprobar si el archivo termina en .jpg
                if archivo.lower().endswith('.jpg'):
                    # Generar nuevo nombre
                    nuevo_nombre = f"{nombre_carpeta}_{contador}.jpg"
                    ruta_nueva = os.path.join(ruta_carpeta, nuevo_nombre)

                    # Renombrar el archivo
                    os.rename(ruta_completa, ruta_nueva)
                    print(f"Renombrado: {archivo} -> {nuevo_nombre}")
                    contador += 1
                else:
                    # Eliminar el archivo si no es .jpg
                    os.remove(ruta_completa)
                    print(f"Eliminado: {archivo}")

        print("Proceso completado.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

# Lista de rutas de carpetas a procesar
rutas_carpetas = [
    "known_faces/Badar el Asery",
    "known_faces/Eduardo Ugarte",
    "known_faces/Miguel Ferrer",
    "known_faces/Miguel Pascual",
    "known_faces/Pablo de Codina"
]

# Procesar cada carpeta
for ruta in rutas_carpetas:
    print(f"Procesando carpeta: {ruta}")
    procesar_carpeta(ruta)