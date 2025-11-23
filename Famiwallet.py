import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime

# ------------------------------------
# VARIABLES GLOBALES
# ------------------------------------
datos_por_fecha = {}
apellido_familia = ""

# ------------------------------------
# ESTILOS
# ------------------------------------
BG_COLOR = "#F5F5F5"
BTN_COLOR = "#D3A97D"
BTN_TEXT = "#3E2C1C"
FONT_MAIN = ("Segoe UI", 14)
FONT_HEADER = ("Segoe UI", 20, "bold")

# ------------------------------------
# PANTALLA DE INICIO
# ------------------------------------
def pantalla_inicio():
    inicio = tk.Tk()
    inicio.title("FamiWallet - Inicio")
    inicio.geometry("600x600")
    inicio.config(bg=BG_COLOR)

    # Logo
    try:
        logo_img = PhotoImage(file="/mnt/data/6060e6c4-789d-4879-ad30-eb2c43ef7245.png")
        tk.Label(inicio, image=logo_img, bg=BG_COLOR).pack(pady=20)
    except:
        tk.Label(inicio, text="FamiWallet", font=FONT_HEADER, bg=BG_COLOR, fg=BTN_TEXT).pack(pady=20)
        logo_img = None

    tk.Label(
        inicio,
        text="Somos la familia:",
        font=FONT_HEADER,
        bg=BG_COLOR,
        fg=BTN_TEXT
    ).pack(pady=10)

    apellido_entry = tk.Entry(inicio, font=("Segoe UI", 18), justify="center")
    apellido_entry.pack(pady=10)

    def continuar():
        global apellido_familia
        apellido = apellido_entry.get().strip()

        if apellido == "":
            messagebox.showerror("Error", "Por favor ingresa un apellido.")
            return

        apellido_familia = apellido.upper()
        inicio.destroy()
        main()  # pasar a la interfaz real

    tk.Button(
        inicio,
        text="Continuar",
        font=FONT_MAIN,
        bg=BTN_COLOR,
        fg=BTN_TEXT,
        width=15,
        relief="flat",
        command=continuar
    ).pack(pady=30)

    inicio.mainloop()

# ------------------------------------
# AGREGAR GASTOS
# ------------------------------------
def abrir_ventana_agregar_gastos(parent):
    ventana_gastos = tk.Toplevel(parent)
    ventana_gastos.title("Agregar Gastos")
    ventana_gastos.geometry("500x500")
    ventana_gastos.config(bg=BG_COLOR)

    tk.Label(ventana_gastos, text="Formulario de Gastos", font=FONT_HEADER, fg=BTN_TEXT, bg=BG_COLOR).pack(pady=10)

    formulario_frame = tk.Frame(ventana_gastos, bg=BG_COLOR)
    formulario_frame.pack(pady=10)

    etiquetas = [
        "Fecha (DD/MM/AAAA):", "Ingreso mensual ($):",
        "Gasto - Luz ($):", "Gasto - Agua ($):",
        "Gasto - Internet ($):", "Gasto - Alimentos ($):",
        "Otros gastos ($):"
    ]

    entradas = []

    for i, texto in enumerate(etiquetas):
        tk.Label(formulario_frame, text=texto, bg=BG_COLOR, fg=BTN_TEXT, font=FONT_MAIN)\
            .grid(row=i, column=0, sticky="w", pady=5, padx=5)
        entrada = tk.Entry(formulario_frame, font=FONT_MAIN)
        entrada.grid(row=i, column=1, pady=5, padx=5)
        entradas.append(entrada)

    entradas[0].insert(0, datetime.now().strftime("%d/%m/%Y"))

    def guardar_datos():
        valores = [e.get().strip() for e in entradas]
        if not all(valores):
            messagebox.showerror("Error", "Por favor completa todos los campos.")
            return

        fecha = valores[0]
        try:
            ingreso = float(valores[1])
            gastos = {
                "Luz": float(valores[2]),
                "Agua": float(valores[3]),
                "Internet": float(valores[4]),
                "Alimentos": float(valores[5]),
                "Otros": float(valores[6]),
            }
        except ValueError:
            messagebox.showerror("Error", "Ingresa números válidos.")
            return

        datos_por_fecha[fecha] = {
            "Ingreso": ingreso,
            **gastos
        }

        messagebox.showinfo("Guardado", f"Gastos del {fecha} guardados correctamente.")
        ventana_gastos.destroy()

    tk.Button(
        ventana_gastos, text="Guardar", font=FONT_MAIN, bg=BTN_COLOR,
        fg=BTN_TEXT, relief="flat", width=15, command=guardar_datos
    ).pack(pady=20)

