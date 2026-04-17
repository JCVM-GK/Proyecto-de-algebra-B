#!/usr/bin/env python3
"""
Simulador de Impedancia RLC - Versión Python/pygame-ce
Migrado desde C++/SFML
"""

import math
import sys
import os
import pygame #type: ignore

# ============================================
# CONSTANTES
# ============================================
PI = math.pi
WIDTH = 800
HEIGHT = 600
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2
MARGEN = 50
MAX_RADIO = 250

# Colores
COLOR_FONDO = (30, 30, 30)
COLOR_EJES = (100, 100, 100)
COLOR_VECTOR = (0, 200, 255)
COLOR_PUNTO = (255, 100, 34)  # Naranja #ff6422
COLOR_TEXTO = (255, 255, 255)
COLOR_GRID = (60, 60, 60)
COLOR_PANEL = (45, 45, 45)
COLOR_BOTON = (80, 80, 80)
COLOR_BOTON_HOVER = (110, 110, 110)


# ============================================
# CLASE COMPLEJO
# ============================================
class Complejo:
    """Representa un número complejo con parte real e imaginaria."""

    def __init__(self, real: float = 0.0, imaginaria: float = 0.0):
        self.real = real
        self.imaginaria = imaginaria

    def get_real(self) -> float:
        return self.real

    def get_imaginaria(self) -> float:
        return self.imaginaria

    def suma(self, otro: 'Complejo') -> 'Complejo':
        """Suma de complejos: (a + bi) + (c + di) = (a+c) + (b+d)i"""
        return Complejo(self.real + otro.real, self.imaginaria + otro.imaginaria)

    def resta(self, otro: 'Complejo') -> 'Complejo':
        """Resta de complejos: (a + bi) - (c + di) = (a-c) + (b-d)i"""
        return Complejo(self.real - otro.real, self.imaginaria - otro.imaginaria)

    def multiplicacion(self, otro: 'Complejo') -> 'Complejo':
        """Multiplicación: (a + bi) * (c + di) = (ac - bd) + (ad + bc)i"""
        nueva_real = self.real * otro.real - self.imaginaria * otro.imaginaria
        nueva_imaginaria = self.real * otro.imaginaria + self.imaginaria * otro.real
        return Complejo(nueva_real, nueva_imaginaria)

    def division(self, otro: 'Complejo') -> 'Complejo':
        """División: (a + bi) / (c + di) = [(ac + bd) + (bc - ad)i] / (c² + d²)"""
        denominador = otro.real * otro.real + otro.imaginaria * otro.imaginaria
        if denominador == 0.0:
            return Complejo(0.0, 0.0)
        nueva_real = (self.real * otro.real + self.imaginaria * otro.imaginaria) / denominador
        nueva_imaginaria = (self.imaginaria * otro.real - self.real * otro.imaginaria) / denominador
        return Complejo(nueva_real, nueva_imaginaria)

    def modulo(self) -> float:
        """Módulo (magnitud): |a + bi| = √(a² + b²)"""
        return math.sqrt(self.real * self.real + self.imaginaria * self.imaginaria)

    def argumento_radianes(self) -> float:
        """Argumento en radianes: θ = atan2(b, a)"""
        return math.atan2(self.imaginaria, self.real)

    def argumento_grados(self) -> float:
        """Argumento en grados"""
        return self.argumento_radianes() * 180.0 / PI

    def forma_polar(self) -> tuple[float, float]:
        """Retorna tupla (módulo, argumento en grados)"""
        return (self.modulo(), self.argumento_grados())

    def __str__(self) -> str:
        """Representación en string: a + bi o a - bi"""
        if self.imaginaria >= 0:
            return f"{self.real:.2f} + {self.imaginaria:.2f}i"
        else:
            return f"{self.real:.2f} - {-self.imaginaria:.2f}i"

    def __repr__(self) -> str:
        return f"Complejo({self.real}, {self.imaginaria})"


