def generar_histograma(lista_numeros):
    """
    Toma una lista de números enteros y genera un histograma visual en consola
    utilizando barras de asteriscos (*) proporcionales a cada valor numérico.
    """
    print("\n--- GENERADOR DE HISTOGRAMA ---")
    
    # Recorrer cada elemento de la lista junto con su índice usando enumerate
    for indice, valor in enumerate(lista_numeros):
        
        # Validar que el valor sea un número entero no negativo
        if not isinstance(valor, int) or valor < 0:
            print(f"Elemento {indice + 1}: [Valor inválido o negativo: {valor}]")
            continue
        
        # Crear la barra de asteriscos multiplicando '*' por el valor numérico
        barra_asteriscos = '*' * valor
        
        # Mostrar en pantalla el número del elemento, su valor y la barra gráfica correspondiente
        print(f"Elemento {indice + 1:2d} (Valor {valor:2d}): {barra_asteriscos}")

def main():
    # Definir una lista de números de prueba para el histograma
    numeros_ejemplo = [3, 7, 1, 5, 9, 4]
    
    print(f"Lista de entrada numérica: {numeros_ejemplo}")
    
    # Ejecutar la función constructora del histograma
    generar_histograma(numeros_ejemplo)

if __name__ == "__main__":
    main()