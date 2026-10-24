import unicodedata
import re

def limpiar_cadena(texto):
    """
    Limpia la cadena de entrada:
    - Convierte todos los caracteres a minúsculas.
    - Elimina tildes y marcas diacríticas (normalización Unicode).
    - Remueve espacios, signos de puntuación y caracteres especiales.
    """
    # Convertir el texto a minúsculas para estandarizar la comparación
    texto_minuscula = texto.lower()
    
    # Normalizar caracteres acentuados separando la letra de su tilde (NFD) y eliminar marcas (Mn)
    texto_normalizado = ''.join(
        c for c in unicodedata.normalize('NFD', texto_minuscula) 
        if unicodedata.category(c) != 'Mn'
    )
    
    # Utilizar expresión regular para conservar únicamente letras (a-z) y dígitos (0-9)
    texto_limpio = re.sub(r'[^a-z0-9]', '', texto_normalizado)
    
    return texto_limpio

def es_palindromo(texto):
    """
    Verifica si una cadena procesada es idéntica al leerse 
    de izquierda a derecha y de derecha a izquierda.
    """
    # Obtener la cadena limpia sin espacios ni puntuación
    limpia = limpiar_cadena(texto)
    
    # Comprobar si la cadena es igual a su inversa ([::-1])
    es_igual = (limpia == limpia[::-1])
    
    return es_igual, limpia

def main():
    print("=== PROGRAMA VERIFICADOR DE PALÍNDROMOS ===")
    
    # Solicitar la cadena de texto al usuario mediante la consola
    entrada_usuario = input("Ingresa una palabra o frase para evaluar: ")
    
    # Llamar a la función de validación
    resultado, texto_procesado = es_palindromo(entrada_usuario)
    
    # Imprimir los resultados detallados en pantalla
    print(f"\nTexto original: {entrada_usuario}")
    print(f"Texto procesado (sin espacios/acentos): {texto_procesado}")
    
    if resultado:
        print("Resultado: ¡Sí es un palíndromo!")
    else:
        print("Resultado: No es un palíndromo.")

if __name__ == "__main__":
    main()