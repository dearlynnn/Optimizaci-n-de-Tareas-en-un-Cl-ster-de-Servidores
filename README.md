# Optimizador de tareas

Este README documenta la versión de prueba implementada en [test.py](test.py), donde se comparan varios enfoques para resolver el problema de selección de intervalos con ganancia.

## Objetivo

Dado un conjunto de tareas con:

- inicio
- fin
- ganancia

se busca elegir un subconjunto compatible que maximice la ganancia total sin solaparse en el tiempo.

Este problema se conoce como Weighted Interval Scheduling.

---

## Modelo de datos

La estructura base es una dataclass llamada Tarea:

- id: identificador único
- inicio: momento en que comienza la tarea
- fin: momento en que termina la tarea
- ganancia: valor asociado

La función no_se_solapan(a, b) define compatibilidad entre dos tareas:

- una tarea es compatible si termina antes de que la otra empiece, o viceversa

Es decir, no puede haber solapamiento de intervalos.

---

## Funciones auxiliares

### generar_tareas
Genera tareas aleatorias con un valor semilla configurable para que el experimento sea reproducible.

### mostrar_resultado
Imprime la ganancia total y las tareas seleccionadas por cada enfoque.

---

## Enfoque A: Greedy

### Idea
Ordenar las tareas por ganancia descendente y seleccionar las que no se solapen con las ya elegidas.

### Resultado
Es una estrategia rápida, pero no es óptima.

### Qué falla
Greedy maximiza la ganancia local de una tarea sin considerar que podría bloquear un conjunto de varias tareas menores que juntas generan más beneficio.

### Complejidad
- Ordenamiento: O(n log n)
- Verificación de solapamientos: O(n²) en el peor caso

---

## Enfoque B: Programación Dinámica con búsqueda lineal

### Idea
Se ordenan las tareas por tiempo de finalización ascendente y se calcula la mejor ganancia acumulada tarea por tarea.

### Función clave
_la_ultima_compatible_lineal

Busca, recorriendo hacia atrás, la última tarea que termina antes de que comience la tarea actual.

### Recurrencia

La ecuación central es:

- dp[i] = max(ganancia[i] + dp[última_compatible(i)], dp[i - 1])

Esto significa:

- tomar la tarea actual, o
- no tomarla y conservar la mejor solución anterior

### Complejidad
- Ordenamiento: O(n log n)
- Búsqueda compatible: O(n²) en el peor caso
- Total: O(n²)

---

## Enfoque C: Programación Dinámica con búsqueda binaria

### Idea
Es la misma lógica del enfoque B, pero usando búsqueda binaria para localizar la última tarea compatible.

### Función clave
_la_ultima_compatible_binaria

Usa bisect_right para hallar la posición exacta de la última tarea que finaliza antes del inicio actual.

### Ventaja
Reduce el costo de compatibilidad de O(n) a O(log n) por tarea.

### Complejidad
- Ordenamiento: O(n log n)
- Búsqueda compatible: O(log n) por tarea
- Total: O(n log n)

---

## Reconstrucción de la solución

La función _reconstruir_solucion sigue hacia atrás la decisión tomada en cada paso y reconstruye la lista de tareas elegidas.

Esto permite devolver no solo la ganancia máxima, sino también el conjunto exacto de tareas que la alcanza.

---

## Reto 1: la trampa de la avaricia

Se construye un caso manual donde Greedy falla.

### Ejemplo conceptual

- A: [0, 10] ganancia 50
- B: [0, 4] ganancia 20
- C: [4, 8] ganancia 20
- D: [8, 10] ganancia 15

Greedy toma A y obtiene 50, pero la mejor solución real es:

- B + C + D = 55

### Lección
La mejor decisión local no siempre genera la mejor solución global.

---

## Reto 2: el orden del caos

Este reto muestra que el orden de las tareas no es un detalle secundario.

Si se ordena por:

- fin
- inicio
- ganancia

las propiedades del DP cambian. El algoritmo depende de que el arreglo esté ordenado por tiempo de finalización para que los subproblemas queden bien definidos.

### Conclusión
La invariante del DP solo se cumple si las tareas están ordenadas por fin.

---

## Reto 3: la decisión del algoritmo

La línea clave es esta:

- dp[i] = max(ganancia[i] + dp[última_compatible(i)], dp[i - 1])

Esto representa la decisión de:

- tomar la tarea actual, o
- no tomarla

La solución óptima emerge de comparar ambas opciones y elegir la mejor.

---

## Reto 4: prueba de estrés

Se genera un benchmark con 100,000 tareas para comparar la velocidad de ambos enfoques exactos.

