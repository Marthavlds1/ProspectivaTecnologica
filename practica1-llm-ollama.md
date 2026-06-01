---
layout: default
title: Práctica 1 — Instalación, ejecución y comparación de modelos LLM con Ollama
nav_order: 3
---

# Práctica 1 — Instalación, ejecución y comparación de modelos LLM con Ollama y Hugging Face

## Objetivo

Instalar y usar Ollama desde terminal, consultar modelos en Hugging Face, ejecutar al menos seis modelos con los mismos prompts y construir una tabla comparativa que permita analizar diferencias entre fabricante, licencia, tamaño, idioma y requerimientos técnicos.

---

## 1. Instalación de Ollama

Ollama se instaló en Windows descargando el instalador oficial desde [ollama.com/download](https://ollama.com/download). Una vez ejecutado el instalador, se verificó la instalación desde la terminal con:

```
ollama --version
```

La versión instalada fue `ollama version 0.24.0`.

**Evidencia — verificación de versión:**

<!-- Insertar captura de pantalla de ollama --version -->
![Verificación de versión de Ollama](assets/img/practica1/ollama-version.png)

---

## 2. Especificaciones del equipo

La práctica se realizó en una computadora con Windows con las siguientes características relevantes:

| Componente | Detalle |
|---|---|
| RAM total | 16.0 GB |
| Almacenamiento | SSD NVMe |
| GPU dedicada | No disponible |

Como dato de referencia, al ejecutar el modelo Gemma 3 4B se observó un uso de memoria RAM del **86% (13.5 / 15.7 GB)**. Esto ilustra el impacto que tiene correr modelos locales en los recursos del sistema, especialmente en equipos sin GPU dedicada.

**Evidencia — uso de memoria con Gemma 3 4B activo:**

<!-- Insertar captura del Administrador de tareas mostrando 86% de RAM -->
![Uso de memoria RAM con Gemma 3 4B](assets/img/practica1/memoria-gemma.png)

---

## 3. Descarga de modelos

Se descargaron cinco modelos ejecutando los siguientes comandos uno por uno:

```
ollama pull llama3.2:3b
ollama pull gemma3:4b
ollama pull qwen2.5:7b
ollama pull phi4-mini
ollama pull tinyllama:1.1b-chat-v1-q8_0
```

**Evidencia — descarga de modelos:**

<!-- Insertar captura de pantalla de las descargas -->
![Descarga de modelos con ollama pull](assets/img/practica1/ollama-pull.png)

---

## 4. Verificación de modelos instalados

Una vez descargados todos los modelos, se verificó la lista con:

```
ollama ls
```

**Evidencia — lista de modelos instalados:**

<!-- Insertar captura de pantalla de ollama ls -->
![Lista de modelos con ollama ls](assets/img/practica1/ollama-ls.png)

---

## 5. Consideraciones previas a la ejecución

Antes de ejecutar los modelos, se identificaron dos criterios importantes:

**Tamaño en parámetros (B):** El número de parámetros de un modelo (expresado en "B" de billones) indica su capacidad de razonamiento. Un modelo con más parámetros no necesariamente es más rápido, pero tiende a generar respuestas más completas y precisas. Por ejemplo, `qwen2.5:7b` tiene 7 mil millones de parámetros mientras que `tinyllama:1.1b` tiene solo 1.1 mil millones.

**Tipo de modelo:** Los modelos de tipo *instruct* o *text* trabajan exclusivamente con texto. Los modelos *multimodal* pueden procesar tanto texto como imágenes. En esta práctica, Gemma 3 4B es el único modelo multimodal del conjunto, lo que permitió probarlo con una imagen real.

---

## 6. Prompts utilizados

Se utilizaron prompts diferenciados según las capacidades de cada modelo.

### Prompt estándar en español (modelos instruct/texto)
```
Explica la diferencia entre inteligencia artificial, aprendizaje automático,
IA generativa y LLM para estudiantes universitarios. Responde en español,
con tono académico y máximo 200 palabras.
```

### Prompt en inglés (TinyLlama)
TinyLlama fue entrenado principalmente en inglés, por lo que se utilizó el prompt en su idioma nativo para obtener una respuesta de mayor calidad:
```
Explain the difference between artificial intelligence, machine learning,
generative AI, and LLMs for undergraduate students. Respond in English,
with an academic tone and a maximum of 200 words.
```

### Prompt con imagen (Gemma 3 4B — modelo multimodal)
Al ser un modelo multimodal, Gemma 3 4B se probó con una imagen real del sistema:
```
ollama run gemma3:4b "Describe detalladamente esta imagen: C:\Users\A224765\OneDrive - Universidad Iberoamericana A.C. ACAD\Pictures\Screenshots\Screenshot 2026-06-01 165615.png"
```

### Prompts complementarios (todos los modelos)
```
Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica
dentro de un repositorio de documentos académicos.
```
```
Menciona tres riesgos académicos de usar LLM sin verificar fuentes.
Incluye un ejemplo breve para cada riesgo.
```
```
Dame un ejemplo de cómo un estudiante de ingeniería podría usar un LLM
para apoyar el desarrollo de un proyecto con ESP32, sin sustituir su aprendizaje.
```

---

## 7. Ejecución de modelos

### TinyLlama 1.1B

Modelo más pequeño del conjunto (1.1B parámetros). Se ejecutó con el prompt en inglés por ser su idioma principal de entrenamiento.

```
ollama run tinyllama:1.1b-chat-v1-q8_0 "Explain the difference between artificial intelligence, machine learning, generative AI, and LLMs for undergraduate students. Respond in English, with an academic tone and a maximum of 200 words."
```
```
ollama run tinyllama:1.1b-chat-v1-q8_0 "Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica dentro de un repositorio de documentos académicos."
```
```
ollama run tinyllama:1.1b-chat-v1-q8_0 "Menciona tres riesgos académicos de usar LLM sin verificar fuentes. Incluye un ejemplo breve para cada riesgo."
```
```
ollama run tinyllama:1.1b-chat-v1-q8_0 "Dame un ejemplo de cómo un estudiante de ingeniería podría usar un LLM para apoyar el desarrollo de un proyecto con ESP32, sin sustituir su aprendizaje."
```

<!-- Insertar captura de pantalla de tinyllama respondiendo -->
![Ejecución de TinyLlama](assets/img/practica1/run-tinyllama.png)

---

### Phi4-mini (3.8B)

```
ollama run phi4-mini "Explica la diferencia entre inteligencia artificial, aprendizaje automático, IA generativa y LLM para estudiantes universitarios. Responde en español, con tono académico y máximo 200 palabras."
```
```
ollama run phi4-mini "Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica dentro de un repositorio de documentos académicos."
```
```
ollama run phi4-mini "Menciona tres riesgos académicos de usar LLM sin verificar fuentes. Incluye un ejemplo breve para cada riesgo."
```
```
ollama run phi4-mini "Dame un ejemplo de cómo un estudiante de ingeniería podría usar un LLM para apoyar el desarrollo de un proyecto con ESP32, sin sustituir su aprendizaje."
```

<!-- Insertar captura de pantalla de phi4-mini respondiendo -->
![Ejecución de Phi4-mini](assets/img/practica1/run-phi4.png)

---

### Llama 3.2 3B

```
ollama run llama3.2:3b "Explica la diferencia entre inteligencia artificial, aprendizaje automático, IA generativa y LLM para estudiantes universitarios. Responde en español, con tono académico y máximo 200 palabras."
```
```
ollama run llama3.2:3b "Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica dentro de un repositorio de documentos académicos."
```
```
ollama run llama3.2:3b "Menciona tres riesgos académicos de usar LLM sin verificar fuentes. Incluye un ejemplo breve para cada riesgo."
```
```
ollama run llama3.2:3b "Dame un ejemplo de cómo un estudiante de ingeniería podría usar un LLM para apoyar el desarrollo de un proyecto con ESP32, sin sustituir su aprendizaje."
```

<!-- Insertar captura de pantalla de llama3.2:3b respondiendo -->
![Ejecución de Llama 3.2 3B](assets/img/practica1/run-llama.png)

---

### Gemma 3 4B — Modelo multimodal

Gemma 3 4B es el único modelo multimodal de la práctica, capaz de procesar tanto texto como imágenes. Se probó primero con los prompts de texto y después con una imagen real.

```
ollama run gemma3:4b "Explica la diferencia entre inteligencia artificial, aprendizaje automático, IA generativa y LLM para estudiantes universitarios. Responde en español, con tono académico y máximo 200 palabras."
```
```
ollama run gemma3:4b "Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica dentro de un repositorio de documentos académicos."
```
```
ollama run gemma3:4b "Menciona tres riesgos académicos de usar LLM sin verificar fuentes. Incluye un ejemplo breve para cada riesgo."
```
```
ollama run gemma3:4b "Dame un ejemplo de cómo un estudiante de ingeniería podría usar un LLM para apoyar el desarrollo de un proyecto con ESP32, sin sustituir su aprendizaje."
```

**Prueba multimodal con imagen:**
```
ollama run gemma3:4b "Describe detalladamente esta imagen: C:\Users\A224765\OneDrive - Universidad Iberoamericana A.C. ACAD\Pictures\Screenshots\Screenshot 2026-06-01 165615.png"
```

El modelo describió correctamente el contenido de la imagen, demostrando su capacidad multimodal a diferencia de los demás modelos del conjunto.

<!-- Insertar captura de pantalla de gemma3:4b respondiendo texto -->
![Ejecución de Gemma 3 4B — texto](assets/img/practica1/run-gemma.png)

<!-- Insertar captura de pantalla de gemma3:4b describiendo la imagen -->
![Ejecución de Gemma 3 4B — imagen](assets/img/practica1/run-gemma-imagen.png)

---

### Qwen 2.5 7B

```
ollama run qwen2.5:7b "Explica la diferencia entre inteligencia artificial, aprendizaje automático, IA generativa y LLM para estudiantes universitarios. Responde en español, con tono académico y máximo 200 palabras."
```
```
ollama run qwen2.5:7b "Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica dentro de un repositorio de documentos académicos."
```
```
ollama run qwen2.5:7b "Menciona tres riesgos académicos de usar LLM sin verificar fuentes. Incluye un ejemplo breve para cada riesgo."
```
```
ollama run qwen2.5:7b "Dame un ejemplo de cómo un estudiante de ingeniería podría usar un LLM para apoyar el desarrollo de un proyecto con ESP32, sin sustituir su aprendizaje."
```

<!-- Insertar captura de pantalla de qwen2.5:7b respondiendo -->
![Ejecución de Qwen 2.5 7B](assets/img/practica1/run-qwen.png)

---

## 8. Tabla comparativa de modelos

Información obtenida de las model cards de Hugging Face y de la terminal con `ollama ls`.

| Modelo | Fabricante | Tipo | Licencia | Parámetros | Idiomas reportados | Requerimiento sugerido | Tamaño en Ollama |
|---|---|---|---|---|---|---|---|
| TinyLlama 1.1B Chat | TinyLlama | LLM chat compacto — solo texto | Apache 2.0 | 1.1B | Principalmente inglés | Equipos con recursos limitados | <!-- Completar con ollama ls --> |
| Phi-4-mini-instruct | Microsoft | LLM instruct compacto — solo texto | MIT | 3.8B | Árabe, chino, inglés, francés, alemán, español, entre otros | 8 GB RAM | <!-- Completar con ollama ls --> |
| Llama 3.2 3B Instruct | Meta | LLM instruct — solo texto | Llama 3.2 Community License | 3.21B | Inglés, alemán, francés, italiano, portugués, hindi, español y tailandés | 8 GB RAM o más | <!-- Completar con ollama ls --> |
| Gemma 3 4B IT | Google | LLM instruct multimodal — texto e imagen | Gemma License | 4B | Más de 140 idiomas | 8 GB RAM o más | <!-- Completar con ollama ls --> |
| Qwen2.5 7B Instruct | Qwen / Alibaba | LLM instruct — solo texto | Apache 2.0 | 7.61B | Más de 29 idiomas, incluye español | 16 GB RAM o GPU | <!-- Completar con ollama ls --> |

---

## 9. Reflexión

**¿Qué modelo fue más fácil de instalar y ejecutar?**

Todos los modelos se instalaron de la misma forma mediante `ollama pull`, sin pasos adicionales. En cuanto a ejecución, TinyLlama 1.1B fue el más inmediato: arrancó y respondió en segundos. Phi4-mini también resultó ágil, con una latencia notablemente menor que los modelos más grandes.

**¿Qué modelo respondió mejor en español?**

TinyLlama fue entrenado principalmente en inglés, por lo que se ejecutó con el prompt en ese idioma para obtener mejores resultados. Phi4-mini y Llama 3.2 3B respondieron correctamente en español con buena estructura y coherencia académica. Gemma 3 4B respondió pero con menor adecuación al contexto solicitado.

**¿Qué diferencia observaste entre un modelo pequeño y uno más grande?**

La diferencia más evidente fue el tiempo de respuesta. TinyLlama 1.1B respondió casi de forma inmediata, mientras que Llama 3.2 3B tardó aproximadamente un minuto o más. Los modelos con más parámetros tienden a producir respuestas más elaboradas y precisas, pero a costa de mayor tiempo de cómputo y uso de memoria RAM. Esto confirma que un mayor número de parámetros (B) implica mayor capacidad de razonamiento, aunque no necesariamente mayor velocidad.

**¿Qué importancia tiene la licencia del modelo?**

La licencia determina cómo puede usarse el modelo legalmente. Modelos con licencia Apache 2.0 como Qwen2.5 permiten uso comercial y modificación libre, mientras que la Llama 3.2 Community License de Meta impone restricciones que deben leerse antes de publicar o distribuir proyectos. En contexto académico, ignorar la licencia puede representar un problema ético o legal.

**¿Por qué no debe usarse un LLM como única fuente académica?**

Los LLM generan respuestas con base en patrones estadísticos, no a partir de búsquedas verificadas. Pueden producir afirmaciones incorrectas o inventadas con apariencia de veracidad, fenómeno conocido como alucinación. Una respuesta fluida no equivale a una respuesta correcta, por lo que cualquier información generada debe verificarse con fuentes primarias.

**¿Qué ventajas y limitaciones tiene ejecutar modelos localmente?**

La principal ventaja es la privacidad: los datos no salen de la computadora y no se depende de una API externa. Como limitación, el rendimiento depende del hardware disponible. Al correr Gemma 3 4B se observó un uso de RAM del 86% (13.5 de 15.7 GB), lo que indica que en equipos sin GPU dedicada los modelos grandes pueden saturar los recursos del sistema.

---

## Referencias

- Ollama. (2025). *CLI Reference*. [https://docs.ollama.com/cli](https://docs.ollama.com/cli)
- Hugging Face. (2025). *Model Cards*. [https://huggingface.co/docs/hub/en/model-cards](https://huggingface.co/docs/hub/en/model-cards)
- Meta. *Llama-3.2-3B-Instruct*. [https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
- Google. *Gemma 3 4B IT*. [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)
- Qwen / Alibaba. *Qwen2.5-7B-Instruct*. [https://huggingface.co/Qwen/Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- Microsoft. *Phi-4-mini-instruct*. [https://huggingface.co/microsoft/Phi-4-mini-instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct)
- TinyLlama. *TinyLlama-1.1B-Chat-v1.0*. [https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0)