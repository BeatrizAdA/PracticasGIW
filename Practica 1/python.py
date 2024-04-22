# TODO: rellenar
# Asignatura: GIW
# Práctica 1
# Grupo: 3
# Autores: Beatriz Álvarez de Arriba, David Chaparro García, David Elías Piñeiro, Rubén Martín Castro
#
# Declaramos que esta solución es fruto exclusivamente de nuestro trabajo personal. No hemos
# sido ayudados por ninguna otra persona o sistema automático ni hemos obtenido la solución
# de fuentes externas, y tampoco hemos compartido nuestra solución con otras personas
# de manera directa o indirecta. Declaramos además que no hemos realizado de manera
# deshonesta ninguna otra actividad que pueda mejorar nuestros resultados ni perjudicar los
# resultados de los demás.



# Ejercicio 1 Matrices
print("EJERCICIO 1 - MATRICES")

matriz = [[1, 0, 2], [0, 3, 3], [1, 2, 2]]

# dimension(matriz) utilizamos la función len de Python para obtener la dimensión de la matriz.
# Recorre las filas para asegurarse que todas son igual de largas, en caso contrario devuelve None.
def dimension(matriz):
	x = len(matriz)
	
	if x == 0:
		return None
	
	y = len(matriz[0])
	
	for row in matriz[1:]:
		if len(row) != y:
			return None
		
	return (x,y)

print("------ DIMENSIONES ------")
print(dimension(matriz))

# es_cuadrada(matriz) utilizamos dimension(matriz) para comprobar que las filas y columnas son igual de largas.
def es_cuadrada(matriz):
	if dimension(matriz) == None:
		return False
	return dimension(matriz)[0] == dimension(matriz)[1]

print("------ ES CUADRADA ------")
print(es_cuadrada(matriz))

# es_simetrica(matriz) comprobamos primero que todo que la matriz sea cuadrada, ya que es un requisito para que sea simétrica.
# Después vamos comprobando que los valores en los campos contrarios son iguales, y que por tanto la matriz es simétrica.
def es_simetrica(matriz):
	if es_cuadrada(matriz) == False:
		return False
	
	for idx, num1 in enumerate(matriz):
		for idy, num2 in enumerate(num1):
			if matriz[idx][idy] != matriz[idy][idx]:
				return False
	return True

print("------ ES SIMETRICA ------")
print(es_simetrica(matriz))

# multiplica_escalar(matriz, k) comprobamos que la matriz no esté vacia, en caso contrario devolvemos None.
# En caso de no ser vacia la recorremos entera con un doble for y multiplicamos cada valor por el escalar k.
def multiplica_escalar(matriz, k):
	if dimension(matriz) == None:
		return None
	
	matriz_sol = []
	
	for row in matriz:
		filaRes = []
		
		for val in row:
			filaRes.append(val * k)
			
		matriz_sol.append(filaRes)
		
	return matriz_sol

print("------ MULTIPLICA ESCALAR ------")
print(multiplica_escalar(matriz, 8))

matriz1 = [[1,0,2], [0,8], [1,2,2]]

matriz2 = [[1,0,2], [0,3], [1,2,2]]

# suma(matriz1, matriz2) comprobamos que las matrices tienen la misma dimensión y por tanto puede ser sumadas.
# En caso de que se puedan sumar, se crea una nueva matriz sumando cada valor de una matriz con su igual (el que esté en la misma posición) en la otra matriz.
def suma(matriz1, matriz2):
	    
    if dimension(matriz1) is not None and dimension(matriz1)==dimension(matriz2):
        
        matriz_sol=[]
        
        for i in range(len(matriz1)):
            row = []
            for j in range(len(matriz1[i])):
                row.append(matriz1[i][j] + matriz2[i][j])
            matriz_sol.append(row)
    
        return matriz_sol

print("------ SUMA ------")
print(suma(matriz1,matriz2))
	
	
# Ejercicio 2 Automatas
print("EJERCICIO 2 - AUTOMATAS")

#Ejemplos para probar validar(autómata)
automata_ok = {'alfabeto': {'0', '1'},
				'estados': {'p', 'q' , 'r'},
				'inicial': 'p',
				'finales': {'q'},
				'transicion': {('p', '0'): 'q',
				   ('p', '1'): 'r',
				   ('q', '0'): 'r',
				   ('q', '1'): 'q',
				   ('r', '0'): 'r',
				   ('r', '1'): 'r'
				   }
				}

automata_mal1 = {'alfabeto': {},
				 'estados': {'p', 'q' , 'r'},
				 'inicial': 'p',
				 'finales': {'q'},
				 'transicion': {('p', '0'): 'q',
					('p', '1'): 'r',
					('q', '0'): 'r',
					('q', '1'): 'q',
					('r', '0'): 'r',
					('r', '1'): 'r'
					}
				}

# validar(automata) se hacen las siguiente comprobaciones para saber que es una automata válido:
# 1- Se comprueban que estén todos los campos requeridos: alfabeto, estados, inicial, finales y transicion.
# 2- Se comrpueba que los campos alfabeto y estados no estén vacios, que el inicial y el final esté entre los estados.
# 3- Se comprueban las transiciones, comprobando que todas ellas están compuestas por un estado y letra del alfabeto válidas.
# 4- Si todo ello se cumple devuelves true, en caso de fallar cualquier if devuelves un False.
def validar(automata):
	if 'alfabeto' not in automata or 'estados' not in automata or 'inicial' not in automata or 'finales' not in automata or 'transicion' not in automata:
		return False
	if automata.get('alfabeto') == {}:
		return False
	if automata.get('estados') == {}:
		return False
	if automata.get('inicial') not in automata.get('estados'):
		return False
	for i in automata.get('finales'):
		if i not in automata.get('estados'):
			return False
	transicion = automata.get('transicion')
	for i in transicion:
		if i[0] not in automata.get('estados'):
			return False
		if i[1] not in automata.get('alfabeto'):
			return False
		if transicion[i] not in automata.get('estados'):
			return False
	return True

