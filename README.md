# Aplicación de Kardex y etiquetas de almacén

Aplicación web sencilla en Flask para controlar el inventario de un almacén de construcción modular. Incluye Kardex en Excel, generación de etiquetas con código de barras y registro de movimientos por lectura de scanner.

## Requisitos
- Python 3.11+
- Dependencias de `requirements.txt`

Instalación rápida:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Datos de muestra
Se incluyen 200 ítems de ejemplo generados por `scripts/seed_data.py`. Si necesitas regenerarlos:
```bash
python scripts/seed_data.py
```

## Ejecutar la aplicación
```bash
flask --app app run --debug
```
La app quedará disponible en `http://localhost:5000`.

## Funcionalidades
- **Listado de inventario**: consulta rápida con stock y ubicación.
- **Lectura de código de barras**: ingresa o retira cantidades con el formulario (compatible con scanner).
- **Kardex Excel**: descarga un archivo con ítems y movimientos registrados.
- **Etiquetas**: cada ítem genera un código de barras Code128 listo para imprimir en impresora térmica.
