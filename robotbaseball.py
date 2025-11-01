from scipy.optimize import minimize_scalar
import numpy as np
from sympy import symbols, solve, simplify, Eq, lambdify, diff
from mpmath import mp



#Crear una matriz de 5X4 con diccionario de valor, probabilidadBall, probabilidadSwing
#Poner valores terminales y generar diccionario para todos

def generarMatriz():   
    matriz = np.empty((5, 4), dtype=object)
    for i in range(5):
        for h in range(4):
            matriz[i][h] = {'valor':None, 'probabilidadBall' : None, 'probabilidadSwing':None}


    for h in range(4):
        matriz[h][3]['valor'] = 0

    for h in range(3):
        matriz[4][h]['valor'] = 1

    return  matriz

#Poner en cada uno los valores no terminales

def generarDatosCelda(matriz, fila, columna):
    
    x, p = symbols('x p')

    esperanzaWait = x  * matriz[fila + 1][columna]['valor'] + (1-x) * matriz[fila][columna + 1]['valor']
    esperanzaSwing = x * matriz[fila][columna + 1]['valor'] + (1-x) * p * 4 + (1-x) * (1-p) * matriz[fila][columna + 1]['valor']

    equation = Eq(esperanzaWait,esperanzaSwing)

    probabilidadBall = solve(equation, x)[0]
    #print(f"x = {probabilidadBall}")
    matriz[fila][columna]['probabilidadBall'] = probabilidadBall

    y, p = symbols('y p')

    esperanzaBall = y * matriz[fila][columna + 1]['valor'] + (1-y) * matriz[fila + 1][columna]['valor']
    esperanzaStrike = y * p * 4 + y * (1-p) * matriz[fila][columna + 1]['valor'] + (1-y) *  matriz[fila][columna + 1]['valor']

    equation = Eq(esperanzaBall,esperanzaStrike)
    probabilidadSwing = solve(equation, y)[0]
    #print(f"y = {probabilidadSwing}")probabilidadSwing
    matriz[fila][columna]['probabilidadSwing'] = probabilidadSwing

    p = symbols('p')
    esperanzaPuntos = (1 - probabilidadBall) * probabilidadSwing * p * 4 + probabilidadBall * (1 - probabilidadSwing) * matriz[fila + 1][columna]['valor'] + (1 - probabilidadBall) * probabilidadSwing * (1 - p) * matriz[fila][columna + 1]['valor'] + (probabilidadBall) * (probabilidadSwing) * matriz[fila][columna + 1]['valor'] + (1 - probabilidadBall) * (1 - probabilidadSwing) * matriz[fila][columna + 1]['valor']

    equation = simplify(esperanzaPuntos)
    #print(f"puntos= {equation}")
    matriz[fila][columna]['valor'] = equation

    return matriz

def generarTodas(matriz):

    filas = 3
    cols = 2
    while filas >= 0:
        cols = 2
        while cols >= 0:
            matriz = generarDatosCelda(matriz,filas,cols)
            cols -= 1
        filas -=1

    return matriz

#armar la funcion de como se llega a 3b 2s

def probabilidadDeLlegar(matriz,fila,col):

    probabilidadDeLlegarPorball = 0
    probabilidadDeLlegarPorstrike = 0
    
    if col == 0 and fila == 0:
        return 1

    p = symbols('p')

    if col > 0:
        probabilidadDeLlegarPorstrike = probabilidadDeLlegar(matriz, fila, col - 1) * (matriz[fila][col - 1]['probabilidadBall'] * matriz[fila][col - 1]['probabilidadSwing'] + (1 - matriz[fila][col - 1]['probabilidadBall']) * (1 - matriz[fila][col - 1]['probabilidadSwing']) +  (1 - matriz[fila][col - 1]['probabilidadBall']) * matriz[fila][col - 1]['probabilidadSwing'] * (1 - p) )
    
    if fila > 0: 
        probabilidadDeLlegarPorball = probabilidadDeLlegar(matriz, fila - 1, col) * (matriz[fila-1][col]['probabilidadBall'] * (1- matriz[fila-1][col]['probabilidadSwing']))

    return simplify(probabilidadDeLlegarPorball + probabilidadDeLlegarPorstrike)


#derivarla para encontrar el maximo
#ingresar el maximo en la funcion y ver que da
p = symbols('p')
matriz = generarMatriz()
matriz = generarTodas(matriz)
ecuacion = probabilidadDeLlegar(matriz,3,2)
funcion = lambdify(p, ecuacion, 'numpy')

# Encontrar el maximo
result = minimize_scalar(
    lambda p_val: -funcion(p_val), 
    bounds=(0, 1), 
    method='bounded',
    options={'xatol': 1e-16} 
)

p_max = result.x
max_value = funcion(p_max)

# Imprimir con 15 valores decimales
print(f"p at maximum = {p_max:.15f}")
print(f"Maximum value = {max_value:.15f}")
