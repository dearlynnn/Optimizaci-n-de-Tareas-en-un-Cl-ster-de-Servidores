from random import Random
from time import perf_counter
from bisect import bisect_right


# ============================================================
# MODELO DE DATOS
# ============================================================

def mostrar_tareas(tareas, titulo="Tareas"):
    """Muestra las tareas de forma ordenada."""

    print(f"\n{'=' * 65}")
    print(titulo)
    print(f"{'=' * 65}")
    print(f"{'ID':<6}{'Inicio':<12}{'Fin':<12}{'Ganancia':<15}")
    print("-" * 65)

    for inicio, fin, ganancia, identificador in tareas:
        print(
            f"{identificador:<6}"
            f"{inicio:<12}"
            f"{fin:<12}"
            f"{ganancia:<15}"
        )


def calcular_ganancia(tareas):
    """Calcula la ganancia total de un conjunto de tareas."""

    return sum(tarea[2] for tarea in tareas)


# ============================================================
# GENERACIÓN DE DATOS
# ============================================================

def generar_tareas(n, semilla=42):
    """
    Genera N tareas aleatorias.

    Se utiliza una semilla fija para que los resultados
    puedan reproducirse durante la sustentación.
    """

    rng = Random(semilla)

    tareas = []

    for identificador in range(1, n + 1):

        inicio = rng.randint(0, n * 10)

        # Duraciones relativamente pequeñas.
        # Esto permite realizar el benchmark de 100.000
        # tareas sin convertir la búsqueda lineal en un caso
        # artificialmente extremo.
        duracion = rng.randint(1, 100)

        fin = inicio + duracion

        ganancia = rng.randint(10, 1000)

        tareas.append(
            (inicio, fin, ganancia, identificador)
        )

    return tareas
858

# ============================================================
# ENFOQUE A: ALGORITMO VORAZ / GREEDY
# ============================================================

def greedy(tareas):
    """
    Enfoque A.

    Ordena las tareas de mayor a menor ganancia y selecciona
    secuencialmente aquellas que no se solapen.

    Complejidad:
        Ordenamiento: O(n log n)
        Recorrido:    O(n)
        Total:        O(n log n)

    IMPORTANTE:
    Este algoritmo NO garantiza la solución óptima.
    """

    ordenadas = sorted(
        tareas,
        key=lambda tarea: tarea[2],
        reverse=True
    )

    seleccionadas = []
    ultimo_fin = -1

    for tarea in ordenadas:

        inicio, fin, ganancia, identificador = tarea

        if inicio >= ultimo_fin:

            seleccionadas.append(tarea)
            ultimo_fin = fin

    return seleccionadas


# ============================================================
# PREPARACIÓN PARA PROGRAMACIÓN DINÁMICA
# ============================================================

def ordenar_por_finalizacion(tareas):
    """
    Ordena las tareas por tiempo de finalización ascendente.

    ESTE ORDEN ES FUNDAMENTAL para los enfoques B y C.
    """

    return sorted(
        tareas,
        key=lambda tarea: tarea[1]
    )


# ============================================================
# ENFOQUE B: PROGRAMACIÓN DINÁMICA + BÚSQUEDA LINEAL
# ============================================================

