#!/usr/bin/env python3
"""Genera gráfica SVG para la validación con IA - datos del documento LaTeX."""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Configuración de estilo
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

# Datos CORRECTOS del documento LaTeX (Table 18, página 28)
# Ordenados de mayor a menor promedio para mejor visualización
dimensiones = [
    'Conexión\nTeoría-Práctica',
    'Rol del\nEstudiante',
    'Coherencia\nEpistemológica',
    'Reflexión\nCrítica',
    'Evaluación del\nAprendizaje',
    'Integración\nTecnológica'
]
puntuaciones = [8.0, 7.5, 7.0, 6.0, 5.75, 5.5]

# Colores: verde para fortalezas (≥7), amarillo para medio (6-6.9), rojo para debilidades (<6)
colores = ['#22c55e', '#22c55e', '#22c55e', '#f59e0b', '#ef4444', '#dc2626']

# Crear figura
fig, ax = plt.subplots(figsize=(10, 5))

# Barras horizontales
bars = ax.barh(dimensiones, puntuaciones, color=colores, height=0.6, edgecolor='white', linewidth=1.5)

# Agregar valores al final de cada barra
for bar, score in zip(bars, puntuaciones):
    ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
            f'{score:.2f}' if score != int(score) else f'{score:.1f}',
            va='center', ha='left', fontsize=12, fontweight='bold', color='#374151')

# Configuración de ejes
ax.set_xlim(0, 10)
ax.set_xlabel('Puntuación (escala 1-10)', fontsize=11, color='#6b7280')
ax.set_title('Puntuaciones Consolidadas del Panel de Agentes IA', fontsize=14, fontweight='bold', color='#1f2937', pad=15)

# Línea de referencia en 7 (umbral de "aceptable")
ax.axvline(x=7, color='#9ca3af', linestyle='--', linewidth=1, alpha=0.7)
ax.text(7.1, -0.5, 'Umbral', fontsize=9, color='#9ca3af', style='italic')

# Estilo de grid
ax.xaxis.grid(True, linestyle='-', alpha=0.3)
ax.yaxis.grid(False)

# Remover bordes
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_color('#e5e7eb')
ax.spines['bottom'].set_color('#e5e7eb')

# Invertir eje Y para que la mayor puntuación esté arriba
ax.invert_yaxis()

# Ajustar layout
plt.tight_layout()

# Guardar como SVG
plt.savefig('/mnt/c/Users/HG_Co/OneDrive/Documents/Github/analsisis-del-curriculo-upaep/slides/assets/validacion_ia_chart.svg',
            format='svg', bbox_inches='tight', transparent=True)

print("✓ Gráfica corregida guardada en slides/assets/validacion_ia_chart.svg")
print("\nDatos utilizados (del documento LaTeX Table 18):")
for dim, score in zip(dimensiones, puntuaciones):
    print(f"  {dim.replace(chr(10), ' ')}: {score}")
