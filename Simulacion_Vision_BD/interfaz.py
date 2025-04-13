import tkinter as tk
from tkinter import Label, Frame, Button, Toplevel, Entry, Text
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import psycopg2 as psy
import os
import threading

def conectar_bd():
    try:
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
        cursor.execute("""
            SELECT r.id_receta
            FROM pacientes p
            JOIN recetas r ON p.id_paciente = r.id_paciente
            WHERE p.nombre = %s;
            """, (nombre,))
        receta = cursor.fetchone()
        if receta is None:
            return [], None, None  # No se encontraron recetas para este paciente

        id_receta = receta[0]
        cursor.execute("""
            SELECT m.id_medicamento, m.nombre, m.dosis, m.frecuencia, m.tipo
            FROM rec_med rm
            JOIN medicamentos m ON rm.id_medicamento = m.id_medicamento
            WHERE rm.id_receta = %s;
            """, (id_receta,))
        medicamentos = cursor.fetchall()

        cursor.execute("""
            SELECT edad, habitacion
            FROM pacientes
            WHERE nombre = %s;
            """, (nombre,))
        info_paciente = cursor.fetchone()
        edad, habitacion = info_paciente if info_paciente else (None, None)

        return medicamentos, edad, habitacion
    except Exception as e:
        print(f"Error al consultar los datos: {e}")
        return [], None, None