print("------ VALIDAR ------")
print(validar(automata_ok))
print(validar(automata_mal1))

# aceptar(cadena, automata) recibe una cadena de texto y un automata. Comprueba que la cadena sea válida para el automata.
# Para ello recorremos la cadena, y comprobamos que el estado inicial y final sean correctos siguiendo las instrucciónes del automata.
# Antes de empezar se comprobará si la cadena y el automata son válidos.
def aceptar(cadena, automata):
	if(not validar(automata) or len(cadena) == 0):
		return False
	else:
		estado = automata['inicial']
		
		for valor in cadena:
			if(not valor in automata['alfabeto']):
				return False
			
			transicion = (estado, str(valor))
			estado = automata['transicion'][transicion]
	
		if(estado in automata['finales']):
			return True
		return False		
		
print("------ ACEPTAR ------")
print(aceptar('', automata_ok))
print(aceptar('0001', automata_ok))
print(aceptar('0111', automata_ok))
print(aceptar('01a0', automata_ok))

#Ejemplos para equivalentes(automata1, automata2)
# reconoce el lenguaje a*
automata1 = {'alfabeto': {'a', 'b'},
			 'estados': {'q0', 'q1' , 'q2'},
			 'inicial': 'q0',
			 'finales': {'q0', 'q2'},
			 'transicion': {('q0', 'a'): 'q2',
				   ('q0', 'b'): 'q1',
				   ('q1', 'a'): 'q1',
				   ('q1', 'b'): 'q1',
				   ('q2', 'a'): 'q0',
				   ('q2', 'b'): 'q1',
				   }
			 }

# reconoce el lenguaje a*
automata2 = {'alfabeto': {'a', 'b'},
			 'estados': {'r0', 'r1'},
			 'inicial': 'r0',
			 'finales': {'r0'},
			 'transicion': {('r0', 'a'): 'r0',
				   ('r0', 'b'): 'r1',
				   ('r1', 'a'): 'r1',
				   ('r1', 'b'): 'r1',
				   }
			}

# reconoce el lenguaje ab*
automata3 = {'alfabeto': {'a', 'b'},
			 'estados': {'s0', 's1', 's2', 's3'},
			 'inicial': 's0',
			 'finales': {'s2'},
			 'transicion': {('s0', 'a'): 's1',
				   ('s0', 'b'): 's3',
				   ('s1', 'a'): 's3',
				   ('s1', 'b'): 's2',
				   ('s2', 'a'): 's3',
				   ('s2', 'b'): 's2',
				   ('s3', 'a'): 's3',
				   ('s3', 'b'): 's3',
				   }
			}

# sonCompatibles(finales1, finales2, nodo) comprueba si los nodos son compatibles, es decir o los dos son finales o ninguno de ellos lo es.
def sonCompatibles(finales1, finales2, nodo):
	return (nodo[0] in finales1 and nodo[1] in finales2) or (nodo[0] not in finales1 and nodo[1] not in finales2)

# equivalente(automata1, automata2) comprueba si dos automatas son equivalentes.
# 1- Comprobamos que los automatas son válidos y que el alfabeto es el mismo en ambos automatas, en caso contrario se devuelve False.
# 2- Se crea un nodo inicial (tupla) con el comienzo de ambos automatas.
# 3- Se inicializan las estructuras que vamos a usar con el nodo inicial. Una de ellas será una lista grafo donde se meten los nodos usados,
# y la otra una cola, donde se meteran aquellos que estén por comprobar.
# 4- Mientras nuevos_nodos no esté vacio se hace lo siguiente:
# 		- Comprobamos que el nuevo nodo creado está formado por nodos compatibles.
#		- Recorremos el automata1, creamos un nodo (tupla) con los estados, si ese nodo no esta en el grafo lo añadimos tanto al grafo como
#			a nuevos_nodos.
#		- Si no aparecen pares nuevos, se devuelve True ya que son equivalentes.
#		- Si siguen apareciendo pares nuevos, se elimina el primero de nuevos_nodos ya que ya ha sido comprobado y se sigue el mismo proceso.
def equivalentes(automata1, automata2):

	if(not validar(automata1) or not validar(automata2)):
		return False

	a1 = automata1.get("alfabeto")
	a2 = automata2.get("alfabeto")

	if a1 != a2:
		return False
	
	inicial = (automata1.get("inicial"), automata2.get("inicial"))

	grafo = [inicial]
	nuevos_nodos = [inicial]

	while len(nuevos_nodos) > 0:

		if sonCompatibles(automata1.get("finales"),automata2.get("finales"),nuevos_nodos[0]):
			aparecen = False

			for a in a1:
				
				q1 = automata1.get("transicion").get((nuevos_nodos[0][0], a))
				q2 = automata2.get("transicion").get((nuevos_nodos[0][1], a))

				nodo = (q1, q2)
				
				if(nodo not in grafo):
					grafo.append(nodo)
					nuevos_nodos.append(nodo)
					aparecen = True

			if(aparecen == False):
				return True
			
			nuevos_nodos.pop(0)
	
		else: return False	

print("------ EQUIVALENTES ------")
print(equivalentes(automata1,automata2))
print(equivalentes(automata2,automata1))
print(equivalentes(automata1,automata1))
print(equivalentes(automata1,automata3))