### Observación
La versión con búsqueda binaria es varias órdenes de magnitud más rápida que la lineal.

### Resultado esperado
- Enfoque B: O(n²)
- Enfoque C: O(n log n)

En pruebas grandes, la diferencia de tiempo es muy notable.

---

## Cómo ejecutar

Desde la raíz del proyecto:

```bash
python test.py
```

El script ejecuta una demo general, los retos y la prueba de estrés.

---

## Resumen final

- Greedy es rápido, pero no garantiza optimalidad
- DP lineal es exacta, pero más costosa
- DP binaria es exacta y mucho más eficiente
- El orden por fin es esencial para la validez del algoritmo
- La solución correcta se basa en comparar “tomar” vs “no tomar” cada tarea

Este archivo sirve como una demostración didáctica del problema y de cómo evolucionan las soluciones desde la idea voraz hasta la versión optimizada con programación dinámica.
# README — Optimización de Tareas en un Clúster de Servidores

## 1. ¿Qué hace este proyecto?

El programa busca **seleccionar tareas que no se solapen entre sí para maximizar la ganancia total**.

Cada tarea tiene:

```python
Tarea(
    id,
    inicio,
    fin,
    ganancia
)
```

Por ejemplo:

```text
T0: inicio = 1, fin = 4, ganancia = 20
```

Significa que la tarea ocupa el servidor desde el tiempo `1` hasta el `4` y genera una ganancia de `20`.

El servidor solamente puede ejecutar **una tarea a la vez**, por lo que no podemos seleccionar dos tareas que se ejecuten simultáneamente.

---

# 2. ¿Qué significa que dos tareas se solapen?

Dos tareas se **solapan** cuando sus intervalos de ejecución se cruzan.

Por ejemplo:

```text
T1: 1 ───── 5
T2:       3 ───── 7
```

Se solapan porque ambas necesitan el servidor entre `3` y `5`.

Por lo tanto, **no pueden seleccionarse las dos**.

### Ejemplo de tareas compatibles

```text
T1: 1 ─── 4
T2:         4 ─── 7
```

Estas sí pueden ejecutarse juntas porque:

```python
T1.fin <= T2.inicio
```

es decir:

```text
4 <= 4 → True
```

En nuestro código, la condición que comprueba esto es:

```python
if tareas[j].fin <= tareas[i].inicio:
```

### Regla para recordar

```text
fin de una tarea <= inicio de la otra
        ↓
    compatibles
```

Si no se cumple, las tareas se solapan.

---

# 3. Las tres soluciones

El proyecto implementa tres enfoques:

| Enfoque | Función                  | Idea principal                               |
| ------- | ------------------------ | -------------------------------------------- |
| A       | `greedy()`               | Elegir primero las tareas con mayor ganancia |
| B       | `dp(..., binaria=False)` | Programación dinámica + búsqueda lineal      |
| C       | `dp(..., binaria=True)`  | Programación dinámica + búsqueda binaria     |

---

# 4. Enfoque A — Greedy

La función es:

```python
def greedy(tareas):
```

Primero ordena las tareas por ganancia:

```python
tareas = sorted(tareas, key=lambda t: t.ganancia, reverse=True)
```

Es decir:

```text
mayor ganancia
      ↓
   primero
```

Después intenta agregar cada tarea:

```python
if all(
    t.fin <= s.inicio or s.fin <= t.inicio
    for s in seleccion
):
    seleccion.append(t)
```

Esta parte comprueba que la nueva tarea **no se solape con ninguna tarea que ya fue seleccionada**.

### ¿Qué deben saber explicar?

Greedy es rápido y sencillo, pero **no garantiza la ganancia óptima**.

El Reto 1 demuestra precisamente esto.

---

# 5. Reto 1 — Demostrar que Greedy puede fallar

La función es:

```python
def reto1():
```

Aquí se introducen manualmente 4 o 5 tareas.

Después se ejecutan:

```python
g = greedy(tareas)
d = dp(tareas)
```

Y se comparan:

```python
if g[0] < d[0]:
```

La idea es demostrar:

```text
Greedy < DP
```

### Qué decir

> "Greedy toma las tareas según la mayor ganancia inmediata, pero una tarea con una ganancia alta puede impedir seleccionar varias tareas que juntas produzcan una ganancia mayor."

No necesitan decir que Greedy está "mal"; **es una estrategia que no garantiza el óptimo para este problema**.

---

# 6. Enfoque B y C — Programación Dinámica

Ambos están dentro de:

```python
def dp(tareas, binaria=False, clave=None):
```

La diferencia principal entre B y C está en **cómo encuentran la última tarea compatible**.