def dp_busqueda_lineal(tareas):
    """
    Weighted Interval Scheduling.

    Programación Dinámica con búsqueda lineal para encontrar
    la última tarea compatible.

    Complejidad:
        Ordenamiento: O(n log n)
        Búsqueda de compatibilidad: O(n²) en el peor caso
        DP: O(n)

        Total: O(n²)
    """

    # ========================================================
    # ORDENAMIENTO CRÍTICO
    #
    # ESTA ES LA LÍNEA QUE EL PROFESOR PUEDE PEDIR CAMBIAR
    # DURANTE LA SUSTENTACIÓN.
    # ========================================================

    tareas = ordenar_por_finalizacion(tareas)

    n = len(tareas)

    if n == 0:
        return [], 0

    # dp[i] representa la máxima ganancia utilizando
    # las primeras i tareas.
    dp = [0] * (n + 1)

    # Para reconstruir posteriormente la solución.
    decisiones = [False] * n

    # ========================================================
    # BÚSQUEDA DE LA ÚLTIMA TAREA COMPATIBLE
    # ========================================================

    for i in range(n):

        inicio_actual = tareas[i][0]

        # Buscamos hacia atrás.
        j = i - 1

        while j >= 0 and tareas[j][1] > inicio_actual:
            j -= 1

        # j queda siendo:
        #
        # -1 si no existe tarea compatible
        #  0..n-1 si existe
        #
        ganancia_actual = tareas[i][2]

        if j == -1:
            ganancia_tomando = ganancia_actual
        else:
            ganancia_tomando = ganancia_actual + dp[j + 1]

        ganancia_sin_tomar = dp[i]

        # ====================================================
        # RECURRENCIA PRINCIPAL
        #
        # ESTA ES LA LÍNEA QUE EL PROFESOR PUEDE PEDIR
        # SEÑALAR Y EXPLICAR.
        # ====================================================

        dp[i + 1] = max(
            ganancia_sin_tomar,
            ganancia_tomando
        )

        if ganancia_tomando > ganancia_sin_tomar:
            decisiones[i] = True

    # ========================================================
    # RECONSTRUCCIÓN DE LA SOLUCIÓN
    # ========================================================

    seleccionadas = reconstruir_solucion_lineal(
        tareas,
        dp
    )

    return seleccionadas, dp[n]


def reconstruir_solucion_lineal(tareas, dp):
    """
    Reconstruye las tareas seleccionadas a partir de la tabla DP.
    """

    seleccionadas = []

    i = len(tareas) - 1

    while i >= 0:

        inicio_actual = tareas[i][0]

        j = i - 1

        while j >= 0 and tareas[j][1] > inicio_actual:
            j -= 1

        ganancia_tomando = tareas[i][2]

        if j >= 0:
            ganancia_tomando += dp[j + 1]

        # Si tomar la tarea produce el mismo óptimo,
        # podemos tomarla.
        if ganancia_tomando >= dp[i]:

            seleccionadas.append(tareas[i])

            i = j

        else:

            i -= 1

    seleccionadas.reverse()

    return seleccionadas


# ============================================================
# ENFOQUE C: PROGRAMACIÓN DINÁMICA + BÚSQUEDA BINARIA
# ============================================================

def dp_busqueda_binaria(tareas):
    """
    Programación Dinámica optimizada utilizando búsqueda binaria.

    Complejidad:
        Ordenamiento: O(n log n)
        Búsqueda compatible: O(log n) por tarea
        DP: O(n)

        Total: O(n log n)
    """

    # ========================================================
    # MISMO ORDENAMIENTO QUE EN EL ENFOQUE B
    # ========================================================

    tareas = ordenar_por_finalizacion(tareas)

    n = len(tareas)

    if n == 0:
        return [], 0

    # Lista de tiempos de finalización.
    finales = [tarea[1] for tarea in tareas]

    # dp[i] = máxima ganancia utilizando las primeras i tareas.
    dp = [0] * (n + 1)

    for i in range(n):

        inicio_actual = tareas[i][0]
        ganancia_actual = tareas[i][2]

        # ====================================================
        # BÚSQUEDA BINARIA
        #
        # Encontramos cuántas tareas terminan antes o justo
        # cuando empieza la tarea actual.
        #
        # bisect_right devuelve la posición después del último
        # valor <= inicio_actual.
        # ====================================================

        cantidad_compatibles = bisect_right(
            finales,
            inicio_actual,
            0,
            i
        )

        # Si hay k tareas compatibles, su valor DP está
        # en dp[k].
        ganancia_tomando = (
            ganancia_actual
            + dp[cantidad_compatibles]
        )

        ganancia_sin_tomar = dp[i]

        # ====================================================
        # MISMA RECURRENCIA DEL ENFOQUE B
        # ====================================================

        dp[i + 1] = max(
            ganancia_sin_tomar,
            ganancia_tomando
        )

    # ========================================================
    # RECONSTRUCCIÓN
    # ========================================================

    seleccionadas = reconstruir_solucion_binaria(
        tareas,
        dp,
        finales
    )

    return seleccionadas, dp[n]


