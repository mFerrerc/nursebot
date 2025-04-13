import cv2
import face_recognition
import os

# Ruta de la carpeta con las imágenes conocidas
KNOWN_FACES_DIR = "known_faces"
TOLERANCE = 0.4  # Tolerancia para reconocimiento facial
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = "hog"  # Usa "cnn" si tienes GPU para mayor precisión

print("Cargando caras conocidas...")
known_faces = []
known_names = []

for name in os.listdir(KNOWN_FACES_DIR):
    for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):
        file_path = f"{KNOWN_FACES_DIR}/{name}/{filename}"
        print(f"Procesando {filename}...")
        
        # Cargar la imagen
        image = face_recognition.load_image_file(file_path)
        
        # Intentar codificar la cara
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            encoding = encodings[0]
            known_faces.append(encoding)
            known_names.append(name)
        else:
            print(f"No se detectó ninguna cara en {filename}. Asegúrate de que la imagen contiene una cara visible.")

# Inicializar la cámara
print("Iniciando cámara...")
video = cv2.VideoCapture(0)

while True:
    # Leer un frame de la cámara
    ret, frame = video.read()
    if not ret:
        break

    # Reducir tamaño del frame para procesarlo más rápido
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Encontrar todas las caras y codificarlas
    face_locations = face_recognition.face_locations(rgb_small_frame, model=MODEL)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        # Comparar con caras conocidas
        matches = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
        name = "Desconocido"

        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]

        # Escalar coordenadas de vuelta al tamaño original
        top, right, bottom, left = face_location
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Dibujar un rectángulo alrededor de la cara
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), FRAME_THICKNESS)
        # Mostrar el nombre
        cv2.putText(frame, name, (left + 10, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), FONT_THICKNESS)
        with open("persona.txt", "w") as archivo:
            archivo.write(name)
    
    # Redimensionar el frame para mostrarlo más pequeño
    display_frame = cv2.resize(frame, (0, 0), fx=0.6, fy=0.6)  # Cambiar los factores según sea necesario
    cv2.imshow("Face Recognition", display_frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        with open("persona.txt", "w") as archivo:
            archivo.write("no_corriendo")
        break

# Liberar recursos
video.release()
cv2.destroyAllWindows()