Pero antes hay algo fundamental.

---

# 7. Ordenamiento por tiempo de finalización

Esta es una de las líneas más importantes del proyecto:

```python
tareas = sorted(tareas, key=clave or (lambda t: t.fin))
```

Por defecto, las tareas se ordenan por:

```python
t.fin
```

Es decir:

```text
fin menor → fin mayor
```

Esto es necesario para que la programación dinámica pueda encontrar correctamente las tareas compatibles anteriores.

### ⭐ ESTA LÍNEA ES CLAVE PARA EL RETO 2

El profesor puede pedir modificarla.

Por inicio:

```python
tareas = sorted(tareas, key=lambda t: t.inicio)
```

Por ganancia:

```python
tareas = sorted(tareas, key=lambda t: -t.ganancia)
```

La idea del Reto 2 es demostrar que **la DP depende de que las tareas estén ordenadas por tiempo de finalización**.

---

# 8. ¿Por qué el orden por FIN es necesario?

La DP necesita responder:

> "Si tomo esta tarea, ¿cuál es la última tarea que puedo ejecutar antes de ella?"

Por eso necesitamos buscar una tarea que cumpla:

```python
tareas[j].fin <= tareas[i].inicio
```

Es decir:

```text
la tarea anterior termina
antes o exactamente cuando
comienza la nueva tarea
```

Al ordenar por `fin`, las posiciones anteriores tienen la estructura temporal que la DP necesita.

Si ordenamos por `inicio` o por `ganancia`, estar antes en la lista **ya no garantiza que la tarea haya terminado antes**.

Por eso el algoritmo puede producir un resultado que no representa correctamente la solución óptima.

---

# 9. Reto 2 — Ordenamiento

La función es:

```python
def reto2():
```

Tiene tres opciones:

```python
print("\n1) Fin\n2) Inicio\n3) Ganancia")
```

Las opciones están definidas aquí:

```python
claves = {
    "1": lambda t: t.fin,
    "2": lambda t: t.inicio,
    "3": lambda t: -t.ganancia
}
```

### Lo que deben señalar

La línea principal:

```python
tareas = sorted(tareas, key=clave or (lambda t: t.fin))
```

Y después esta:

```python
if tareas[j].fin <= tareas[i].inicio:
```

### Qué explicar

> "El orden por finalización es necesario porque la programación dinámica busca la última tarea compatible entre las tareas anteriores. Si cambiamos el orden por inicio o ganancia, las posiciones dejan de representar correctamente el orden temporal y la recurrencia puede utilizar información incorrecta."

---

# 10. Búsqueda de la tarea compatible

Aquí está la diferencia entre B y C.

## B — Búsqueda lineal

```python
for i in range(n):
    for j in range(i - 1, -1, -1):
        if tareas[j].fin <= tareas[i].inicio:
            p[i] = j
            break
```

El programa revisa las tareas anteriores **una por una**, desde la más cercana hacia atrás.

Por eso es:

```text
Búsqueda lineal → O(n)
```

para cada tarea.

En total:

```text
O(n²)
```

---

# 11. C — Búsqueda binaria

Cuando:

```python
binaria=True
```

se utiliza:

```python
finales = [t.fin for t in tareas]
```

y:

```python
p[i] = bisect.bisect_right(
    finales, t.inicio, 0, i
) - 1
```

Aquí se utiliza búsqueda binaria para encontrar rápidamente la última tarea compatible.

La búsqueda pasa de:

```text
O(n)
```

a:

```text
O(log n)
```

Por eso el enfoque C tiene una complejidad general de:

```text
O(n log n)
```

---

# 12. Reto 3 — La parte MÁS importante de la DP

La línea que deben señalar es:

```python
tabla[i] = max(tomar, no_tomar)
```

Esta es la **recurrencia de programación dinámica**.

Antes de llegar a ella, el código calcula las dos posibilidades.

### Opción 1: tomar

```python
tomar = tareas[i].ganancia
```

Si existe una tarea compatible:

```python
if p[i] != -1:
    tomar += tabla[p[i]]
```

Significa:

```text
Ganancia de la tarea actual
+
mejor ganancia compatible anterior
```

---

### Opción 2: no tomar

```python
no_tomar = tabla[i - 1] if i else 0
```

Significa:

> Ignoramos la tarea actual y conservamos la mejor solución que ya teníamos.

---

### Finalmente:

```python
tabla[i] = max(tomar, no_tomar)
```

La DP compara:

```text
              ┌── Tomar
              │
tabla[i] = max
              │
              └── No tomar
```

Y guarda la alternativa con mayor ganancia.

### Qué decir en la exposición

