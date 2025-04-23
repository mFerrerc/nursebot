<div align="justify">

# NurseBot: Sistema Integral de Asistencia de Medicación Automatizada
NurseBot es un sistema diseñado para automatizar la dispensación de medicamentos, enlazando el reconocimiento del paciente, la gestión de dosis y la interacción por voz. Tras detectar quién solicita la medicación, el robot sirve la dosis adecuada y registra cada administración en una base de datos, al mismo tiempo que mantiene una comunicación conversacional con el usuario.

## Tecnologías Empleadas

### RobotStudio
RobotStudio es una plataforma de simulación robótica que recrea la celda de trabajo, ofreciendo un entorno virtual para programar y probar movimientos. En NurseBot, se define toda la lógica de manipulación de frascos, goteros y pastillas. Mediante esta herramienta, se afinan las trayectorias de la pinza y se integra la comunicación con otros módulos antes de cualquier implementación física.

<p align="center">
  <img src="https://github.com/user-attachments/assets/7a95ce79-1333-4161-991a-5069108a8ef6" />
</p>

### OPC UA
OPC UA es un estándar de comunicación cliente-servidor que facilita el intercambio de datos entre distintas aplicaciones industriales. En el proyecto, NurseBot se vincula con RobotStudio a través de este protocolo, transmitiendo las órdenes de medicación y recibiendo la confirmación de que el robot ha completado la tarea.

### face_recognition
La librería face_recognition permite detectar y reconocer rostros utilizando comparaciones de vectores de características. NurseBot emplea este módulo para identificar al paciente antes de cada dispensación, asegurándose de asociar el tratamiento correcto a la persona adecuada.

### PostgreSQL
PostgreSQL es una base de datos relacional robusta y escalable. En NurseBot, se utiliza para almacenar la información de pacientes, su plan de medicación y los detalles de cada medicamento. Su alojamiento en la nube hace posible el acceso remoto y la actualización inmediata de los datos, evitando inconsistencias.

<p align="center">
  <img src="https://github.com/user-attachments/assets/b2416697-b326-4fbb-b031-2b8da509c87f" />
</p>

### FlowiseAI
FlowiseAI ofrece un entorno visual para encadenar procesos de inteligencia artificial y lógica de negocio. Aquí se orquestan los flujos de preguntas y respuestas, conectando el reconocimiento de voz, la recuperación de información y el modelo de lenguaje para generar respuestas coherentes y contextualizadas.

<p align="center">
  <img src="https://github.com/user-attachments/assets/58c1c1f3-7919-4506-ab30-4052ae614731" />
</p>

### Ollama
Ollama actúa como un servidor de modelos de lenguaje, proporcionando un endpoint unificado para ejecutar inferencias con distintas variantes de LLM. NurseBot se apoya en Ollama para servir el modelo (por ejemplo, Llama3.1 8B), asegurando una gestión centralizada y eficiente de los recursos.

### RAG (Retrieval-Augmented Generation)
El enfoque RAG combina la recuperación de información con la generación de lenguaje. Primero se buscan fragmentos relevantes en un índice vectorial, y después se suministran como contexto al LLM. En NurseBot, esta técnica permite enriquecer las respuestas del agente conversacional con datos privados o específicos almacenados en la base de datos.

<p align="center">
  <img src="https://github.com/user-attachments/assets/250ee4c0-2c75-4ac8-909d-663d7c3b0faf" />
</p>

### Whisper
Whisper (y variantes optimizadas como WhisperS2T) son modelos de Speech-to-Text capaces de transcribir de forma confiable el audio de los usuarios. Aquí, NurseBot se basa en Whisper para entender las solicitudes verbales, detectando el idioma y convirtiendo la voz en texto antes de consultar el agente conversacional.

### XTTS
XTTS es un módulo de Text-to-Speech que transforma la respuesta del sistema en audio. Tras elaborar la contestación, NurseBot la pasa a XTTS para generar una voz natural, facilitando la interacción fluida con el usuario, tanto en español como en otros idiomas.

### Tkinter
Tkinter es la biblioteca de interfaces gráficas nativa de Python. NurseBot utiliza esta herramienta para presentar un panel de control donde el personal de enfermería puede visualizar la información del paciente, editar datos en tiempo real y controlar la dispensación de medicamentos de forma intuitiva.

## Vídeo de la aplicación
En este apartado se encuentra un enlace a un vídeo a YouTube
donde se muestra el funcionamiento al completo de la aplicación de robótica de servicios.

