# Instrucciones.

## Instalacion 

- *1* **clonar el repositorio**

git clone https://github.com/nacho-gonz/PDI-TUIA-2024-G12-TP3.git

- *2* **Instalar las librerias necesarias**:
  - opencv: mediante pip: *pip install opencv-contrib-Python*
  - numpy: mediante pip: *pip install numpy*
  - matplotlib: mediante pip: *pip install matplotlib*

## Ejecución del código:

  Escribir en la terminal: python TP3-PDI-2024-G13.py

## Personalización

- Si desea agregar videos de tiradas, para detectar los valores de los dados, es necesario que sean añadidas en la carpeta "videos" siguiendo el orden númerico ya existente desde 1 hasta inf y el formato de "tirada_{n}.mp4" siendo n el número del video después de los 4 por default.
- Ejemplo: si añade su primer video nuevo tendría que llamarse "tirada_5.mp4".
- Todos los videos de salida van a quedar en la carpeta videos_salida y en caso de repetir el proceso estando los videos dentro, se reescribiran.
