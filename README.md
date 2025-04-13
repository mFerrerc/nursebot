# NurseBot: Sistema Integral de Asistencia de Medicación Automatizada
NurseBot es un sistema diseñado para automatizar la dispensación de medicamentos, enlazando el reconocimiento del paciente, la gestión de dosis y la interacción por voz. Tras detectar quién solicita la medicación, el robot sirve la dosis adecuada y registra cada administración en una base de datos, al mismo tiempo que mantiene una comunicación conversacional con el usuario.

## Tecnologías Empleadas
### RobotStudio
RobotStudio es una plataforma de simulación robótica que recrea la celda de trabajo, ofreciendo un entorno virtual para programar y probar movimientos. En NurseBot, se define toda la lógica de manipulación de frascos, goteros y pastillas. Mediante esta herramienta, se afinan las trayectorias de la pinza y se integra la comunicación con otros módulos antes de cualquier implementación física.

### OPC UA
OPC UA es un estándar de comunicación cliente-servidor que facilita el intercambio de datos entre distintas aplicaciones industriales. En el proyecto, NurseBot se vincula con RobotStudio a través de este protocolo, transmitiendo las órdenes de medicación y recibiendo la confirmación de que el robot ha completado la tarea.

### face_recognition
La librería face_recognition permite detectar y reconocer rostros utilizando comparaciones de vectores de características. NurseBot emplea este módulo para identificar al paciente antes de cada dispensación, asegurándose de asociar el tratamiento correcto a la persona adecuada.

### PostgreSQL
PostgreSQL es una base de datos relacional robusta y escalable. En NurseBot, se utiliza para almacenar la información de pacientes, su plan de medicación y los detalles de cada medicamento. Su alojamiento en la nube hace posible el acceso remoto y la actualización inmediata de los datos, evitando inconsistencias.

### FlowiseAI
FlowiseAI ofrece un entorno visual para encadenar procesos de inteligencia artificial y lógica de negocio. Aquí se orquestan los flujos de preguntas y respuestas, conectando el reconocimiento de voz, la recuperación de información y el modelo de lenguaje para generar respuestas coherentes y contextualizadas.

### Ollama
Ollama actúa como un servidor de modelos de lenguaje, proporcionando un endpoint unificado para ejecutar inferencias con distintas variantes de LLM. NurseBot se apoya en Ollama para servir el modelo (por ejemplo, Llama3.1 8B), asegurando una gestión centralizada y eficiente de los recursos.

### RAG (Retrieval-Augmented Generation)
El enfoque RAG combina la recuperación de información con la generación de lenguaje. Primero se buscan fragmentos relevantes en un índice vectorial, y después se suministran como contexto al LLM. En NurseBot, esta técnica permite enriquecer las respuestas del agente conversacional con datos privados o específicos almacenados en la base de datos.

### Whisper
Whisper (y variantes optimizadas como WhisperS2T) son modelos de Speech-to-Text capaces de transcribir de forma confiable el audio de los usuarios. Aquí, NurseBot se basa en Whisper para entender las solicitudes verbales, detectando el idioma y convirtiendo la voz en texto antes de consultar el agente conversacional.

### XTTS
XTTS es un módulo de Text-to-Speech que transforma la respuesta del sistema en audio. Tras elaborar la contestación, NurseBot la pasa a XTTS para generar una voz natural, facilitando la interacción fluida con el usuario, tanto en español como en otros idiomas.

### Tkinter
Tkinter es la biblioteca de interfaces gráficas nativa de Python. NurseBot utiliza esta herramienta para presentar un panel de control donde el personal de enfermería puede visualizar la información del paciente, editar datos en tiempo real y controlar la dispensación de medicamentos de forma intuitiva.

En conjunto, estas tecnologías se combinan para ofrecer un sistema integral que abarca tanto la programación y simulación del robot como la interacción multimodal (voz y visión) y la administración de datos, siempre con el objetivo de mejorar la seguridad y la eficiencia en el cuidado de los pacientes.
 
