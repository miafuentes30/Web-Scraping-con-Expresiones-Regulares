import re
import csv
from pathlib import Path
from typing import List, Dict, Optional
import sys

# Configuración y constantes

# Tamaño del buffer en bytes
BUFFER_SIZE = 4096

# Centinelas para identificar secciones de producto
CENTINELA_INICIO = '<div class="product-layout'
CENTINELA_NOMBRE = 'data-name='
CENTINELA_IMAGEN = '<img class=" lazyloaded"'

# Expresiones regulares compiladas
REGEX_NOMBRE = re.compile(r'data-name="([^"]+)"')
REGEX_IMAGEN_COMPLETA = re.compile(r'data-src="(https?://[^"]+\.png)"')
REGEX_IMAGEN_RELATIVA = re.compile(r'src="(\./Videojuegos[^"]+\.png)"')


def extract_product_name(text: str) -> Optional[str]:
    """
    Extrae el nombre del producto usando expresión regular.

    Args:
        text: Fragmento HTML con el atributo data-name.

    Returns:
        Nombre del producto o None si no se encuentra.
    """
    match = REGEX_NOMBRE.search(text)
    if match:
        return match.group(1).strip()
    return None


def extract_image_url(text: str) -> Optional[str]:
    """
    Extrae la URL de la imagen usando expresiones regulares.

    Args:
        text: Fragmento HTML con referencias de imagen.

    Returns:
        URL de la imagen o None si no se encuentra.
    """
    # Buscar URL completa en data-src
    match = REGEX_IMAGEN_COMPLETA.search(text)
    if match:
        return match.group(1)

    # Buscar ruta relativa en src
    match = REGEX_IMAGEN_RELATIVA.search(text)
    if match:
        return match.group(1)

    return None


def procesar_buffer(segmento: str) -> Optional[Dict[str, str]]:
    """
    Procesa un segmento HTML de un producto y extrae datos.

    Args:
        segmento: Texto HTML de un producto.

    Returns:
        Diccionario con nombre e imagen, o None si faltan datos.
    """
    nombre = extract_product_name(segmento)
    imagen = extract_image_url(segmento)

    if nombre and imagen:
        return {
            'nombre': nombre,
            'imagen': imagen
        }
    
    return None


def procesar_html_con_buffer(ruta_archivo: str, ruta_salida_csv: str) -> List[Dict]:
    """
    Procesa el HTML en bloques y extrae productos.

    Args:
        ruta_archivo: Ruta del archivo HTML.
        ruta_salida_csv: Ruta de salida del CSV.

    Returns:
        Lista de diccionarios con productos.
    """
    
    productos = []
    buffer = ""
    contador_productos = 0
    
    print("Iniciando procesamiento con buffer")
    print(f"Archivo: {ruta_archivo}")
    print(f"Buffer size: {BUFFER_SIZE} bytes")
    print()
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            print("Leyendo archivo...")
            
            while True:
                # Leer bloque del archivo
                bloque = archivo.read(BUFFER_SIZE)
                if not bloque:
                    # Procesar último buffer al terminar el archivo
                    if CENTINELA_INICIO in buffer and CENTINELA_NOMBRE in buffer:
                        producto = procesar_buffer(buffer)
                        if producto:
                            productos.append(producto)
                            contador_productos += 1
                    break
                
                # Acumular bloque en buffer
                buffer += bloque
                
                # Procesar productos encontrados en el buffer
                while CENTINELA_INICIO in buffer:
                    pos_inicio = buffer.find(CENTINELA_INICIO)
                    pos_siguiente = buffer.find(CENTINELA_INICIO, pos_inicio + 1)
                    
                    if pos_siguiente == -1:
                        # No hay siguiente producto, mantener buffer para próxima lectura
                        buffer = buffer[pos_inicio:]
                        break
                    
                    # Extraer segmento del producto
                    segmento_producto = buffer[pos_inicio:pos_siguiente]
                    
                    # Procesar segmento
                    producto = procesar_buffer(segmento_producto)
                    if producto:
                        productos.append(producto)
                        contador_productos += 1
                        nombre_corto = producto['nombre'][:60]
                        print(f"  [{contador_productos:3d}] {nombre_corto}...")
                    
                    # Avanzar buffer al siguiente producto
                    buffer = buffer[pos_siguiente:]
            
            # Guardar resultados en CSV
            print()
            print("Guardando resultados...")
            guardar_csv(productos, ruta_salida_csv)
            
            print()
            print("Estadísticas:")
            print(f"Productos encontrados: {contador_productos}")
            print(f"Archivo CSV: {ruta_salida_csv}")
            print("Estado: Completado")
            print()
            
            return productos
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_archivo}")
        return []
    except Exception as e:
        print(f"Error durante procesamiento: {e}")
        import traceback
        traceback.print_exc()
        return []


def guardar_csv(productos: List[Dict], ruta_salida: str) -> None:
    """
    Guarda productos en un archivo CSV.

    Args:
        productos: Lista de diccionarios con nombre e imagen.
        ruta_salida: Ruta del archivo CSV de salida.
    """
    
    try:
        with open(ruta_salida, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Nombre del Producto', 'URL de la Imagen']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            print("Encabezados escritos")
            
            for producto in productos:
                writer.writerow({
                    'Nombre del Producto': producto['nombre'],
                    'URL de la Imagen': producto['imagen']
                })

            print(f"{len(productos)} productos guardados en {ruta_salida}")
        
    except Exception as e:
        print(f"Error al guardar CSV: {e}")


def mostrar_resumen(productos: List[Dict], cantidad_max: int = 5) -> None:
    """
    Muestra un resumen de los primeros productos.

    Args:
        productos: Lista de productos.
        cantidad_max: Cantidad de productos a mostrar.
    """
    
    if not productos:
        print("No hay productos para mostrar")
        return
    
    print(f"Primeros {min(cantidad_max, len(productos))} productos:")
    print()
    
    for i, producto in enumerate(productos[:cantidad_max], 1):
        nombre = producto['nombre']
        imagen = producto['imagen']
        
        # Limitar longitud de visualización
        nombre_display = nombre[:67] + "..." if len(nombre) > 70 else nombre
        imagen_display = imagen[:60] + "..." if len(imagen) > 63 else imagen
        
        print(f"{i}. Nombre: {nombre_display}")
        print(f"   Imagen: {imagen_display}")
        print()


def main() -> int:
    """
    Ejecuta el flujo principal del programa.

    Returns:
        0 si éxito, 1 si error.
    """
    
    # Rutas de archivos
    ruta_html = Path("c:/Users/miafu/Downloads/Web-Scraping-con-Expresiones-Regulares/web_scraping/Videojuegos en Guatemala - Pacifiko.com.html")
    ruta_csv = Path("c:/Users/miafu/Downloads/Web-Scraping-con-Expresiones-Regulares/web_scraping/productos_videojuegos.csv")
    
    print()
    print("Web Scraper - Extracción de Productos")
    print("Buffers - Centinelas - Expresiones Regulares")
    print()
    
    # Verificar que el archivo existe
    if not ruta_html.exists():
        print("Error: El archivo HTML no existe")
        print(f"Ruta esperada: {ruta_html}")
        return 1

    print("Archivo HTML encontrado")
    print(f"{ruta_html}")
    print()
    
    # Procesar HTML
    productos = procesar_html_con_buffer(str(ruta_html), str(ruta_csv))
    
    if not productos:
        print("No se extrajeron productos")
        return 1
    
    # Mostrar resumen
    mostrar_resumen(productos, cantidad_max=5)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())