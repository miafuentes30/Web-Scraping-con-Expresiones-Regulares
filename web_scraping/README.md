# Web Scraper - Productos de Videojuegos

## ¿Qué hace este programa?
Extrae el nombre del producto y la URL de la imagen desde un archivo HTML de una tienda en línea y guarda los resultados en un archivo CSV.

## ¿Cómo funciona?
Lee el HTML por bloques de tamaño fijo (buffer) y usa centinelas para detectar el inicio de cada producto. Luego aplica expresiones regulares para obtener el nombre y la imagen de cada producto y finalmente guarda los datos en un CSV.

## Cómo ejecutar
1. Asegúrate de tener Python 3 instalado.
2. Coloca el archivo HTML en la misma ruta configurada en el script.
3. Ejecuta:
   
   python web_scraper.py

## Knowledge Check
**¿Qué rol juegan los buffers en el procesamiento de datos de un archivo HTML?**

Permiten leer y procesar bloques de datos eficientemente, optimizando el manejo de grandes volúmenes de texto.
