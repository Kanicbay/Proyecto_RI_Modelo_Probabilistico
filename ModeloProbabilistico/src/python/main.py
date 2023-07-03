import os
import math
import re

# Leer documentos en formato txt y separar por palabras
# Los documentos deben iniciar con el nombre 'Document'
def leer_documentos():
    coleccion_documentos = {}
    archivos = os.listdir()

    for archivo in archivos:
        if archivo.startswith("Document"):
            nombre_documento = archivo[:-4]
            with open(archivo, 'r') as f:
                contenido = f.read()
            palabras = contenido.split()
            coleccion_documentos[nombre_documento] = palabras
    return coleccion_documentos

# Funciona para eliminar stop-words - No funciona con tildes
def quitarStopWords(representaciones):
    stopWords = ["a", "al", "con", "de", "del", "el", "en", "es", "están", "la", "los",
                 "las", "su", "un", "una", "unos", "unas", "tiene", "va", "y", "estan"]
    nuevas_representaciones = {}

    for documento, palabras in representaciones.items():
        palabras_limpias = []
        for palabra in palabras:
            if palabra.lower() not in stopWords:
                palabras_limpias.append(palabra)
        nuevas_representaciones[documento] = palabras_limpias

    return nuevas_representaciones

# Obtener lexicon a partir de las palabras de todos los documentos
# Se ordena el lexicon en orden alfabetico
def obtener_lexicon(coleccion_documentos):
    lexicon = set()

    for palabras_documento in coleccion_documentos.values():
        lexicon.update(palabras_documento)

    return sorted(list(lexicon))

# Obtener tabla de frecuencias
def obtener_tabla_frecuencias(coleccion_documentos, lexicon, query):
    frecuencias = {}
    
    # Recorrer documentos
    for nombre_documento, palabras_documento in coleccion_documentos.items():
        fila = {}
        # Recorrer terminos y verificar frecuencia
        for termino in lexicon:
            if termino in palabras_documento:
                fila[termino] = 1
            else:
                fila[termino] = 0
        # agregar fila a la tabla
        frecuencias[nombre_documento] = fila

    # Agregar fila para la consulta
    fila_query = {}
    palabras_query = query.split()
    for termino in lexicon:
        if termino in palabras_query:
            fila_query[termino] = 1
        else:
            fila_query[termino] = 0
    frecuencias['Query'] = fila_query

    # Agregar suma de frecuencias
    fila_ni = {}
    for termino in lexicon:
        suma_frecuencias = sum([fila[termino] for nombre, fila in frecuencias.items() if nombre != 'Query'])
        fila_ni[termino] = suma_frecuencias
    frecuencias['ni'] = fila_ni

    return frecuencias

# Se calculan las medidas para encontrar la similud de los documentos con la
# consulta
def calcular_medidas(tabla_frecuencias, cantidad_documentos):
    medidas = {}

    for termino, fila in tabla_frecuencias['ni'].items():
        ni = fila
        pi = 0.5    # Constante
        qi = ni / cantidad_documentos
        ci = round(math.log10((cantidad_documentos - ni) / ni), 2)
        medidas[termino] = {'ni': ni, 'pi': pi, 'qi': qi, 'ci': ci}

    return medidas

def calcular_similitud(medidas, tabla_frecuencias):
    similitud = {}

    # Obtener los nombres de los documentos y los términos del lexicon
    nombres_documentos = list(tabla_frecuencias.keys())
    terminos = list(tabla_frecuencias['Query'].keys())

    # Crear la columna de similitud
    similitud['similitud'] = [0] * len(nombres_documentos)
    similitud['ci'] = [0] * len(nombres_documentos)  # Agregar la columna 'ci'

    # Obtener la similitud a partir del vector de query y de cada documento
    for i in range(len(nombres_documentos)):
        if nombres_documentos[i] == 'Query':
            continue

        for termino in terminos:
            if tabla_frecuencias['Query'][termino] == 1 and tabla_frecuencias[nombres_documentos[i]][termino] == 1:
                similitud['similitud'][i] += medidas[termino]['ci']
                similitud['ci'][i] = medidas[termino]['ci']  # Asignar el valor de 'ci'

    return similitud

