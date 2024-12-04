import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

def filtrar_consecutivos(lista: list)-> list:
    """
    Se toma una lista con valores, y se devuelve unicamente la cadena de nuermos consecutivos 

    Parámetros:
    lista (list): Una lista de números enteros.

    Retorna:
    list: Una nueva lista que contiene los bloques consecutivos con más de un elemento.
        Si no hay bloques consecutivos o la lista está vacía, retorna una lista vacía.
    """
    if not lista:  # Si la lista está vacía, devuelve una lista vacía
        return []

    resultado = []
    consecutivo_actual = []

    for i in range(1, len(lista)):
        if lista[i] == lista[i - 1] + 1:  # Es consecutivo
            consecutivo_actual.append(lista[i])
        else:
            if len(consecutivo_actual) > 1:  # Si el bloque tiene más de 1 elemento, lo guarda
                resultado.extend(consecutivo_actual)
            consecutivo_actual = [lista[i]]  # Nuevo bloque consecutivo

    # Agregar el último bloque consecutivo si es válido
    if len(consecutivo_actual) > 1:
        resultado.extend(consecutivo_actual)

    return resultado

for i in range(1, 5):
    
    cap = cv2.VideoCapture(f'videos/tirada_{i}.mp4')
    # Creamos el objeto de cada video y obtenemos los frames con las funciones que fueron dadas 
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Creamos el video de salida con los dados remarcados y sus respectivos puntos
    out = cv2.VideoWriter(f'videos/tirada_output_{i}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width,height))


    frame_number = 0
    frames = []
    centroides_dados = []
    frames_quietos = []
    centroides_boundings = []

    while (cap.isOpened()): # Verifica si el video se abrió correctamente.

        ret, frame = cap.read() # 'ret' indica si la lectura fue exitosa (True/False) y 'frame' contiene el contenido del frame si la lectura fue exitosa.
        if ret == True:  
            
            # Agregamos todos los frames del video a una lista
            frames.append(frame)

            # Decidimos trabajar con el componente A de CIELab, ya que este canal trabaja bien con los colores rojos y verdes
            # Pudiendo así, identificar bien el fondo de los dados
            frame_cielab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            _, a , _ = cv2.split(frame_cielab)
        
            # Se aplica un umbral para quedarnos únicamente con el área de las monedas
            _ , mascara = cv2.threshold(a, 120, 255, cv2.THRESH_BINARY)
            
            # Buscamos las componentes conectadas para identificar los dados
            num_labels,_,stats,centroide = cv2.connectedComponentsWithStats(mascara,connectivity=4)

            dados = []

            # Iteramos sobre todos los objetos que fueron encontrados como posibles dados
            # Identificándolos, primero por sus relaciones de aspecto, y también por el área que ocupa cada dado
            # Luego, buscamos los centroides de los dados, para así, luego, poder identificar en qué momento los dados se dejan de mover
            for i in range(1,num_labels):
                x, y, w, h, area = stats[i]
                if 0.4 < w/h < 1.3 and 3000 < w*h < 12000:
                    centroidee = centroide[i]
                    centroidee = centroidee.astype(int)
                    dados.append(centroidee)


            centroides_dados.append(dados)

            # Mediante la distancia de Euclídea, buscamos saber cuándo el dado deja de moverse, comprando el frame actual con el anterior y sus respectivos centroides 
            # También, nos aseguramos de tener únicamente 5 centroides, o sea, 5 dados para comparar
            # Al final, agregamos el número del frame y la posición del centroide
            if len(centroides_dados) > 1:
                frame_actual = centroides_dados[frame_number]
                frame_anterior = centroides_dados[frame_number-1]
                dado_no_movil = 0
                if len(frame_actual) == 5  and len(frame_anterior) == 5:
                    for i in range(5):
                        diff = np.linalg.norm(frame_actual[i] - frame_anterior[i])
                        if diff <= 5:
                            dado_no_movil += 1
                    if dado_no_movil == 5:
                        frames_quietos.append(frame_number)
                        centroides_boundings.append((frame_number, centroides_dados[frame_number]))
            frame_number += 1
        else:  
            break  

    cap.release()


    # Buscamos los frames consecutivos que tengan los dados estáticos
    frames_finales = filtrar_consecutivos(frames_quietos)
    num_dados = []

    # Iteramos sobre todos los frames, buscando los frames consecutivos que anteriormente guardamos 
    # Luego, trabajamos sobre el primer frame que tenga los dados estáticos, iterando en cada centroide, o sea, en cada dado
    for indx, imagen in enumerate(frames):
        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        if indx in frames_finales:
            if frames_finales.index(indx) == 0:
                imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20,20))
                imagen_tophat = cv2.morphologyEx(imagen_gris, cv2.MORPH_TOPHAT, kernel)
                for indice_centroide, centroides in centroides_boundings:
                    if indx == indice_centroide:
                        for centroide in centroides:
                            valor_dado = 0
                            x,y = centroide
                            
                            # Pasamos la imagen a gris y creamos una máscara para utilizar con el método tophat 
                            # Que resaltará las áreas de la imagen que son más brillantes

                            # Recortamos la imagen sumando 50 píxeles a cada lado del centroide 
                            # Luego realizamos un umbral para diferenciar los puntos del dado, y buscamos sus contornos para luego contarlos 
                            padding = 50
                            recorte = imagen_tophat[y-padding:y+padding,x-padding:x+padding]
                            _, recorte_bin = cv2.threshold(recorte, 100, 255, cv2.THRESH_BINARY)
                            cont, her = cv2.findContours(recorte_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

                            # Buscamos diferenciar las formas de los puntos, buscando sus factores de forma
                            for contorno in cont:
                                area_objetos = cv2.contourArea(contorno)
                                perimetro_cuadrado_objetos = cv2.arcLength(contorno, True)**2
                                if perimetro_cuadrado_objetos > 0:
                                    factor_de_forma = area_objetos/perimetro_cuadrado_objetos
                                    if factor_de_forma > 0.062:
                                        valor_dado += 1
                            
                            # Dibujamos los cuadrados de cada dado y la cantidad de puntos en cada dado
                            cv2.rectangle(imagen, (x-padding,y-padding), (x+padding,y+padding), (0,0,255), 5)
                            cv2.putText(imagen, str(valor_dado), (x-47,y-53), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5, cv2.LINE_AA)
                            num_dados.append(valor_dado)
                out.write(imagen)
            else:
                # Paro el resto de frames en que los dados están quitos, graficamos los recuadrados y cantidad de puntos 
                cont_dado = 0
                for indice_centroide, centroides in centroides_boundings:
                    if indx == indice_centroide:
                        for centroide in centroides:
                            x,y = centroide
                            cv2.rectangle(imagen, (x-padding,y-padding), (x+padding,y+padding), (0,0,255), 5)
                            cv2.putText(imagen, str(num_dados[cont_dado]), (x-47,y-53), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5, cv2.LINE_AA)
                            cont_dado += 1
                out.write(imagen)
        else:   
            out.write(imagen)


    out.release()