def actualizar_paciente(conexion, nombre, edad, habitacion):
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE pacientes
            SET edad = %s, habitacion = %s
            WHERE nombre = %s;
            """, (edad, habitacion, nombre))
        conexion.commit()
        messagebox.showinfo("Éxito", "Datos del paciente actualizados correctamente.")
    except Exception as e:
        print(f"Error al actualizar los datos del paciente: {e}")
        messagebox.showerror("Error", "No se pudieron actualizar los datos del paciente.")
       
       
def agregar_medicamento(conexion, medicamento, id_receta):
	try:
		cursor = conexion.cursor()
		cursor.execute(
			"""
			INSERT INTO rec_med (id_receta, id_medicamento)
			VALUES (%s, %s);
			""",
			(id_receta,medicamento)
		)
		conexion.commit()
		print(f"Medicamento '{medicamento}' agregado correctamente.")
		
	except Exception as e:
		print(f"Error al insertar un nuevo medicamento: {e}")

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

class App:
    def __init__(self, root, conexion):
        self.root = root
        self.conexion = conexion
        self.root.title("Sistema de Monitoreo de Pacientes")

        # Frame para el video
        self.video_frame = Frame(self.root)
        self.video_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Canvas para la cámara
        #self.canvas = tk.Canvas(self.video_frame, width=640, height=480)
        #self.canvas.pack()

        # Frame para la información
        self.info_frame = Frame(self.root)
        self.info_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.nombre_label = Label(self.info_frame, text="Paciente: ", font=("Arial", 12))
        self.nombre_label.pack()

        self.edad_label = Label(self.info_frame, text="Edad: ", font=("Arial", 12))
        self.edad_label.pack()

        self.habitacion_label = Label(self.info_frame, text="Habitación: ", font=("Arial", 12))
        self.habitacion_label.pack()

        self.meds_label = Label(self.info_frame, text="Medicamentos: ", font=("Arial", 12))
        self.meds_label.pack()

        self.edit_button = Button(self.info_frame, text="Editar paciente", command=self.editar_paciente)
        self.add_button = Button(self.info_frame, text="Añadir medicación ", command=self.add_med)
        self.remove_button = Button(self.info_frame, text="Quitar medicación", command=self.remove_med)
        self.edit_button.pack(pady=10)
        self.add_button.pack(pady=10)
        self.remove_button.pack(pady=10)

        #elf.video_capture = cv2.VideoCapture(0)
        #self.update_video()

        # Iniciar el hilo para actualizar los datos del paciente
        self.file_path = "persona.txt"
        self.update_patient_info()

    def update_video(self):
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk
        self.root.after(10, self.update_video)

    def update_patient_info(self):
        nombre = leer_nombre(self.file_path)
        if nombre:
            self.nombre = nombre
            medicamentos, edad, habitacion = med_pac(self.conexion, nombre)
            self.medicamentos = medicamentos

            self.nombre_label.config(text=f"Paciente: {nombre}")
            self.edad_label.config(text=f"Edad: {edad if edad else 'N/A'}")
            self.habitacion_label.config(text=f"Habitación: {habitacion if habitacion else 'N/A'}")

            if medicamentos:
                meds_text = "\n".join([f"ID: {med[0]}, {med[1]} - {med[2]} {med[3]} ({med[4]})" for med in medicamentos])
            else:
                meds_text = "Sin medicamentos asignados"

            self.meds_label.config(text=f"Medicamentos: \n{meds_text}")
        else:
            self.nombre_label.config(text="Paciente: Desconocido")
            self.edad_label.config(text="Edad: N/A")
            self.habitacion_label.config(text="Habitación: N/A")
            self.meds_label.config(text="Medicamentos: N/A")

        self.root.after(5000, self.update_patient_info)

    def editar_paciente(self):
        nombre = leer_nombre(self.file_path)
        if not hasattr(self, 'nombre') or not self.nombre:
            messagebox.showwarning("Aviso", "No hay un paciente seleccionado para editar.")
            return

        edit_window = Toplevel(self.root)
        edit_window.title("Editar Paciente")

        Label(edit_window, text="Edad:").grid(row=0, column=0, padx=10, pady=10)
        edad_entry = Entry(edit_window)
        edad_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(edit_window, text="Habitación:").grid(row=1, column=0, padx=10, pady=10)
        habitacion_entry = Entry(edit_window)
        habitacion_entry.grid(row=1, column=1, padx=10, pady=10)
        
        
        
        def guardar_cambios():
            nueva_edad = edad_entry.get()
            nueva_habitacion = habitacion_entry.get()
            
            medicamentos, edad, habitacion = med_pac(self.conexion, nombre)
            if(nueva_habitacion == ''):
                nueva_habitacion=habitacion
            if(nueva_edad == ''):
                nueva_edad=edad                


            if not nueva_edad.isdigit() or int(nueva_edad) <= 0:
                messagebox.showerror("Error", "La edad debe ser un número válido.")
                return
                
            if not nueva_habitacion.isdigit() or not (1 <= int(nueva_habitacion) <= 400):
                messagebox.showerror("Error", "La habitación debe ser un número entre 1 y 400.")
                return

            actualizar_paciente(self.conexion, self.nombre, int(nueva_edad), nueva_habitacion)
            edit_window.destroy()

        Button(edit_window, text="Guardar", command=guardar_cambios).grid(row=2, column=0, columnspan=2, pady=10)


    def add_med(self):
        if not hasattr(self, 'nombre') or not self.nombre:
            messagebox.showwarning("Aviso", "No hay un paciente seleccionado.")
            return
           
        edit_window = Toplevel(self.root)
        edit_window.title("Añadir medicación")

        Label(edit_window, text="ID:").grid(row=0, column=0, padx=10, pady=10)
        med_entry = Entry(edit_window)
        med_entry.grid(row=0, column=1, padx=10, pady=10)

        
        def guardar_cambios():
            nuevo_med = med_entry.get()
            if int(nuevo_med) > 32 or int(nuevo_med) < 1:
                messagebox.showinfo("Aviso","IDs validos 1-32.")
                return
            nombre=self.nombre
            cursor = self.conexion.cursor()
            try:
				#Busca la receta
                cursor.execute("""
					SELECT r.id_receta
					FROM pacientes p
					JOIN recetas r ON p.id_paciente = r.id_paciente
					WHERE p.nombre = %s;
					""",(nombre,))
                receta = cursor.fetchone()
                if receta is None:
                	return []
                id_receta = receta[0]
            except Exeception as e:
            	print(e)
            agregar_medicamento(self.conexion, nuevo_med, id_receta)
            edit_window.destroy()

        Button(edit_window, text="Guardar", command=guardar_cambios).grid(row=1, column=0, columnspan=2, pady=10)
        
    def remove_med(self):
        if not hasattr(self, 'nombre') or not self.nombre:
        	messagebox.showwarning("Aviso", "No hay un paciente seleccionado.")
        	return

        edit_window = Toplevel(self.root)
        edit_window.title("Eliminar medicación")

        Label(edit_window, text="ID a eliminar:").grid(row=0, column=0, padx=10, pady=10)
        med_entry = Entry(edit_window)
        med_entry.grid(row=0, column=1, padx=10, pady=10)

        def eliminar_medicamento():
        	med_id = med_entry.get()
        	nombre = self.nombre
        	cursor = self.conexion.cursor()
        	try:
				# Busca la receta
        		cursor.execute("""
        			SELECT r.id_receta
        			FROM pacientes p
        			JOIN recetas r ON p.id_paciente = r.id_paciente
        			WHERE p.nombre = %s;
        		""", (nombre,))
        		receta = cursor.fetchone()
        		if receta is None:
        			messagebox.showerror("Error", "No se encontró una receta para el paciente.")
        			return
        		id_receta = receta[0]

        		cursor.execute("""
        			SELECT COUNT(*)
        			FROM rec_med
        			WHERE id_receta = %s AND id_medicamento = %s;
        		""", (id_receta, med_id))
        		exist = cursor.fetchone()[0]
				
        		if exist == 0:
        			messagebox.showerror("Error", "Medicamento no existente en la receta.")
        			return
				# Eliminar el medicamento de la receta
        		cursor.execute("""
        			DELETE FROM rec_med
        			WHERE id_receta = %s AND id_medicamento = %s;
        		""", (id_receta, med_id))
        		self.conexion.commit()

        		messagebox.showinfo("Éxito", f"Medicamento con ID {med_id} eliminado de la receta.")
        		edit_window.destroy()

        	except Exception as e:
        		print(e)
        		messagebox.showerror("Error", f"Ocurrió un error: {e}")
        		self.conexion.rollback()

        Button(edit_window, text="Eliminar", command=eliminar_medicamento).grid(row=1, column=0, columnspan=2, pady=10)

        
        
    def on_closing(self):
        #self.video_capture.release()
        self.root.destroy()

if __name__ == "__main__":
    conexion = conectar_bd()
    if not conexion:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
        exit()

    root = tk.Tk()
    root.geometry("300x480+100+50")
    app = App(root, conexion)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

    if conexion:
        conexion.close()
