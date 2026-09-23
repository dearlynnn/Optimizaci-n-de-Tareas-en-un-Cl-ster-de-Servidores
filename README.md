# README — Proyecto Integrador: Optimización de Tareas en un Clúster de Servidores

## 1. Descripción

El programa busca **seleccionar un conjunto de tareas que no se solapen y que maximicen la ganancia total**.

Cada tarea tiene:

* `id`: identificador.
* `inicio`: momento en que comienza.
* `fin`: momento en que termina.
* `ganancia`: beneficio obtenido al ejecutar la tarea.

El servidor solo puede ejecutar **una tarea a la vez**, por lo que las tareas seleccionadas deben ser compatibles entre sí.

---

# 2. ¿Qué significa que dos tareas se solapen?

Dos tareas se solapan cuando necesitan utilizar el servidor durante un mismo intervalo de tiempo.

### Ejemplo de solapamiento

```text
T1: 1 ───────── 5
T2:       3 ───────── 7
```

Entre los tiempos `3` y `5`, ambas necesitan el servidor.

Por lo tanto:

```text
T1 + T2 → NO se pueden ejecutar juntas
```

### Ejemplo sin solapamiento

```text
T1: 1 ─── 4
T2:         4 ─── 7
```

Estas sí son compatibles porque:

```text
T1.fin <= T2.inicio
4 <= 4
```

En el código esta condición aparece en:

```python
if tareas[j].fin <= tareas[i].inicio:
```

### Regla para recordar

> Si una tarea termina antes o exactamente cuando comienza la otra, ambas pueden seleccionarse.

---

# 3. Los tres enfoques

El proyecto utiliza tres estrategias:

| Enfoque                   | Función        | Complejidad |
| ------------------------- | -------------- | ----------- |
| A — Greedy                | `greedy()`     | O(n log n)  |
| B — DP + búsqueda lineal  | `dp_lineal()`  | O(n²)       |
| C — DP + búsqueda binaria | `dp_binaria()` | O(n log n)  |

La diferencia principal entre B y C está en **cómo encuentran la última tarea compatible**.

---

# 4. Enfoque A — Greedy

La función es:

```python
def greedy(tareas):
```

Primero ordena las tareas por ganancia descendente:

```python
ordenadas = sorted(tareas, key=lambda t: t.ganancia, reverse=True)
```

Es decir:

```text
mayor ganancia
      ↓
   primero
```

Después intenta seleccionar cada tarea verificando que no se solape con las que ya fueron seleccionadas:

```python
if all(
    tarea.fin <= otra.inicio or otra.fin <= tarea.inicio
    for otra in seleccion
):
```

### ¿Qué deben saber explicar?

Greedy toma decisiones basándose en la **ganancia inmediata**.

El problema es que una tarea con una ganancia alta puede ocupar un intervalo que impida seleccionar varias tareas cuya ganancia combinada sea mayor.

Por eso **Greedy no garantiza la solución óptima**.

---

# 5. Reto 1 — Demostrar que Greedy falla

La función correspondiente es:

```python
def reto1():
```

Se introducen tareas y se calculan dos soluciones:

```python
mostrar("Greedy", greedy(tareas))
mostrar("DP", dp_lineal(tareas))
```

La comparación busca demostrar:

```text
Ganancia Greedy < Ganancia DP
```

### ¿Qué deben decir?

> "Greedy selecciona según la mejor ganancia individual disponible, pero esa decisión puede impedir seleccionar varias tareas compatibles cuya ganancia total sea mayor."

El objetivo del Reto 1 es demostrar con un caso concreto que la estrategia Greedy puede obtener una solución inferior a la programación dinámica. 

---

# 6. Programación Dinámica

Los enfoques B y C utilizan programación dinámica.

La idea general es que para cada tarea existen dos posibilidades:

```text
              Tarea actual
                  │
          ┌───────┴───────┐
          ↓               ↓
        TOMAR          NO TOMAR
          │               │
    ganar + DP        DP anterior
          │               │
          └───────┬───────┘
                  ↓
                 MAX
```

La programación dinámica conserva la mejor ganancia encontrada hasta cada posición.

---

# 7. Ordenamiento por finalización

Esta es una de las líneas **más importantes del proyecto**:

```python
tareas = sorted(tareas, key=clave or (lambda t: t.fin))
```