def reconstruir_solucion_binaria(tareas, dp, finales):

    seleccionadas = []

    i = len(tareas) - 1

    while i >= 0:

        inicio_actual = tareas[i][0]

        cantidad_compatibles = bisect_right(
            finales,
            inicio_actual,
            0,
            i
        )

        ganancia_tomando = (
            tareas[i][2]
            + dp[cantidad_compatibles]
        )

        # Si tomar la tarea conserva el óptimo.
        if ganancia_tomando >= dp[i]:

            seleccionadas.append(tareas[i])

            i = cantidad_compatibles

        else:

            i -= 1

    seleccionadas.reverse()

    return seleccionadas


# ============================================================
# RETO 1: CASO DONDE GREEDY FALLA
# ============================================================

def caso_trampa_greedy():

    """
    Caso construido manualmente para demostrar que Greedy
    puede producir una solución inferior a Programación Dinámica.

    Tareas:

        A: 1 -> 4    ganancia 50
        B: 4 -> 7    ganancia 50
        C: 1 -> 7    ganancia 90
        D: 7 -> 9    ganancia 20
        E: 0 -> 1    ganancia 10

    Greedy prioriza C porque tiene ganancia 90.

    Greedy:
        C + D = 110

    Solución óptima:
        E + A + B + D = 130
    """

    return [
        (1, 4, 50, "A"),
        (4, 7, 50, "B"),
        (1, 7, 90, "C"),
        (7, 9, 20, "D"),
        (0, 1, 10, "E"),
    ]


def ejecutar_reto_greedy():

    tareas = caso_trampa_greedy()

    mostrar_tareas(
        tareas,
        "RETO 1 - TRAMPA DE LA AVARICIA"
    )

    seleccion_greedy = greedy(tareas)

    seleccion_dp, ganancia_dp = dp_busqueda_binaria(
        tareas
    )

    ganancia_greedy = calcular_ganancia(
        seleccion_greedy
    )

    print("\nGREEDY")
    print("-" * 40)

    for tarea in seleccion_greedy:
        print(
            f"Tarea {tarea[3]} | "
            f"{tarea[0]} -> {tarea[1]} | "
            f"Ganancia: {tarea[2]}"
        )

    print(f"Ganancia total Greedy: {ganancia_greedy}")

    print("\nPROGRAMACIÓN DINÁMICA")
    print("-" * 40)

    for tarea in seleccion_dp:
        print(
            f"Tarea {tarea[3]} | "
            f"{tarea[0]} -> {tarea[1]} | "
            f"Ganancia: {tarea[2]}"
        )

    print(f"Ganancia óptima DP: {ganancia_dp}")

    print("\nCOMPARACIÓN")
    print("-" * 40)

    if ganancia_greedy < ganancia_dp:
        print(
            "Greedy falla: encontró una solución "
            "inferior al óptimo global."
        )
    else:
        print(
            "ADVERTENCIA: este caso no demuestra "
            "la falla de Greedy."
        )


# ============================================================
# RETO 4: BENCHMARKING
# ============================================================

def medir_tiempo(funcion, tareas):

    inicio = perf_counter()

    resultado = funcion(tareas)

    fin = perf_counter()

    tiempo = fin - inicio

    return resultado, tiempo


