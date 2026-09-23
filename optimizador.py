import bisect
import random
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Tarea:
    id: int
    inicio: float
    fin: float
    ganancia: float


def generar(n, semilla=42):
    r = random.Random(semilla)
    tareas = []

    for i in range(n):
        inicio = r.randint(0, 1_000_000)
        fin = inicio + r.randint(1, 100)
        ganancia = r.randint(1, 1000)
        tareas.append(Tarea(i, inicio, fin, ganancia))

    return tareas


def leer():
    n = int(input("Cantidad de tareas: "))
    tareas = []

    for i in range(n):
        print(f"\nTarea {i}")
        inicio = float(input("Inicio: "))
        fin = float(input("Fin: "))
        ganancia = float(input("Ganancia: "))
        tareas.append(Tarea(i, inicio, fin, ganancia))

    return tareas


def greedy(tareas):
    tareas = sorted(tareas, key=lambda t: t.ganancia, reverse=True)
    seleccion = []

    for t in tareas:
        if all(
            t.fin <= s.inicio or s.fin <= t.inicio
            for s in seleccion
        ):
            seleccion.append(t)

    seleccion.sort(key=lambda t: t.inicio)
    return sum(t.ganancia for t in seleccion), seleccion

# Ordenamiento 

def dp(tareas, binaria=False, clave=None):
    tareas = sorted(tareas, key=clave or (lambda t: t.fin))
    n = len(tareas)

    if not n:
        return 0, []

    p = [-1] * n

    if binaria:
        finales = [t.fin for t in tareas]

        for i, t in enumerate(tareas):
            p[i] = bisect.bisect_right(
                finales, t.inicio, 0, i
            ) - 1
    else:
        for i in range(n):
            for j in range(i - 1, -1, -1):
                if tareas[j].fin <= tareas[i].inicio:
                    p[i] = j
                    break

    tabla = [0] * n
    # desición 
    for i in range(n):
        tomar = tareas[i].ganancia
        if p[i] != -1:
            tomar += tabla[p[i]]

        no_tomar = tabla[i - 1] if i else 0
        tabla[i] = max(tomar, no_tomar)

    seleccion = []
    i = n - 1

    while i >= 0:
        anterior = tabla[i - 1] if i else 0

        if tabla[i] != anterior:
            seleccion.append(tareas[i])
            i = p[i]
        else:
            i -= 1

    seleccion.reverse()
    return tabla[-1], seleccion


def mostrar(nombre, resultado):
    ganancia, tareas = resultado
    print(f"\n{nombre}")
    print(f"Ganancia: {ganancia}")
    print("Tareas:", tareas)


def reto1():
    print("\nRETO 1")
    print("Ingrese 4 o 5 tareas que demuestren la falla de Greedy.")
    tareas = leer()

    g = greedy(tareas)
    d = dp(tareas)

    mostrar("Greedy", g)
    mostrar("DP", d)

    if g[0] < d[0]:
        print("\nGreedy obtiene una ganancia menor que DP.")
    else:
        print("\nEste conjunto no demuestra la falla de Greedy.")


def reto2():
    print("\nRETO 2")
    tareas = leer()

    print("\n1) Fin\n2) Inicio\n3) Ganancia")
    opcion = input("Orden: ")

    claves = {
        "1": lambda t: t.fin,
        "2": lambda t: t.inicio,
        "3": lambda t: -t.ganancia
    }

    resultado = dp(tareas, clave=claves.get(opcion, claves["1"]))
    mostrar("Resultado", resultado)

    correcto = dp(tareas)
    print(f"Referencia por fin: {correcto[0]}")


def benchmark():
    n = 100_000
    print(f"\nGenerando {n:,} tareas aleatorias...")

    tareas = generar(n)

    inicio = time.perf_counter()
    b = dp(tareas)
    tiempo_b = time.perf_counter() - inicio

    inicio = time.perf_counter()
    c = dp(tareas, binaria=True)
    tiempo_c = time.perf_counter() - inicio

    print("\nBENCHMARK")
    print(f"N = {n:,}")
    print(f"DP lineal : {tiempo_b:.4f} s")
    print(f"DP binaria: {tiempo_c:.4f} s")
    print(f"Ganancia B: {b[0]}")
    print(f"Ganancia C: {c[0]}")
    print(f"Relación: {tiempo_b / tiempo_c:.2f}x")
    print(f"¿Misma solución?: {b[0] == c[0]}")


def main():
    while True:
        print("\n" + "=" * 50)
        print("OPTIMIZACIÓN DE TAREAS")
        print("=" * 50)
        print("1) Comparar los 3 enfoques")
        print("2) Reto 1 - Greedy")
        print("3) Reto 2 - Ordenamiento")
        print("4) Reto 4 - Benchmark 100.000")
        print("0) Salir")

        opcion = input("\nOpción: ")

        if opcion == "0":
            break

        if opcion == "1":
            tareas = leer()
            mostrar("Greedy", greedy(tareas))
            mostrar("DP lineal", dp(tareas))
            mostrar("DP binaria", dp(tareas, binaria=True))

        elif opcion == "2":
            reto1()

        elif opcion == "3":
            reto2()

        elif opcion == "4":
            benchmark()

        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()