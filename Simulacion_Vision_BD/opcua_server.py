from opcua import Server
import time

class OpcuaServer:
    def __init__(self, endpoint="opc.tcp://192.168.18.107:4840", namespace="http://example.org"):
        # Crear servidor OPC UA
        self.server = Server()

        # Configurar el servidor: URI del servidor y dirección de acceso
        self.server.set_endpoint(endpoint)
        
        # Registrar espacio de nombres (namespace)
        self.uri = namespace
        self.idx = self.server.register_namespace(self.uri)
        
        # Obtener el objeto de la raíz (root) del servidor
        self.objects = self.server.get_objects_node()  # Usar get_objects_node() en lugar de get_objects()
        
        # Crear el objeto "Medicina"
        self.medicina_obj = self.objects.add_object(self.idx, "Medicina")
        
        # Crear las variables dentro del objeto "Medicina"
        self.medicina_signal = self.medicina_obj.add_variable(self.idx, "medicina_signal", 0)  # Valor inicial: 0
        self.dosis_signal = self.medicina_obj.add_variable(self.idx, "dosis_signal", 0)  # Valor inicial: 0
        self.ready_signal = self.medicina_obj.add_variable(self.idx, "ready_signal", True)  # Valor inicial: True
        
        # Hacer que las variables "medicina_signal" y "dosis_signal" sean escribibles
        self.medicina_signal.set_writable()
        self.dosis_signal.set_writable()
        
        # Hacer que la señal "ready_signal" sea también escribible
        self.ready_signal.set_writable()

    def start_server(self):
        # Iniciar el servidor
        self.server.start()
        print(f"Servidor OPC UA iniciado en {self.server.endpoint}")
    
    def stop_server(self):
        # Detener el servidor
        self.server.stop()
        print("Servidor detenido.")

    def enviar_datos_paciente(self, medicamento_id, dosis):
        # Verificar si el sistema está listo
        if not self.ready_signal.get_value():
            print("El sistema no está listo para procesar una nueva medicina.")
            return

        # Enviar los valores al servidor OPC UA
        self.medicina_signal.set_value(medicamento_id)  # Asignar el ID de medicina
        self.dosis_signal.set_value(dosis)  # Asignar la dosis

        # Mostrar los valores enviados (para monitoreo)
        print(f"medicina_signal: {self.medicina_signal.get_value()}")
        print(f"dosis_signal: {self.dosis_signal.get_value()}")

        # Esperar 1 segundo antes de restablecer los valores
        time.sleep(1)

        # Restablecer los valores a 0
        self.medicina_signal.set_value(0)
        self.dosis_signal.set_value(0)

        # Mostrar los valores restablecidos (para monitoreo)
        print(f"medicina_signal después de 1 segundo: {self.medicina_signal.get_value()}")
        print(f"dosis_signal después de 1 segundo: {self.dosis_signal.get_value()}")

        # Establecer la señal ready_signal a True (se puede escribir)
        #self.ready_signal.set_value(True)
        #print("ready_signal está ahora en: ", self.ready_signal.get_value())

    def get_ready(self):
        return self.ready_signal.get_value()