def benchmark(n=100_000):

    print("\n")
    print("=" * 70)
    print(f"BENCHMARK - {n:,} TAREAS")
    print("=" * 70)

    tareas = generar_tareas(n)

    print("\nDatos generados correctamente.")
    print(f"N = {len(tareas):,}")

    # ========================================================
    # ENFOQUE B
    # ========================================================

    print("\nEjecutando Enfoque B...")
    print("Programación Dinámica + Búsqueda Lineal")

    (_, ganancia_b), tiempo_b = medir_tiempo(
        dp_busqueda_lineal,
        tareas
    )

    print(
        f"Tiempo B: {tiempo_b:.6f} segundos"
    )

    print(
        f"Ganancia B: {ganancia_b:,}"
    )

    # ========================================================
    # ENFOQUE C
    # ========================================================

    print("\nEjecutando Enfoque C...")
    print("Programación Dinámica + Búsqueda Binaria")

    (_, ganancia_c), tiempo_c = medir_tiempo(
        dp_busqueda_binaria,
        tareas
    )

    print(
        f"Tiempo C: {tiempo_c:.6f} segundos"
    )

    print(
        f"Ganancia C: {ganancia_c:,}"
    )

    # ========================================================
    # COMPARACIÓN
    # ========================================================

    print("\n")
    print("=" * 70)
    print("RESULTADOS")
    print("=" * 70)

    print(f"DP Lineal : {tiempo_b:.6f} s")
    print(f"DP Binaria: {tiempo_c:.6f} s")

    if tiempo_c > 0:

        aceleracion = tiempo_b / tiempo_c

        print(
            f"\nLa búsqueda binaria fue aproximadamente "
            f"{aceleracion:.2f}x más rápida."
        )

    if ganancia_b == ganancia_c:

        print(
            "\nVALIDACIÓN: ambos enfoques encontraron "
            "la misma ganancia óptima."
        )

    else:

        print(
            "\nERROR: las soluciones no coinciden."
        )


# ============================================================
# COMPARACIÓN COMPLETA
# ============================================================

def comparar_enfoques(tareas):

    print("\n")
    print("=" * 70)
    print("COMPARACIÓN DE LOS TRES ENFOQUES")
    print("=" * 70)

    # Greedy
    solucion_a = greedy(tareas)
    ganancia_a = calcular_ganancia(solucion_a)

    # DP lineal
    solucion_b, ganancia_b = dp_busqueda_lineal(tareas)

    # DP binaria
    solucion_c, ganancia_c = dp_busqueda_binaria(tareas)

    print(f"\nEnfoque A - Greedy")
    print(f"Ganancia: {ganancia_a}")

    print(f"\nEnfoque B - DP + búsqueda lineal")
    print(f"Ganancia: {ganancia_b}")

    print(f"\nEnfoque C - DP + búsqueda binaria")
    print(f"Ganancia: {ganancia_c}")

    print("\nVALIDACIÓN")

    if ganancia_b == ganancia_c:
        print(
            "B y C producen la misma solución óptima."
        )
    else:
        print(
            "ERROR: B y C producen resultados diferentes."
        )


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def menu():

    while True:

        print("\n")
        print("=" * 70)
        print("PROYECTO INTEGRADOR - OPTIMIZACIÓN DE TAREAS")
        print("=" * 70)

        print("1. Generar tareas y comparar los tres enfoques")
        print("2. Ejecutar Reto 1 - Trampa de Greedy")
        print("3. Ejecutar Benchmark - 100.000 tareas")
        print("4. Salir")

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":

            try:

                n = int(
                    input(
                        "\n¿Cuántas tareas desea generar? "
                    )
                )

                if n <= 0:
                    print("N debe ser mayor que 0.")
                    continue

                tareas = generar_tareas(n)

                if n <= 30:
                    mostrar_tareas(
                        tareas,
                        "CONJUNTO DE TAREAS"
                    )

                comparar_enfoques(tareas)

            except ValueError:

                print(
                    "Debe introducir un número entero."
                )

        elif opcion == "2":

            ejecutar_reto_greedy()

        elif opcion == "3":

            benchmark(100_000)

        elif opcion == "4":

            print("\nPrograma finalizado.")
            break

        else:

            print(
                "Opción no válida."
            )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    menu()