https://www.youtube.com/watch?v=vQD2WK-XxbI&feature=youtu.be


## Requisitos
El sistema NurseBot requiere un conjunto de librerías, frameworks y configuraciones específicas para funcionar correctamente. A continuación, se describen los componentes principales tomados de la Guía de Usuario, incluyendo las dependencias mínimas, las herramientas de simulación y los ajustes sugeridos para una instalación exitosa.

### RobotStudio
Para la simulación robótica es fundamental contar con:

- RobotStudio de ABB, que permite definir la celda de trabajo y programar las trayectorias del robot.

- La librería de OPC UA, imprescindible para la comunicación entre RobotStudio y la aplicación de Python, instalable mediante:
```
pip install opcua
```
### Base de Datos
La gestión de la información de pacientes, medicamentos y recetas se realiza en PostgreSQL. Para interactuar con la base de datos en Python, se requiere:
```
pip install psycopg2
```
### Control por Visión
Este apartado se encarga de detectar y reconocer rostros para asociarlos al plan de medicación:

OpenCV: Biblioteca para el procesamiento de imágenes en tiempo real.
```
pip install opencv
```

face_recognition: Motor de detección y comparación de rostros.
```
pip install face_recognition
```

dlib: Base subyacente para la extracción de características faciales.
```
pip install dlib
```

Estructura de archivos: Debe existir un archivo persona.txt y una carpeta known_faces con subcarpetas (una por cada persona), conteniendo sus imágenes de entrenamiento.

### Agente Conversacional
El módulo de interacción por voz y generación de respuestas depende de varias tecnologías, detalladas a continuación:

#### Configuración de GPU
Para un rendimiento óptimo en la etapa de procesamiento de voz y modelos de lenguaje se recomienda:

- Python 3.9

- CUDA 12.1

- PyTorch 2.5.1

- TensorFlow 2.18.0

- cudnn-cu12 9.1.0.70

#### Detección de Habla
El sistema usa Silero-VAD para identificar cuándo el usuario habla y cuándo hay silencio:
```
pip install numpy>=1.24.0
pip install torch>=1.12.0
pip install torchaudio>=0.12.0
```

En Windows puede instalarse PyAudio con:
```
pip install pyaudio
```

En Linux, se recomienda:
```
apt install python3-pyaudio
```

#### STT (Speech-to-Text)
Para la transcripción del audio en tiempo real, NurseBot combina dos variantes de Whisper:

Whisper
```
pip install whisper
```

WhisperS2T
```
pip install -U whisper-s2t
```

Además, es necesario contar con ffmpeg, instalable según el entorno:

Ubuntu:
```
apt-get install -y libsndfile1 ffmpeg
```

Mac:
```
brew install ffmpeg
```

Conda (cualquier SO):
```
conda install conda-forge::ffmpeg
```

#### LLM (Modelos de Lenguaje)
NurseBot utiliza Ollama como servidor de modelos de lenguaje y Flowise para gestionar los flujos de información:

- Docker Ollama: Se requiere el contenedor de herramientas de NVIDIA para habilitar CUDA y ejecutar Ollama con la GPU. Posteriormente, se descargan y configuran los modelos (como llama3.1:8b).

- Docker Flowise: Para servir el flujo del agente conversacional, se construye y lanza la imagen en el puerto indicado.

#### Traducción
Si el usuario habla un idioma diferente al español, se realiza la traducción con:
```
pip install googletrans==4.0.0-rc1
pip install requests
```

#### TTS (Text-to-Speech)
La respuesta se sintetiza en una voz natural mediante XTTS dentro de un servidor Flask:
```
pip install flask
sudo apt-get -y install libegl1
sudo apt-get -y install libopengl0
sudo apt-get -y install libxcb-cursor
pip install gradio==4.44.1
pip install fastapi==0.103.1
pip install pydantic==2.3.0
pip install ctranslate2==4.4.0
```

Además, es necesario clonar el repositorio xtts-webui, instalar sus dependencias (requirements.txt), y descargar los modelos de voz indicados con los comandos wget y unzip.

#### Interfaz
La interfaz gráfica se basa en Tkinter y requiere de:
```
pip install tkinter
pip install Pillow
```

Dicha interfaz muestra los datos del paciente (edad, habitación, medicación) y posibilita la edición de información en tiempo real.

</div>
