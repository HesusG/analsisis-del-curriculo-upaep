#!/usr/bin/env python3
"""Genera una imagen de mockup de diálogo con IA para la presentación."""

from PIL import Image, ImageDraw, ImageFont
import textwrap

# Dimensiones
WIDTH = 800
HEIGHT = 600

# Colores
BG_COLOR = (249, 250, 251)  # gray-50
USER_BG = (219, 234, 254)   # blue-100
AI_BG = (220, 252, 231)     # green-100
USER_TEXT = (30, 64, 175)   # blue-800
AI_TEXT = (22, 101, 52)     # green-800
GRAY = (107, 114, 128)

# Crear imagen
img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

# Intentar cargar fuente, si no usar default
try:
    font_regular = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    font_regular = ImageFont.load_default()
    font_bold = font_regular
    font_small = font_regular

# Título
draw.text((40, 30), "Diálogo Socrático con IA", fill=(31, 41, 55), font=font_bold)
draw.text((40, 55), "GPT programado como cuestionador ético", fill=GRAY, font=font_small)

# Mensajes del diálogo
messages = [
    ("user", "Mi equipo propone segmentar el mercado por nivel\nsocioeconómico alto (NSE A/B) para productos premium."),
    ("ai", "Interesante propuesta. Antes de avanzar, reflexionemos:\n¿Quién queda excluido de este segmento?\n¿Qué implicaciones tiene priorizar solo a consumidores\nde alto poder adquisitivo?"),
    ("user", "Bueno, quedan fuera las personas de ingresos medios\ny bajos... no habíamos pensado en eso."),
    ("ai", "Exacto. Ahora pregunto: ¿Qué sesgos podría tener\nesta clasificación? ¿El NSE define completamente las\nnecesidades del consumidor?"),
]

y_pos = 100
padding = 15

for sender, text in messages:
    # Calcular altura del texto
    lines = text.split('\n')
    text_height = len(lines) * 22 + padding * 2

    if sender == "user":
        # Mensaje del usuario (derecha)
        bubble_width = 450
        x_start = WIDTH - bubble_width - 40
        color = USER_BG
        text_color = USER_TEXT
        label = "Estudiante"
    else:
        # Mensaje de la IA (izquierda)
        bubble_width = 480
        x_start = 40
        color = AI_BG
        text_color = AI_TEXT
        label = "GPT Socrático"

    # Dibujar etiqueta
    draw.text((x_start, y_pos - 18), label, fill=GRAY, font=font_small)

    # Dibujar burbuja
    draw.rounded_rectangle(
        [x_start, y_pos, x_start + bubble_width, y_pos + text_height],
        radius=12,
        fill=color
    )

    # Dibujar texto
    y_text = y_pos + padding
    for line in lines:
        draw.text((x_start + padding, y_text), line, fill=text_color, font=font_regular)
        y_text += 22

    y_pos += text_height + 35

# Nota al pie
draw.text((40, HEIGHT - 40),
          "El GPT no da respuestas directas, guía al estudiante a descubrirlas.",
          fill=GRAY, font=font_small)

# Guardar
img.save('/mnt/c/Users/HG_Co/OneDrive/Documents/Github/analsisis-del-curriculo-upaep/slides/images/dialogo-ia.png', 'PNG')
print("✓ Imagen generada: dialogo-ia.png")