Por defecto, las tareas se ordenan por:

```python
t.fin
```

es decir:

```text
fin menor → fin mayor
```

Este orden es fundamental para los enfoques B y C porque permite buscar correctamente las tareas compatibles anteriores.

### ⚠️ Esta línea es la principal del Reto 2.

---

# 8. Reto 2 — Cambiar el ordenamiento

El Reto 2 pide demostrar qué sucede cuando se modifica el ordenamiento de las tareas. El enunciado plantea cambiar el orden por tiempo de finalización a **tiempo de inicio o ganancia** y explicar por qué la programación dinámica depende del orden por finalización. 

La línea que deben señalar es:

```python
tareas = sorted(tareas, key=clave or (lambda t: t.fin))
```

### Orden correcto

```python
lambda t: t.fin
```

### Cambiar a inicio

```python
lambda t: t.inicio
```

### Cambiar a ganancia

```python
lambda t: -t.ganancia
```

---

## ¿Por qué el orden por `fin` es necesario?

La programación dinámica necesita encontrar la última tarea compatible con la actual.

La condición es:

```python
tareas[j].fin <= tareas[i].inicio
```

Es decir:

> "La tarea anterior debe haber terminado antes de que empiece la tarea actual."

Cuando las tareas están ordenadas por `fin`, el algoritmo puede buscar correctamente entre las tareas anteriores.

Si las ordenamos por `inicio` o por `ganancia`, **estar antes en la lista ya no garantiza que una tarea haya terminado antes**.

Por eso se rompe la estructura sobre la que se basa la recurrencia.

### Para la exposición

Si preguntan:

> "¿Qué línea controla el Reto 2?"

Señalar:

```python
tareas = sorted(tareas, key=clave or (lambda t: t.fin))
```

Y explicar:

> "Esta línea determina el orden en que la programación dinámica procesa las tareas. El orden correcto es por finalización ascendente."

---

# 9. Enfoque B — DP + búsqueda lineal

La función es:

```python
def dp_lineal(tareas, clave=None):
```

Primero ordena las tareas:

```python
tareas = sorted(tareas, key=clave or (lambda t: t.fin))
```

Después busca la última tarea compatible:

```python
for i in range(n):
    for j in range(i - 1, -1, -1):
        if tareas[j].fin <= tareas[i].inicio:
            compatibles[i] = j
            break
```

La búsqueda comienza desde la tarea anterior y retrocede hasta encontrar una compatible.

Como puede revisar muchas tareas para cada posición:

```text
Búsqueda compatible → O(n)
```

y esto se hace para `n` tareas:

```text
O(n) × O(n) = O(n²)
```

Por eso el enfoque B tiene complejidad:

```text
O(n²)
```

---

# 10. Reto 3 — La decisión de tomar o no tomar

Esta es **la línea que deben señalar para el Reto 3**:

```python
dp[i] = max(tomar, no_tomar)
```

Antes se calculan las dos posibilidades.

### Tomar

```python
tomar = tareas[i].ganancia

if compatibles[i] != -1:
    tomar += dp[compatibles[i]]
```

Significa:

> Ejecutar la tarea actual y sumar la mejor ganancia obtenida con una tarea compatible anterior.

En términos del problema:

```text
ganancia de la tarea actual
+
mejor solución compatible
```

### No tomar

```python
no_tomar = dp[i - 1] if i else 0
```

Significa:

> No ejecutar la tarea actual y conservar la mejor solución encontrada anteriormente.

### La decisión

```python
dp[i] = max(tomar, no_tomar)
```

El algoritmo compara ambas alternativas y conserva la que tenga mayor ganancia.

### 🎯 Frase para memorizar

> **"Tomar significa ejecutar la tarea actual junto con la mejor solución compatible anterior; no tomar significa conservar la solución anterior. `max` selecciona la alternativa con mayor ganancia."**

El Reto 3 pide precisamente explicar esta recurrencia en términos de la decisión de asignación del recurso. 

---

# 11. Enfoque C — DP + búsqueda binaria

La función es:

```python
def dp_binaria(tareas):
```

Primero se ordenan las tareas por finalización:

```python
tareas = sorted(tareas, key=lambda t: t.fin)
```

Después se crea una lista con los tiempos de finalización:

