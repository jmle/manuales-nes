# Manuales de NES en Español

Colección completa de manuales de instrucciones de Nintendo Entertainment System en español, preservados con fines educativos y de archivo.

## 📋 Contenido

- **281 manuales en PDF** de juegos de NES
- Manuales de hardware (consola, accesorios)
- Material publicitario de la época
- Sitio web de navegación con búsqueda y categorización
- **148 códigos de juego** extraídos mediante OCR

## 🌐 Sitio Web

Abre `index.html` en tu navegador para acceder a la colección completa con:

- Búsqueda de manuales
- Filtrado por categoría (Juegos, Hardware, Publicidad)
- Códigos de juego (ej: NES-B5-ESP, NES-MU-FRG)
- Diseño responsivo para móviles

## 🛠️ Scripts Incluidos

### 1. Descargador de Manuales

```bash
python download_nes_manuals.py
```

**Características:**
- Descarga todos los manuales desde MediaFire
- Rate limiting (3 segundos entre descargas)
- Resume capability (salta archivos existentes)
- Nombres de archivo en minúsculas con guiones

**Configuración:**
- `TEST_MODE = True/False` - Modo de prueba
- `DELAY_BETWEEN_DOWNLOADS = 3` - Segundos entre descargas

### 2. Extractor de Códigos (OCR)

```bash
python extract_codes.py
```

**Características:**
- Extrae códigos de juego de los PDFs mediante OCR
- Soporta múltiples códigos de país (ESP, FRG, NOE, EUR, etc.)
- Guarda resultados en `game_codes.json`
- Tasa de éxito: 52.7% (148 de 281 manuales)

**Requisitos:**
```bash
pip install PyMuPDF pytesseract pillow
sudo dnf install tesseract tesseract-langpack-eng  # Fedora
# o
sudo apt install tesseract-ocr  # Debian/Ubuntu
```

**Configuración:**
- `TEST_MODE = True/False` - Procesar todos o solo algunos PDFs
- `DPI = 300` - Resolución para OCR

## 📊 Estadísticas

- **Total de manuales:** 281
- **Juegos:** 267
- **Hardware:** 11
- **Publicidad:** 3
- **Códigos extraídos:** 148 (52.7%)
  - ESP (España): 105
  - FRG (Alemania): 38
  - NOE (Austria): 1
  - FRA (Francia): 1

## 🎮 Códigos de País

Los códigos de juego siguen el formato `NES-XX-CCC`:
- **ESP** - España
- **FRG** - Alemania Occidental (Bundesrepublik Deutschland)
- **NOE** - Austria (Nintendo of Europe)
- **EUR** - Europa
- **FRA** - Francia
- **ITA** - Italia
- **UKV** - Reino Unido
- **HOL** - Países Bajos

## 📁 Estructura del Proyecto

```
manuales-nes/
├── index.html                   # Sitio web principal
├── manuals/                     # PDFs de los manuales (281 archivos)
├── download_nes_manuals.py      # Script de descarga
├── extract_codes.py             # Script de extracción OCR
├── game_codes.json              # Códigos extraídos
├── README.md                    # Este archivo
└── LICENSE                      # Licencia CC BY-NC-SA 3.0
```

## 📜 Licencia

Este contenido está licenciado bajo [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)](https://creativecommons.org/licenses/by-nc-sa/3.0/).

**Esto significa que puedes:**
- ✅ Compartir - copiar y redistribuir el material en cualquier medio o formato
- ✅ Adaptar - remezclar, transformar y construir sobre el material

**Bajo los siguientes términos:**
- 📝 **Atribución** - Debes dar crédito apropiado, proporcionar un enlace a la licencia e indicar si se realizaron cambios
- 🚫 **No Comercial** - No puedes usar el material con fines comerciales
- 🔄 **Compartir Igual** - Si remezclas, transformas o construyes sobre el material, debes distribuir tus contribuciones bajo la misma licencia

## 🙏 Créditos

**Fuente original:** [WikiNES77 - Kaiserland77](https://www.kaiserland77.com/wikines77/index.php/Manuales_de_NES_en_Espa%C3%B1ol)

Estos manuales son propiedad de sus respectivos titulares de derechos de autor. Esta colección se mantiene únicamente con fines educativos, de preservación histórica y de archivo.

## 🤝 Contribuciones

Si tienes manuales adicionales o mejoras para los scripts, las contribuciones son bienvenidas.

## ⚠️ Aviso Legal

Este proyecto es una colección con fines educativos y de preservación histórica. Todos los manuales son propiedad de Nintendo y sus respectivos titulares de derechos de autor. No se pretende infringir ningún derecho de autor.

## 📧 Contacto

Para preguntas sobre la licencia o el uso de este material, consulta la [licencia CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).