# Llamar a la función para leer los documentos e imprimir cada documento
coleccion_documentos = leer_documentos()
cantidad_documentos = len(coleccion_documentos)
print("Documentos originales:\n")
for i ,(nombre_documento, palabras) in enumerate(coleccion_documentos.items()):
    palabras_documento = " ".join(palabras)
    print(f'Document{i+1}: "{palabras_documento}"')

# Llamar a la función quitarStopWords para limpiar el documento e imprimirlos
coleccion_documentos = quitarStopWords(coleccion_documentos)
print("\nDocumentos con palabras claves:\n")
for i ,(nombre_documento, palabras) in enumerate(coleccion_documentos.items()):
    palabras_documento = " ".join(palabras)
    print(f'Document{i+1}: "{palabras_documento}"')

# Generar lexicon a partir de los documentos con palabras claves
lexicon = obtener_lexicon(coleccion_documentos)
print("\nLexicon generado de los documentos: \n")
print("V = {",', '.join(lexicon),"}\n")

# Leer consulta, la consulta se leer a partir de un txt ingresado en la GUI
print("Ingreso de consulta: ")
with open("consulta.txt", 'r') as archivo:
    query = archivo.read().strip()
print("\nLa consulta ingresada es: ", query)

# Obtener la tabla de frecuencias para los documentos
# esta estructura no contiene a los terminos como parte pero al mantener
# el orden alfabetico inicial entonces siempre seran los valores correctos
tabla = obtener_tabla_frecuencias(coleccion_documentos, lexicon, query)

max_valor_alineacion = 15   # Valor de alineacion maximo para formateo de texto

print("\nTabla de frecuencias: \n")
print(" " * (max_valor_alineacion+1) + "\t".join(lexicon))
print("--" * len("\t".join(lexicon)))
for nombre_documento, fila in tabla.items():
    print(nombre_documento.ljust(max_valor_alineacion), end="\t")
    for termino in lexicon:
        print(fila[termino], end="\t")
    print()


# Obtener las medidas
# esta estructura no tiene terminos como la anterior
cantidad_documentos = len(coleccion_documentos)
medidas = calcular_medidas(tabla, cantidad_documentos)
medidas_texto = ['termino', 'ni', 'pi', 'qi', 'ci']
print("\nMedidas: \n")
print(medidas_texto[0].ljust(max_valor_alineacion), "\t".join(medidas_texto[1:]))
print("--" * (len("\t".join(lexicon)) - 4))

for termino, medida in medidas.items():
    print(termino.ljust(max_valor_alineacion), medida['ni'],
          medida['pi'], medida['qi'], medida['ci'], end="\t", sep="\t")
    print()

# Obtener los nombres de los documentos
nombres_documentos = list(tabla.keys())

# Obtener la similitud de los documentos con la consulta
similitud = calcular_similitud(medidas, tabla)
valores_ci = [f"c{i+1}" for i in range(len(tabla.items())-1)]
similitud_documentos = {}
print("\nSimilitud: \n")
print(" " * (max_valor_alineacion+1) + "\t".join(valores_ci))
print("--" * (len("\t".join(lexicon)) + 4))
for nombre_documento, fila in tabla.items():
    if(nombre_documento == 'Query'):
        break
    print(nombre_documento.ljust(max_valor_alineacion), end="\t")
    for termino in lexicon:
        print(fila[termino], end="\t")
    print(similitud['similitud'][nombres_documentos.index(nombre_documento)])
    similitud_documentos[nombres_documentos[nombres_documentos.index(nombre_documento)]] = similitud['similitud'][nombres_documentos.index(nombre_documento)]


# Imprimir los elementos mas relevantes
valor_relevancia_min = min(similitud_documentos.values())
valor_relevancia_max = max(similitud_documentos.values())
if(valor_relevancia_max <= 0):
    valor_relevancia = valor_relevancia_min
else:
    valor_relevancia = valor_relevancia_max
    
if(valor_relevancia != 0):
    documentos_relevantes = {
        nombre_documento: similitud for nombre_documento, similitud in similitud_documentos.items()
        if similitud == valor_relevancia
    }
    documentos_relevantes = list(documentos_relevantes)
    if(len(documentos_relevantes) != 1):
        print("\nSegun estos resultados los documentos", ", ".join(documentos_relevantes), "se consideran empatados en la primera posicion")
    else:
        print("\nSegun estos resultados el documento", ", ".join(documentos_relevantes), "se considera en la primera posicion")
else:
    print("Ningun documento relevante")
