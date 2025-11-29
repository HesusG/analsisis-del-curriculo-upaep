# Export Slidev slides to PDF
# Requires: Node.js, npm, and Playwright

Write-Host "Exportando slides a PDF..." -ForegroundColor Cyan

# Navigate to slides directory
Set-Location -Path "$PSScriptRoot\slides"

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    npm install
}

# Install Playwright browsers if needed
Write-Host "Verificando Playwright..." -ForegroundColor Yellow
npx playwright install chromium --with-deps 2>$null

# Export to PDF
Write-Host "Generando PDF..." -ForegroundColor Yellow
npm run export:pdf

# Check if export was successful
$pdfPath = ".\slides.pdf"
if (Test-Path $pdfPath) {
    # Move to root with better name
    $destination = "$PSScriptRoot\slides-presentacion.pdf"
    Move-Item -Path $pdfPath -Destination $destination -Force
    Write-Host "`nPDF generado exitosamente: $destination" -ForegroundColor Green
} else {
    Write-Host "`nError: No se pudo generar el PDF" -ForegroundColor Red
    Write-Host "Intenta ejecutar manualmente: cd slides && npm run export" -ForegroundColor Yellow
}

Set-Location -Path $PSScriptRoot