> "La recurrencia representa las dos decisiones posibles sobre la tarea actual: tomarla y sumar su ganancia a la mejor solución compatible anterior, o no tomarla y conservar la solución anterior. El máximo selecciona la alternativa que produce mayor ganancia."

**Esta es la explicación que deben memorizar para el Reto 3.**

---

# 13. Reconstrucción de las tareas

Después de calcular la tabla, el programa recupera cuáles tareas fueron seleccionadas:

```python
seleccion = []
i = n - 1
```

Luego:

```python
if tabla[i] != anterior:
    seleccion.append(tareas[i])
    i = p[i]
else:
    i -= 1
```

La idea es recorrer la tabla hacia atrás para descubrir **qué decisiones produjeron la ganancia óptima**.

---

# 14. Reto 4 — Comparación de rendimiento

La función es:

```python
def benchmark():
```

El tamaño solicitado es:

```python
n = 100_000
```

Se generan:

```python
tareas = generar(n)
```

Después se mide B:

```python
inicio = time.perf_counter()
b = dp(tareas)
tiempo_b = time.perf_counter() - inicio
```

Y C:

```python
inicio = time.perf_counter()
c = dp(tareas, binaria=True)
tiempo_c = time.perf_counter() - inicio
```

Finalmente se comparan:

```python
print(f"DP lineal : {tiempo_b:.4f} s")
print(f"DP binaria: {tiempo_c:.4f} s")
```

Y se verifica que ambas obtengan la misma ganancia:

```python
print(f"¿Misma solución?: {b[0] == c[0]}")
```

### Qué deben explicar

B:

```text
Búsqueda lineal
O(n) por tarea
↓
O(n²)
```

C:

```text
Búsqueda binaria
O(log n) por tarea
↓
O(n log n)
```

Por eso C debería ser considerablemente más rápida cuando `n` es grande.

---

# 15. Qué debe saber cada integrante

Aunque cada persona pueda explicar una parte, **todos deben conocer estas líneas** porque el profesor puede seleccionar a cualquiera.

### 🟢 Greedy

```python
tareas = sorted(tareas, key=lambda t: t.ganancia, reverse=True)
```

**Saber explicar:** ordena por mayor ganancia y por qué Greedy puede fallar.

---

### 🔵 Reto 1

```python
g = greedy(tareas)
d = dp(tareas)
```

**Saber explicar:** Greedy puede obtener una ganancia menor que DP.

---

### 🟠 Reto 2

```python
tareas = sorted(tareas, key=clave or (lambda t: t.fin))
```

**Saber explicar:** por qué el orden por `fin` es necesario.

También:

```python
if tareas[j].fin <= tareas[i].inicio:
```

**Saber explicar:** cómo se determina si dos tareas son compatibles.

---

### 🔴 Reto 3

```python
tabla[i] = max(tomar, no_tomar)
```

**Saber explicar:**

```text
tomar = tarea actual + solución compatible
no tomar = solución anterior
max = elegir mayor ganancia
```

---

### 🟣 Reto 4

```python
b = dp(tareas)
```

vs.

```python
c = dp(tareas, binaria=True)
```

**Saber explicar:**

```text
B → O(n²)
C → O(n log n)
```

---

# 16. Resumen para la sustentación

Si tienen poco tiempo para estudiar, aprendan esta tabla:

| Reto       | Línea que señalar                          | Qué decir                                                                                         |
| ---------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **Reto 1** | `g = greedy(tareas)` / `d = dp(tareas)`    | Greedy puede tomar una decisión local que impide obtener la mayor ganancia global                 |
| **Reto 2** | `tareas = sorted(... t.fin)`               | La DP necesita las tareas ordenadas por finalización para encontrar correctamente las compatibles |
| **Reto 2** | `tareas[j].fin <= tareas[i].inicio`        | La tarea anterior debe terminar antes o cuando comienza la actual                                 |
| **Reto 3** | `tabla[i] = max(tomar, no_tomar)`          | Comparamos tomar la tarea contra no tomarla                                                       |
| **Reto 4** | `dp(tareas)` vs `dp(tareas, binaria=True)` | Lineal O(n²) frente a binaria O(n log n)                                                          |

---

## ⚠️ Una corrección importante para el Reto 2

No memoricen que **"ordenar por inicio siempre dará X"** o **"ordenar por ganancia siempre dará Y"**. El resultado depende del conjunto de tareas.

Lo que deben defender es el **principio**:

> **El algoritmo de programación dinámica está construido bajo el supuesto de que las tareas están ordenadas por tiempo de finalización. Cambiar ese orden rompe la relación entre los índices y la compatibilidad temporal de las tareas.**

---