```python
finales = [t.fin for t in tareas]
```

La última tarea compatible se encuentra mediante:

```python
bisect.bisect_right(
    finales, tareas[i].inicio, 0, i
) - 1
```

En lugar de revisar una por una las tareas anteriores, la búsqueda binaria reduce la búsqueda a:

```text
O(log n)
```

Por lo tanto:

```text
Ordenamiento       → O(n log n)
Búsquedas          → O(n log n)
Programación DP    → O(n)
--------------------------------
Complejidad final  → O(n log n)
```

---

# 12. Diferencia entre B y C

La lógica de la programación dinámica es la misma.

La diferencia está en encontrar la tarea compatible:

### B

```text
Búsqueda lineal
      ↓
O(n) por tarea
      ↓
O(n²)
```

### C

```text
Búsqueda binaria
      ↓
O(log n) por tarea
      ↓
O(n log n)
```

Por eso ambos deben encontrar **la misma ganancia óptima**, pero C debería tardar considerablemente menos con muchos datos.

---

# 13. Reto 4 — Benchmark con 100.000 tareas

La función es:

```python
def benchmark():
```

El tamaño está establecido en:

```python
n = 100_000
```

Se generan las tareas:

```python
tareas = generar(n)
```

Después se ejecuta B:

```python
b = dp_lineal(tareas)
```

y se mide su tiempo.

Después se ejecuta C:

```python
c = dp_binaria(tareas)
```

y también se mide.

Finalmente se comparan:

```python
print(f"DP lineal : {tiempo_b:.4f} s")
print(f"DP binaria: {tiempo_c:.4f} s")
```

También se verifica que ambas obtengan la misma ganancia:

```python
print(f"¿Misma solución?: {b[0] == c[0]}")
```

### ¿Qué deben explicar?

> "El enfoque B utiliza búsqueda lineal y tiene complejidad O(n²), mientras que C utiliza búsqueda binaria y tiene complejidad O(n log n). Por eso, al aumentar el número de tareas, la diferencia de tiempo se hace significativa."

El Reto 4 específicamente solicita la ejecución con `N = 100.000`, la comparación de tiempos y la explicación matemática de la mejora. 

---

# 14. ¿Qué debe señalar cada integrante?

Todos deberían conocer estas partes:

| Tema               | Línea / función                     | Qué explicar                             |
| ------------------ | ----------------------------------- | ---------------------------------------- |
| **Greedy**         | `greedy()`                          | Selecciona por mayor ganancia            |
| **Reto 1**         | `reto1()`                           | Greedy puede producir una ganancia menor |
| **Reto 2**         | `sorted(... t.fin)`                 | La DP necesita orden por finalización    |
| **Compatibilidad** | `tareas[j].fin <= tareas[i].inicio` | Determina si dos tareas pueden coexistir |
| **Reto 3**         | `dp[i] = max(tomar, no_tomar)`      | Decide tomar o no tomar                  |
| **B**              | `dp_lineal()`                       | Búsqueda lineal → O(n²)                  |
| **C**              | `dp_binaria()`                      | Búsqueda binaria → O(n log n)            |
| **Reto 4**         | `benchmark()`                       | Comparación con 100.000 tareas           |

---

# 15. Mapa rápido para la exposición

Si el profesor pregunta por cada reto:

### 🟢 Reto 1

**Señalar:**

```python
g = greedy(tareas)
d = dp_lineal(tareas)
```

**Explicar:**

> Greedy puede tomar una decisión local que produzca una ganancia total menor que la solución óptima.

---

### 🟠 Reto 2

**Señalar:**

```python
tareas = sorted(tareas, key=clave or (lambda t: t.fin))
```

**Explicar:**

> La DP necesita las tareas ordenadas por finalización para poder encontrar correctamente la última tarea compatible.

---

### 🔴 Reto 3

**Señalar:**

```python
dp[i] = max(tomar, no_tomar)
```

**Explicar:**

> Se compara ejecutar la tarea actual con conservar la mejor solución anterior.

---

### 🟣 Reto 4

**Señalar:**

```python
b = dp_lineal(tareas)
c = dp_binaria(tareas)
```

**Explicar:**

> B utiliza búsqueda lineal y es O(n²); C utiliza búsqueda binaria y es O(n log n).

---