# ============================================
# CLASE COMPONENTE
# ============================================
class Componente:
    """Representa un componente electrónico (R, L o C)."""

    def __init__(self, tipo: str = 'R', valor: float = 0.0):
        """
        Args:
            tipo: 'R' para resistor, 'L' para inductor, 'C' para capacitor
            valor: Resistencia en ohmios, Inductancia en henrios, o Capacitancia en faradios
        """
        self.tipo = tipo.upper()
        self.valor = valor

    def get_tipo(self) -> str:
        return self.tipo

    def get_valor(self) -> float:
        return self.valor

    def impedancia(self, f: float) -> Complejo:
        """
        Calcula la impedancia del componente a una frecuencia dada.

        Args:
            f: Frecuencia en Hz

        Returns:
            Complejo representando la impedancia
        """
        if self.tipo == 'R':
            # Resistencia: Z = R + 0i
            return Complejo(self.valor, 0.0)
        elif self.tipo == 'L':
            # Inductor: Z = 0 + (2πfL)i
            xl = 2.0 * PI * f * self.valor
            return Complejo(0.0, xl)
        elif self.tipo == 'C':
            # Capacitor: Z = 0 - (1/2πfC)i
            xc = 1.0 / (2.0 * PI * f * self.valor)
            return Complejo(0.0, -xc)
        else:
            return Complejo(0.0, 0.0)

    def __str__(self) -> str:
        unidades = {'R': 'Ω', 'L': 'H', 'C': 'F'}
        nombres = {'R': 'Resistor', 'L': 'Inductor', 'C': 'Capacitor'}
        return f"{nombres[self.tipo]}: {self.valor} {unidades[self.tipo]}"


# ============================================
# CLASE CIRCUITO
# ============================================
class Circuito:
    """Representa un circuito con componentes en serie."""

    MAX_COMPONENTES = 10

    def __init__(self):
        self.componentes: list[Componente] = []

    def agregar_componente(self, comp: Componente) -> bool:
        """
        Agrega un componente al circuito.

        Returns:
            True si se agregó correctamente, False si se alcanzó el límite
        """
        if len(self.componentes) >= self.MAX_COMPONENTES:
            return False
        self.componentes.append(comp)
        return True

    def impedancia_total(self, f: float) -> Complejo:
        """
        Calcula la impedancia total del circuito en serie.

        Args:
            f: Frecuencia en Hz

        Returns:
            Complejo con la impedancia total
        """
        total = Complejo(0.0, 0.0)
        for comp in self.componentes:
            total = total.suma(comp.impedancia(f))
        return total

    def get_cantidad(self) -> int:
        return len(self.componentes)

    def get_componentes(self) -> list[Componente]:
        return self.componentes.copy()


