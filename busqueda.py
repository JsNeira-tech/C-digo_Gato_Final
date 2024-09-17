import random
from tkinter import *
from tkinter import messagebox, simpledialog

class JuegoGato:
    def __init__(self, estado=[0]*9, turno=-1):
        self.tablero = estado
        self.completo = False
        self.ganador = None
        self.jugador = turno

    def reiniciar(self):
        self.tablero = [0]*9
        self.completo = False
        self.ganador = None
        self.jugador = -1

    def generar_jugadas_posibles(self):
        return [i for i in range(9) if self.tablero[i] == 0]

    def estado_final(self):
        self.evaluar()
        return self.ganador is not None or self.completo

    def evaluar(self):
        if 0 not in self.tablero:
            self.completo = True
        else:
            self.completo = False
        estado = []
        for i in [0,3,6]:
            estado.append(sum(self.tablero[i:i+3]))
        for i in [0,1,2]:
            estado.append(self.tablero[i]+self.tablero[i+3]+self.tablero[i+6])
        estado.append(self.tablero[0]+self.tablero[4]+self.tablero[8])
        estado.append(self.tablero[2]+self.tablero[4]+self.tablero[6])
        for valor in estado:
            if valor == 3 or valor == -3:
                self.ganador = valor//3
                return
        if self.completo:
            self.ganador = 0
        else:
            self.ganador = None

    def calcular_utilidad(self):
        return self.ganador

    def jugar(self, jugada):
        self.tablero[jugada] = self.jugador
        self.jugador *= -1

    def deshacer_jugada(self, jugada):
        self.tablero[jugada] = 0
        self.jugador *= -1

def minimax(juego, etapa, alpha=-float('inf'), beta=float('inf'), profundidad=0, max_profundidad=9):
    if profundidad >= max_profundidad or juego.estado_final():
        utilidad = juego.calcular_utilidad()
        return utilidad if utilidad is not None else 0, None

    mejor_jugada = None
    if etapa == 1:  # Maximizando (turno del Gato)
        mejor_valor = -float('inf')
        for jugada in juego.generar_jugadas_posibles():
            juego.jugar(jugada)
            valor, _ = minimax(juego, -1, alpha, beta, profundidad + 1, max_profundidad)
            juego.deshacer_jugada(jugada)
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_jugada = jugada
            alpha = max(alpha, mejor_valor)
            if beta <= alpha:
                break
        return mejor_valor, mejor_jugada
    else:  # Minimizando (turno del Ratón)
        mejor_valor = float('inf')
        for jugada in juego.generar_jugadas_posibles():
            juego.jugar(jugada)
            valor, _ = minimax(juego, 1, alpha, beta, profundidad + 1, max_profundidad)
            juego.deshacer_jugada(jugada)
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_jugada = jugada
            beta = min(beta, mejor_valor)
            if beta <= alpha:
                break
        return mejor_valor, mejor_jugada

def elegir_jugada(juego, dificultad):
    if dificultad == "fácil":
        return random.choice(juego.generar_jugadas_posibles())
    elif dificultad == "medio":
        _, jugada = minimax(juego, 1, max_profundidad=3)
        return jugada
    else:  # difícil
        _, jugada = minimax(juego, 1)
        return jugada

class Gato:
    def __init__(self):
        self.principal = Tk()
        self.principal.withdraw()  # Oculta la ventana principal temporalmente
        self.dificultad = simpledialog.askstring("Dificultad", "Elige la dificultad (fácil/medio/difícil):", 
                                                 initialvalue="medio")
        if self.dificultad not in ["fácil", "medio", "difícil"]:
            self.dificultad = "medio"
        
        self.principal.deiconify()  # Muestra la ventana principal
        self.principal.title("Gato")
        self.botones = []
        self.gato = PhotoImage(file="gato.gif")
        self.raton = PhotoImage(file="raton.gif")
        self.vacio = PhotoImage(file="vacio.gif")
        self.empate_png = PhotoImage(file="empate.png")
        self.perdio_png = PhotoImage(file="perdio.png")
        self.juego = JuegoGato()
        
        for i in range(3):
            fila = []
            for j in range(3):
                b1 = Button(self.principal, image=self.vacio, width=80, height=80)
                b1.bind("<Button-1>", self.click)
                b1.grid(row=i, column=j)
                fila.append(b1)
            self.botones.append(fila)
        
        # Centrar la ventana en la pantalla
        self.principal.update_idletasks()
        width = self.principal.winfo_width()
        height = self.principal.winfo_height()
        x = (self.principal.winfo_screenwidth() // 2) - (width // 2)
        y = (self.principal.winfo_screenheight() // 2) - (height // 2)
        self.principal.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def reiniciar_juego(self):
        self.juego.reiniciar()
        for i in range(3):
            for j in range(3):
                self.botones[i][j]["image"] = self.vacio
        
        # Cerrar todas las ventanas Toplevel abiertas
        for widget in self.principal.winfo_children():
            if isinstance(widget, Toplevel):
                widget.destroy()
    
    def mostrar_resultado(self):
        if self.juego.ganador == -1:
            messagebox.showinfo("Juego del Gato", "Has ganado!")
            self.reiniciar_juego()
        else:
            ventana_resultado = Toplevel(self.principal)
            ventana_resultado.transient(self.principal)
            ventana_resultado.grab_set()
            
            # Calcular la posición para la ventana de resultado
            x = self.principal.winfo_x() + self.principal.winfo_width() + 10
            y = self.principal.winfo_y()
            
            # Asegurar que la ventana de resultado esté dentro de la pantalla
            if x + 200 > self.principal.winfo_screenwidth():  # 200 es un ancho estimado para la ventana de resultado
                x = self.principal.winfo_x() - 210  # Colocar a la izquierda si no cabe a la derecha
            
            ventana_resultado.geometry(f"+{x}+{y}")
            
            if self.juego.ganador == 0:
                ventana_resultado.title("Empate")
                Label(ventana_resultado, image=self.empate_png).pack(pady=10)
                Label(ventana_resultado, text="Empate").pack()
            else:
                ventana_resultado.title("Has perdido")
                Label(ventana_resultado, image=self.perdio_png).pack(pady=10)
                Label(ventana_resultado, text="Has perdido").pack()
            
            Button(ventana_resultado, text="Cerrar", command=lambda: self.cerrar_y_reiniciar(ventana_resultado)).pack(pady=10)
    
    def cerrar_y_reiniciar(self, ventana):
        ventana.destroy()
        self.reiniciar_juego()
    
    def click(self, evento):
        fila = evento.widget.grid_info()['row']
        columna = evento.widget.grid_info()['column']
        indice = fila * 3 + columna
        if not self.juego.estado_final() and self.juego.tablero[indice] == 0:
            self.juego.jugar(indice)
            evento.widget["image"] = self.raton
            if self.juego.estado_final():
                self.mostrar_resultado()
            else:
                jugada = elegir_jugada(self.juego, self.dificultad)
                self.juego.jugar(jugada)
                self.botones[jugada//3][jugada%3]["image"] = self.gato
                if self.juego.estado_final():
                    self.mostrar_resultado()

if __name__ == "__main__":
    juego = Gato()
    juego.principal.mainloop()