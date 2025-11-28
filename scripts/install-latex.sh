#!/bin/bash
# Script de instalación de LaTeX para WSL2
# Uso: bash scripts/install-latex.sh

set -e

echo "========================================="
echo "  INSTALACIÓN DE LATEX EN WSL2"
echo "========================================="
echo ""

# 1. Actualizar sistema
echo "[1/4] Actualizando sistema..."
sudo apt update

# 2. Instalar TeX Live (versión completa recomendada)
echo "[2/4] Instalando TeX Live..."
sudo apt install -y texlive-full

# 3. Instalar herramientas adicionales
echo "[3/4] Instalando herramientas adicionales..."
sudo apt install -y \
    latexmk \
    chktex \
    hunspell \
    hunspell-es

# 4. Verificar instalación
echo "[4/4] Verificando instalación..."
echo ""
echo "=== Versiones instaladas ==="
pdflatex --version | head -1
bibtex --version | head -1
chktex --version 2>&1 | head -1
echo ""

echo "========================================="
echo "  INSTALACIÓN COMPLETADA"
echo "========================================="
echo ""
echo "Próximos pasos:"
echo "1. Instala extensiones en VS Code:"
echo "   - LaTeX Workshop (James-Yu.latex-workshop)"
echo "   - LTeX+ (ltex-plus.ltex)"
echo ""
echo "2. Abre el proyecto y compila con Ctrl+Alt+B"
echo ""