# ============================================
# CLASE VISUALIZADOR PYGAME
# ============================================
class VisualizadorPygame:
    """Visualizador gráfico del simulador usando pygame-ce."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simulador de Impedancia - Circuito RLC")
        self.clock = pygame.time.Clock()

        # Cargar fuentes
        self.font_titulo = self._cargar_fuente(24)
        self.font_info = self._cargar_fuente(18)
        self.font_instrucciones = self._cargar_fuente(14)
        self.font_small = self._cargar_fuente(12)

        self.escala = 1.0
        self.controles_ui = self._crear_controles_ui()

    def _crear_controles_ui(self) -> dict[str, pygame.Rect]:
        """Crea botones del panel gráfico para cambiar variables."""
        panel_x = WIDTH - 190
        base_y = 90
        gap = 45
        w, h = 32, 26
        return {
            "freq_minus": pygame.Rect(panel_x + 65, base_y + gap * 0, w, h),
            "freq_plus": pygame.Rect(panel_x + 105, base_y + gap * 0, w, h),
            "r_minus": pygame.Rect(panel_x + 65, base_y + gap * 1, w, h),
            "r_plus": pygame.Rect(panel_x + 105, base_y + gap * 1, w, h),
            "l_minus": pygame.Rect(panel_x + 65, base_y + gap * 2, w, h),
            "l_plus": pygame.Rect(panel_x + 105, base_y + gap * 2, w, h),
            "c_minus": pygame.Rect(panel_x + 65, base_y + gap * 3, w, h),
            "c_plus": pygame.Rect(panel_x + 105, base_y + gap * 3, w, h),
        }

    def _cargar_fuente(self, tamano: int) -> pygame.font.Font:
        """Intenta cargar una fuente del sistema, o usa la fuente por defecto de pygame."""
        # Intentar fuentes comunes del sistema
        fuentes_sistema = [
            "Arial",
            "Segoe UI",
            "Calibri",
            "Helvetica",
            "DejaVu Sans",
            "Liberation Sans",
        ]

        for fuente_nombre in fuentes_sistema:
            try:
                return pygame.font.SysFont(fuente_nombre, tamano)
            except:
                continue

        # Fallback a fuente por defecto
        return pygame.font.Font(None, tamano)

    def calcular_escala(self, z: Complejo):
        """Calcula la escala automática para que el vector quepa en pantalla."""
        max_valor = max(abs(z.get_real()), abs(z.get_imaginaria()))
        if max_valor < 1.0:
            max_valor = 1.0
        self.escala = MAX_RADIO / max_valor

    def dibujar_cuadricula(self):
        """Dibuja la cuadrícula de fondo."""
        pasos = 5
        espaciado = MAX_RADIO / pasos

        for i in range(-pasos, pasos + 1):
            if i == 0:
                continue

            # Líneas verticales
            x = CENTER_X + i * espaciado
            pygame.draw.line(
                self.screen, COLOR_GRID,
                (x, MARGEN + 30),
                (x, HEIGHT - MARGEN)
            )

            # Líneas horizontales
            y = CENTER_Y + i * espaciado
            pygame.draw.line(
                self.screen, COLOR_GRID,
                (MARGEN, y),
                (WIDTH - MARGEN, y)
            )

    def dibujar_ejes(self):
        """Dibuja los ejes X (real) e Y (imaginario)."""
        # Eje X (Real)
        pygame.draw.line(
            self.screen, COLOR_EJES,
            (MARGEN, CENTER_Y),
            (WIDTH - MARGEN, CENTER_Y),
            2
        )

        # Eje Y (Imaginario)
        pygame.draw.line(
            self.screen, COLOR_EJES,
            (CENTER_X, MARGEN + 30),
            (CENTER_X, HEIGHT - MARGEN),
            2
        )

        # Etiquetas de ejes
        label_re = self.font_small.render("Re (Z)", True, COLOR_EJES)
        self.screen.blit(label_re, (WIDTH - MARGEN - 50, CENTER_Y + 10))

        label_im = self.font_small.render("Im (Z)", True, COLOR_EJES)
        self.screen.blit(label_im, (CENTER_X + 10, MARGEN + 30))

    def dibujar_vector(self, z: Complejo):
        """Dibuja el vector del número complejo desde el origen."""
        x = CENTER_X + z.get_real() * self.escala
        y = CENTER_Y - z.get_imaginaria() * self.escala  # Invertir Y

        # Vector desde el origen hasta el punto Z
        pygame.draw.line(
            self.screen, COLOR_VECTOR,
            (CENTER_X, CENTER_Y),
            (int(x), int(y)),
            3
        )

        # Punto Z (círculo naranja)
        pygame.draw.circle(self.screen, COLOR_PUNTO, (int(x), int(y)), 8)

        # Punto en el origen (referencia)
        pygame.draw.circle(self.screen, COLOR_TEXTO, (CENTER_X, CENTER_Y), 4)

    def dibujar_texto_info(self, frecuencia: float, z: Complejo, r: float, l: float, c: float):
        """Dibuja el panel de información en la pantalla."""
        mod, arg = z.forma_polar()

        # Título
        titulo = self.font_titulo.render(
            "Simulador de Impedancia - Circuito RLC", True, COLOR_PUNTO
        )
        self.screen.blit(titulo, (20, 10))

        # Información del circuito
        lineas_info = [
            f"Frecuencia: {frecuencia:.2f} Hz",
            "",
            "Componentes:",
            f"  R = {r} ohm",
            f"  L = {l} H",
            f"  C = {c} F",
            "",
            "Impedancia Total:",
            f"  Rectangular: {z.get_real():.2f} + {z.get_imaginaria():.2f}i ohm",
            f"  Polar: {mod:.2f} ohm ∠ {arg:.2f}°",
        ]

        y_offset = 50
        for linea in lineas_info:
            texto = self.font_info.render(linea, True, COLOR_TEXTO)
            self.screen.blit(texto, (20, y_offset))
            y_offset += 22

    def dibujar_instrucciones(self):
        """Dibuja las instrucciones de control."""
        lineas = [
            "Controles de Simulacion:",
            "  Flechas IZQ/DER: +/- Frecuencia",
            "  Teclas R / E   : +/- Resistencia (R)",
            "  Teclas L / K   : +/- Inductancia (L)",
            "  Teclas C / X   : +/- Capacitancia (C)",
            "  Clic en panel  : botones +/- GUI",
            "  ESC: Salir"
        ]

        y_offset = HEIGHT - 160
        for linea in lineas:
            texto = self.font_instrucciones.render(linea, True, (200, 200, 200))
            self.screen.blit(texto, (WIDTH - 250, y_offset))
            y_offset += 20

    def dibujar_panel_controles(self):
        """Dibuja panel gráfico con botones +/- para F, R, L, C."""
        panel_rect = pygame.Rect(WIDTH - 200, 60, 170, 220)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_EJES, panel_rect, width=1, border_radius=8)

        titulo = self.font_instrucciones.render("Controles GUI", True, COLOR_TEXTO)
        self.screen.blit(titulo, (panel_rect.x + 12, panel_rect.y + 8))

        labels = [("F", 0), ("R", 1), ("L", 2), ("C", 3)]
        mouse_pos = pygame.mouse.get_pos()
        for letra, idx in labels:
            y = 90 + idx * 45
            label = self.font_instrucciones.render(letra, True, COLOR_TEXTO)
            self.screen.blit(label, (panel_rect.x + 16, y + 4))

            minus_key = f"{letra.lower()}_minus" if letra != "F" else "freq_minus"
            plus_key = f"{letra.lower()}_plus" if letra != "F" else "freq_plus"
            for key, txt in ((minus_key, "-"), (plus_key, "+")):
                rect = self.controles_ui[key]
                color = COLOR_BOTON_HOVER if rect.collidepoint(mouse_pos) else COLOR_BOTON
                pygame.draw.rect(self.screen, color, rect, border_radius=5)
                pygame.draw.rect(self.screen, COLOR_EJES, rect, width=1, border_radius=5)
                t = self.font_info.render(txt, True, COLOR_TEXTO)
                self.screen.blit(t, (rect.x + 10, rect.y - 1))

    def render(self, frecuencia: float, z: Complejo, r: float, l: float, c: float):
        """Renderiza un frame completo."""
        self.screen.fill(COLOR_FONDO)

        # Calcular escala automática
        self.calcular_escala(z)

        # Dibujar elementos
        self.dibujar_cuadricula()
        self.dibujar_ejes()
        self.dibujar_vector(z)

        # Dibujar textos
        self.dibujar_texto_info(frecuencia, z, r, l, c)
        self.dibujar_panel_controles()
        self.dibujar_instrucciones()

        pygame.display.flip()

    def handle_events(self) -> tuple[bool, float, float, float, float]:
        """
        Retorna: (continuar, d_frecuencia, d_R, d_L, d_C)
        """
        d_freq, d_r, d_l, d_c = 0.0, 0.0, 0.0, 0.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, 0.0, 0.0, 0.0, 0.0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, 0.0, 0.0, 0.0, 0.0
                
                # Controles de Frecuencia (Flechas)
                elif event.key == pygame.K_RIGHT: d_freq = 10.0
                elif event.key == pygame.K_LEFT: d_freq = -10.0

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.controles_ui["freq_plus"].collidepoint(pos): d_freq += 10.0
                elif self.controles_ui["freq_minus"].collidepoint(pos): d_freq -= 10.0
                elif self.controles_ui["r_plus"].collidepoint(pos): d_r += 1.0
                elif self.controles_ui["r_minus"].collidepoint(pos): d_r -= 1.0
                elif self.controles_ui["l_plus"].collidepoint(pos): d_l += 0.001
                elif self.controles_ui["l_minus"].collidepoint(pos): d_l -= 0.001
                elif self.controles_ui["c_plus"].collidepoint(pos): d_c += 0.00001
                elif self.controles_ui["c_minus"].collidepoint(pos): d_c -= 0.00001

        return True, d_freq, d_r, d_l, d_c

    def tick(self, fps: int = 60):
        """Limita el framerate."""
        self.clock.tick(fps)


# ============================================
# FUNCIONES AUXILIARES
# ============================================
def pedir_valor_consola(prompt: str, valor_default: float) -> float:
    """Pide un valor al usuario con un valor por defecto."""
    try:
        entrada = input(f"{prompt} [default {valor_default}]: ").strip()
        if entrada:
            return float(entrada)
        return valor_default
    except ValueError:
        print(f"Valor inválido. Usando default: {valor_default}")
        return valor_default


def dibujar_plano_ascii(z: Complejo):
    """Dibuja el plano complejo usando ASCII art (versión consola)."""
    TAMANO = 21
    CENTRO = TAMANO // 2
    EJE_X = '-'
    EJE_Y = '|'
    ORIGEN = '+'
    PUNTO = '*'
    VACIO = ' '

    # Calcular escala
    max_valor = max(abs(z.get_real()), abs(z.get_imaginaria()))
    if max_valor < 0.001:
        max_valor = 1.0

    escala = max_valor / (CENTRO - 1)

    # Convertir coordenadas
    col = CENTRO + int(z.get_real() / escala + 0.5)
    fila = CENTRO - int(z.get_imaginaria() / escala + 0.5)

    # Limitar a bordes
    col = max(0, min(TAMANO - 1, col))
    fila = max(0, min(TAMANO - 1, fila))

    # Crear cuadrícula
    cuadricula = [[VACIO for _ in range(TAMANO)] for _ in range(TAMANO)]

    # Dibujar ejes
    for i in range(TAMANO):
        cuadricula[CENTRO][i] = EJE_X
        cuadricula[i][CENTRO] = EJE_Y
    cuadricula[CENTRO][CENTRO] = ORIGEN

    # Marcar punto Z
    cuadricula[fila][col] = PUNTO

    # Imprimir
    print("\n=== Plano Complejo ===")
    print(f"Escala: 1 caracter = {escala:.4f} unidades\n")
    print("  Im↑")

    for i in range(TAMANO):
        margen = "Re← " if i == CENTRO else "    "
        print(margen, end="")
        for j in range(TAMANO):
            print(cuadricula[i][j], end="")

        # Etiquetas derechas
        if i == 0:
            print("  ↑+Im")
        elif i == CENTRO:
            print("  →+Re")
        elif i == TAMANO - 1:
            print("  ↓-Im")
        else:
            print()

    print("    " + " " * CENTRO + "↓" + " " * (TAMANO - CENTRO - 1) + "  -Im")
    print(f"\nCoordenadas de Z: ({z.get_real():.4f}, {z.get_imaginaria():.4f})")


def mostrar_tabla_frecuencias(circuito: Circuito, r: float, l: float, c: float, freq_actual: float):
    """Muestra una tabla de impedancias para diferentes frecuencias."""
    frecuencias = [10, 20, 30, 60, 100, 200, 500, 1000]

    # Encontrar índice más cercano
    indice_cercano = min(range(len(frecuencias)),
                         key=lambda i: abs(frecuencias[i] - freq_actual))

    print("\n=== Variación de Impedancia con la Frecuencia ===")
    print(f"(R = {r} Ω, L = {l} H, C = {c} F)\n")

    print("|----------|-----------|-------------|-----------|----------|")
    print("|  f (Hz)  |   Re(Z)   |    Im(Z)    |   |Z|    |  θ (°)   |")
    print("|----------|-----------|-------------|-----------|----------|")

    for i, freq in enumerate(frecuencias):
        z = circuito.impedancia_total(freq)
        mod, arg = z.forma_polar()

        marcador = " <--" if i == indice_cercano else ""

        print(f"| {freq:8} | {z.get_real():9.2f} | {z.get_imaginaria():11.2f} | "
              f"{mod:9.2f} | {arg:8.2f} |{marcador}")

    print("|----------|-----------|-------------|-----------|----------|")
    print(f"\nNota: La flecha <-- indica la frecuencia más cercana a la ingresada "
          f"({freq_actual} Hz)")


# ============================================
# MODO CONSOLA (sin pygame)
# ============================================
def modo_consola():
    """Ejecuta el simulador en modo consola sin gráficos."""
    print("=== Análisis Interactivo de Circuito RLC en Serie ===\n")

    # Pedir valores
    r = float(input("Ingrese el valor de R (ohms): "))
    l = float(input("Ingrese el valor de L (henrios): "))
    c = float(input("Ingrese el valor de C (farads): "))
    frecuencia = float(input("Ingrese la frecuencia f (Hz): "))

    print("\n" + "=" * 50)

    # Crear circuito
    circuito = Circuito()
    circuito.agregar_componente(Componente('R', r))
    circuito.agregar_componente(Componente('L', l))
    circuito.agregar_componente(Componente('C', c))

    # Mostrar componentes
    print("\nComponentes del circuito:")
    print(f"  Resistor: R = {r} Ω")
    print(f"  Inductor: L = {l} H")
    print(f"  Capacitor: C = {c} F")
    print(f"  Frecuencia: f = {frecuencia} Hz")

    # Calcular impedancias individuales
    print("\nImpedancias individuales:")
    for comp in circuito.get_componentes():
        z = comp.impedancia(frecuencia)
        print(f"  Z_{comp.get_tipo()} = {z}")

    # Calcular impedancia total
    z_total = circuito.impedancia_total(frecuencia)
    mod, arg = z_total.forma_polar()

    print("\n=== Impedancia Total del Circuito ===")
    print(f"Forma rectangular: Z_total = {z_total}")
    print(f"Forma polar: Z_total = {mod:.2f} ∠ {arg:.2f}°")

    # Dibujar plano ASCII
    dibujar_plano_ascii(z_total)

    # Mostrar tabla de frecuencias
    mostrar_tabla_frecuencias(circuito, r, l, c, frecuencia)


# ============================================
# MAIN
# ============================================
def main():
    """Función principal del programa."""
    import argparse

    parser = argparse.ArgumentParser(description="Simulador de Impedancia RLC")
    parser.add_argument(
        "--consola", "-c",
        action="store_true",
        help="Ejecutar en modo consola sin gráficos"
    )
    parser.add_argument(
        "--r", type=float, default=100.0,
        help="Resistencia en ohmios (default: 100)"
    )
    parser.add_argument(
        "--l", type=float, default=0.01,
        help="Inductancia en henrios (default: 0.01)"
    )
    parser.add_argument(
        "--c", type=float, default=0.0001,
        help="Capacitancia en faradios (default: 0.0001)"
    )
    parser.add_argument(
        "--freq", type=float, default=60.0,
        help="Frecuencia inicial en Hz (default: 60)"
    )

    args = parser.parse_args()

    # Modo consola
    if args.consola:
        modo_consola()
        return

    # Modo gráfico (pygame)
    print("=== Simulador de Impedancia RLC (Modo Gráfico pygame-ce) ===")
    print("Presione ESC para salir\n")

    # Usar valores de línea de comandos o pedir por consola
# Usar valores de línea de comandos o pedir por consola
    # Cambiamos la verificación para evitar el error si sys.stdin es None
    r, l, c, frecuencia = args.r, args.l, args.c, args.freq

    # Crear visualizador
    visualizador = VisualizadorPygame()
    circuito = Circuito()

    # Bucle principal
    ejecutando = True
    while ejecutando:
        # Manejo de eventos independiente de la terminal
        continuar, delta_f, delta_r, delta_l, delta_c = visualizador.handle_events()
        if not continuar:
            break

        # Captura de teclas para R, L, C
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            r += 1.0
        if keys[pygame.K_e]:
            r = max(0.1, r - 1.0)
        if keys[pygame.K_l]:
            l += 0.001
        if keys[pygame.K_k]:
            l = max(0.001, l - 0.001)
        if keys[pygame.K_c]:
            c += 0.00001
        if keys[pygame.K_x]:
            c = max(0.00001, c - 0.00001)

        frecuencia = max(1.0, frecuencia + delta_f)
        r = max(0.1, r + delta_r)
        l = max(0.001, l + delta_l)
        c = max(0.00001, c + delta_c)

        # Re-crear o actualizar componentes del circuito
        circuito = Circuito()
        circuito.agregar_componente(Componente('R', r))
        circuito.agregar_componente(Componente('L', l))
        circuito.agregar_componente(Componente('C', c))

        z_total = circuito.impedancia_total(frecuencia)
        visualizador.render(frecuencia, z_total, r, l, c)
        visualizador.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