# ------------------------------------
# VISUALIZAR GASTOS
# ------------------------------------
def abrir_ventana_visualizar(parent):
    ventana = tk.Toplevel(parent)
    ventana.title("Visualizar Gastos por Fecha")
    ventana.geometry("600x600")
    ventana.config(bg=BG_COLOR)

    tk.Label(ventana, text="Selecciona fecha:", font=FONT_MAIN, bg=BG_COLOR, fg=BTN_TEXT).pack(pady=10)

    date_entry = DateEntry(ventana, font=FONT_MAIN, date_pattern='dd/mm/yyyy')
    date_entry.pack(pady=10)

    graf_frame = tk.Frame(ventana, bg=BG_COLOR)
    graf_frame.pack(pady=20, expand=True, fill="both")

    def mostrar_gastos_por_fecha():
        fecha = date_entry.get()
        if fecha not in datos_por_fecha:
            messagebox.showinfo("Sin datos", "No hay registros ese día.")
            return

        registro = datos_por_fecha[fecha]
        gastos = {k: v for k, v in registro.items() if k != "Ingreso"}

        for widget in graf_frame.winfo_children():
            widget.destroy()

        fig = plt.Figure(figsize=(5, 5))
        ax = fig.add_subplot(111)
        ax.pie(gastos.values(), labels=gastos.keys(), autopct="%1.1f%%")
        ax.set_title(f"Gastos del {fecha}")

        canvas = FigureCanvasTkAgg(fig, graf_frame)
        canvas.get_tk_widget().pack(expand=True, fill="both")
        canvas.draw()

    tk.Button(ventana, text="Mostrar", font=FONT_MAIN, bg=BTN_COLOR, fg=BTN_TEXT,
              width=20, command=mostrar_gastos_por_fecha).pack(pady=10)

# ------------------------------------
# RESUMEN GENERAL
# ------------------------------------
def abrir_resumen_general(parent):
    if not datos_por_fecha:
        messagebox.showinfo("Sin datos", "No hay información registrada.")
        return

    categorias = ["Luz", "Agua", "Internet", "Alimentos", "Otros"]
    suma = {c: 0 for c in categorias}
    total_ingresos = 0

    for registro in datos_por_fecha.values():
        total_ingresos += registro["Ingreso"]
        for c in categorias:
            suma[c] += registro[c]

    total_gastos = sum(suma.values())
    restante = total_ingresos - total_gastos

    ventana = tk.Toplevel(parent)
    ventana.title("Resumen General")
    ventana.geometry("620x650")
    ventana.config(bg=BG_COLOR)

    tk.Label(ventana, text="📋 Resumen General",
             font=FONT_HEADER, bg=BG_COLOR, fg=BTN_TEXT).pack(pady=20)

    texto = f"""
Total ingresos: ${total_ingresos:.2f}
Total gastos: ${total_gastos:.2f}
Dinero restante: ${restante:.2f}
"""

    tk.Label(ventana, text=texto, font=FONT_MAIN, bg=BG_COLOR, fg=BTN_TEXT).pack()

# ------------------------------------
# INTERFAZ PRINCIPAL
# ------------------------------------
def main():
    root = tk.Tk()
    root.title("Sistema Contable - FamiWallet")
    root.geometry("700x500")
    root.config(bg=BG_COLOR)

    # ---------------------------
    # BOTÓN "X" CON HOVER
    # ---------------------------
    btn_cerrar = tk.Button(
        root,
        text="✖",
        font=("Segoe UI", 16, "bold"),
        fg="black",
        bg=BG_COLOR,
        bd=0,
        command=root.destroy,
        cursor="hand2",
        activebackground=BG_COLOR
    )
    btn_cerrar.place(x=660, y=10)

    def on_enter(event):
        btn_cerrar.config(fg="white", bg="red")

    def on_leave(event):
        btn_cerrar.config(fg="black", bg=BG_COLOR)

    btn_cerrar.bind("<Enter>", on_enter)
    btn_cerrar.bind("<Leave>", on_leave)

    # ---------------------------

    header = tk.Frame(root, bg=BG_COLOR)
    header.pack(pady=20)

    tk.Label(header, text="FamiWallet", font=FONT_HEADER,
             bg=BG_COLOR, fg=BTN_TEXT).pack(side="left", padx=20)

    tk.Label(header,
             text=f"Bienvenida, familia {apellido_familia}",
             font=FONT_HEADER, bg=BG_COLOR, fg=BTN_TEXT).pack(side="left")

    menu = tk.Frame(root, bg=BG_COLOR)
    menu.pack(pady=40)

    def boton(texto, comando):
        return tk.Button(menu, text=texto, command=comando, font=FONT_MAIN,
                         width=25, height=2, bg=BTN_COLOR, fg=BTN_TEXT, relief="flat")

    boton("➕ Agregar Gastos", lambda: abrir_ventana_agregar_gastos(root)).pack(pady=10)
    boton("📊 Visualizar Gastos", lambda: abrir_ventana_visualizar(root)).pack(pady=10)
    boton("📋 Resumen General", lambda: abrir_resumen_general(root)).pack(pady=10)

    root.mainloop()

# ------------------------------------
# INICIO DEL PROGRAMA
# ------------------------------------
pantalla_inicio()
