"""Completa los TODO conforme a las reglas del documento Word."""
from pathlib import Path
import json
import re
from datetime import datetime

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "datos" / "solicitudes.txt"
SALIDA = BASE / "salidas"

def normalizar_categoria(texto):
    # Normaliza la categoría:(1.) strip, lower,(2.) sustituir guiones/ (3.)guiones bajos y unir palabras.
    if not texto:
        return ""
    # 1. Strip y lower
    t = texto.strip().lower()
    # 2. Sustituir - y _ por espacios
    t = t.replace("-", " ").replace("_", " ")
    # 3. Separar palabras y unirlas con _
    palabras = t.split()
    return "_".join(palabras)

def validar_campos(campos, ids_vistos):
    # Un rechazo devuelve (None, motivo); uno válido devuelve (registro, None).
    # Retorna (registro_limpio, motivo_rechazo).
    # Si es válido: retorna (registro_dict, None)
    # Si es inválido: retorna (None, motivo)

    # Debe haber exactamente 4 campos
    if len(campos) != 4:
        return None, "cantidad_campos_distinta_de_cuatro"
    
    id_raw, correo_raw, cat_raw, desc_raw = campos

    # Campos vacíos tras strip
    if not id_raw.strip() or not correo_raw.strip() or not cat_raw.strip() or not desc_raw.strip():
        return None, "campo_vacio"

    # 1. Validación de ID: SOL- seguido de 4 dígitos, longitud 8
    id_limpio = id_raw.strip().upper()
    if not re.match(r"^SOL-\d{4}$", id_limpio):
        return None, "id_invalido"

    # 2. Validación de Correo (didáctica: una sola @, sin espacios, partes no vacías, punto en dominio)
    correo_limpio = correo_raw.strip().lower()
    if correo_limpio.count("@") != 1:
        return None, "correo_invalido"
    
    partes = correo_limpio.split("@")
    if len(partes) != 2 or not partes[0] or not partes[1]:
        return None, "correo_invalido"
    
    usuario, dominio = partes
    if " " in correo_limpio:
        return None, "correo_invalido"
    if "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        return None, "correo_invalido"

    # 3. Validación de Categoría
    cat_normalizada = normalizar_categoria(cat_raw)
    catalogo_valido = {"acceso", "pago_en_línea", "soporte_técnico"}
    if cat_normalizada not in catalogo_valido:
        return None, "categoria_fuera_de_catalogo"

    # 4. Validación de Descripción (eliminar espacios extremos y reducir internos a uno)
    desc_limpia = " ".join(desc_raw.strip().split())
    if not desc_limpia:
        return None, "descripcion_vacia"

    # 5. ID duplicado
    if id_limpio in ids_vistos:
        return None, "id_duplicado"

    # Si pasa todas las reglas, armamos el registro limpio
    registro = {
        "id": id_limpio,
        "correo": correo_limpio,
        "categoria": cat_normalizada,
        "descripcion": desc_limpia
    }
    return registro, None

def main():
    try:
        # Crear carpeta de salidas si no existe
        SALIDA.mkdir(exist_ok=True)

        registros_validos = []
        rechazos = []
        ids_vistos = set()
        por_categoria = {"acceso": 0, "pago_en_línea": 0, "soporte_técnico": 0}

        # Abrir archivo de entrada con with y utf-8 de forma incremental
        with ENTRADA.open(encoding="utf-8") as archivo:
            # Leer la cabecera (primera línea física)
            cabecera_linea = archivo.readline()
            if not cabecera_linea:
                raise ValueError("El archivo está vacío.")
            
            cabecera_limpia = cabecera_linea.strip()
            if cabecera_limpia != "id|correo|categoria|descripcion":
                print(f"Error: Encabezado incorrecto detectado: '{cabecera_limpia}'")
                return

            # Iterar con enumerate iniciando en la línea 2
            for num_linea, linea_fisica in enumerate(archivo, start=2):
                texto_original = linea_fisica.rstrip("\r\n")

                # Regla 1: Línea vacía
                if not texto_original.strip():
                    rechazos.append({
                        "linea": num_linea,
                        "motivo": "linea_vacia",
                        "texto_original": texto_original
                    })
                    continue

                # Separar por el pipe "|"
                campos = texto_original.split("|")

                # Validar campos
                registro, motivo = validar_campos(campos, ids_vistos)

                if motivo:
                    rechazos.append({
                        "linea": num_linea,
                        "motivo": motivo,
                        "texto_original": texto_original
                    })
                else:
                    # Registrar como válido y guardar ID para evitar duplicados
                    ids_vistos.add(registro["id"])
                    registros_validos.append(registro)
                    por_categoria[registro["categoria"]] += 1

        # Escribir solicitudes limpias (modo w)
        path_limpias = SALIDA / "solicitudes_limpias.txt"
        with path_limpias.open("w", encoding="utf-8") as f_limpias:
            f_limpias.write("id|correo|categoria|descripcion\n")
            for reg in registros_validos:
                f_limpias.write(f"{reg['id']}|{reg['correo']}|{reg['categoria']}|{reg['descripcion']}\n")

        # Escribir rechazos en JSONL (modo w)
        path_rechazos = SALIDA / "rechazos.jsonl"
        with path_rechazos.open("w", encoding="utf-8") as f_rechazos:
            for rechazo in rechazos:
                f_rechazos.write(json.dumps(rechazo, ensure_ascii=False) + "\n")

        # Escribir resumen en JSON (modo w)
        total_lineas = len(registros_validos) + len(rechazos)
        resumen_data = {
            "total": total_lineas,
            "validos": len(registros_validos),
            "rechazados": len(rechazos),
            "por_categoria": por_categoria
        }
        path_resumen = SALIDA / "resumen.json"
        with path_resumen.open("w", encoding="utf-8") as f_resumen:
            json.dump(resumen_data, f_resumen, ensure_ascii=False, indent=2)

        # Escribir en el historial de ejecuciones (modo a)
        path_log = SALIDA / "ejecuciones.log"
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_linea = f"[{ahora}] Entrada: solicitudes.txt | Válidos: {len(registros_validos)} | Rechazados: {len(rechazos)}\n"
        with path_log.open("a", encoding="utf-8") as f_log:
            f_log.write(log_linea)

        # Verificación posterior requerida por el reto (reabrir y validar)
        with path_resumen.open("r", encoding="utf-8") as f_res:
            resumen_cargado = json.load(f_res)
        
        print("¡Proceso completado con éxito!")
        print(f"Total procesadas: {resumen_cargado['total']}")
        print(f"Válidos: {resumen_cargado['validos']} | Rechazados: {resumen_cargado['rechazados']}")
        print(f"Por categoría: {resumen_cargado['por_categoria']}")

    except FileNotFoundError as error:
        print(f"No se encontró el archivo de entrada: {error.filename}")

if __name__ == "__main__":
    main()
