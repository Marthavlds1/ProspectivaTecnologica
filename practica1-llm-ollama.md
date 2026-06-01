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

**Evidencia — verificación de versión:**

<!-- Insertar captura de pantalla de ollama --version -->
![Verificación de versión de Ollama](assets/img/practica1/ollama-version.png)

---

## 2. Descarga de modelos

Se descargaron seis modelos ejecutando los siguientes comandos uno por uno:

```
ollama pull llama3.2:3b
ollama pull gemma3:4b
ollama pull qwen2.5:7b
ollama pull mistral:7b
ollama pull phi4-mini
ollama pull tinyllama:1.1b-chat-v1-q8_0
```

**Evidencia — descarga de modelos:**

<!-- Insertar captura de pantalla de las descargas -->
![Descarga de modelos con ollama pull](assets/img/practica1/ollama-pull.png)

---

## 3. Verificación de modelos instalados

Una vez descargados todos los modelos, se verificó la lista de modelos disponibles localmente con:

```
ollama ls
```

**Evidencia — lista de modelos instalados:**

<!-- Insertar captura de pantalla de ollama ls -->
![Lista de modelos con ollama ls](assets/img/practica1/ollama-ls.png)

---

## 4. Prompts utilizados

Para garantizar una comparación equitativa, se usaron los mismos cuatro prompts en todos los modelos.

**Prompt 1 — Explicación conceptual:**
```
Explica la diferencia entre inteligencia artificial, aprendizaje automático,
IA generativa y LLM para estudiantes universitarios. Responde en español,
con tono académico y máximo 200 palabras.
```

**Prompt 2 — Embeddings:**
```
Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica
dentro de un repositorio de documentos académicos.
```

**Prompt 3 — Evaluación crítica:**
```
Menciona tres riesgos académicos de usar LLM sin verificar fuentes.
Incluye un ejemplo breve para cada riesgo.
```

**Prompt 4 — Uso técnico:**
```
Dame un ejemplo de cómo un estudiante de ingeniería podría usar un LLM
para apoyar el desarrollo de un proyecto con ESP32, sin sustituir su aprendizaje.
```

---

## 5. Ejecución de modelos

Cada modelo se ejecutó con el comando `ollama run` seguido del mismo prompt. A continuación se muestran los comandos utilizados para cada modelo con los cuatro prompts.

---

### TinyLlama 1.1B

```
ollama run tinyllama:1.1b-chat-v1-q8_0 "Explica la diferencia entre inteligencia artificial, aprendizaje automático, IA generativa y LLM para estudiantes universitarios. Responde en español, con tono académico y máximo 200 palabras."
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
![Ejecución de tinyllama](assets/img/practica1/run-tinyllama.png)

---

### Phi4-mini

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
![Ejecución de phi4-mini](assets/img/practica1/run-phi4.png)

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
![Ejecución de llama3.2:3b](assets/img/practica1/run-llama.png)

---

### Gemma 3 4B

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

<!-- Insertar captura de pantalla de gemma3:4b respondiendo -->
![Ejecución de gemma3:4b](assets/img/practica1/run-gemma.png)

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
![Ejecución de qwen2.5:7b](assets/img/practica1/run-qwen.png)

---

### Mistral 7B

```
ollama run mistral:7b "Explica la diferencia entre inteligencia artificial, aprendizaje automático, IA generativa y LLM para estudiantes universitarios. Responde en español, con tono académico y máximo 200 palabras."
```
```
ollama run mistral:7b "Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica dentro de un repositorio de documentos académicos."
```
```
ollama run mistral:7b "Menciona tres riesgos académicos de usar LLM sin verificar fuentes. Incluye un ejemplo breve para cada riesgo."
```
```
ollama run mistral:7b "Dame un ejemplo de cómo un estudiante de ingeniería podría usar un LLM para apoyar el desarrollo de un proyecto con ESP32, sin sustituir su aprendizaje."
```

<!-- Insertar captura de pantalla de mistral:7b respondiendo -->
![Ejecución de mistral:7b](assets/img/practica1/run-mistral.png)

---

## 6. Tabla comparativa de modelos

Información obtenida de las model cards de Hugging Face y de la terminal con `ollama ls`.

| Modelo | Fabricante | Tipo | Licencia | Parámetros | Idiomas reportados | Requerimiento sugerido | Tamaño en Ollama |
|---|---|---|---|---|---|---|---|
| Llama 3.2 3B Instruct | Meta | LLM instruct, texto a texto | Llama 3.2 Community License | 3.21B | Inglés, alemán, francés, italiano, portugués, hindi, español y tailandés | 8 GB RAM o más | <!-- Completar con ollama ls --> |
| Gemma 3 4B IT | Google | LLM instruct multimodal | Gemma License | 4B | Más de 140 idiomas | 8 GB RAM o más | <!-- Completar con ollama ls --> |
| Qwen2.5 7B Instruct | Qwen / Alibaba | LLM instruct | Apache 2.0 | 7.61B | Más de 29 idiomas, incluye español | 16 GB RAM o GPU | <!-- Completar con ollama ls --> |
| Mistral 7B Instruct v0.3 | Mistral AI | LLM instruct | Apache 2.0 | 7B | Sin lista cerrada declarada; se evaluó en español | 16 GB RAM o GPU | <!-- Completar con ollama ls --> |
| Phi-4-mini-instruct | Microsoft | LLM instruct compacto | MIT | 3.8B | Árabe, chino, inglés, francés, alemán, español, entre otros | 8 GB RAM | <!-- Completar con ollama ls --> |
| TinyLlama 1.1B Chat | TinyLlama | LLM chat compacto | Apache 2.0 | 1.1B | Principalmente inglés | Equipos con recursos limitados | <!-- Completar con ollama ls --> |

---

## 7. Reflexión

**¿Qué modelo fue más fácil de instalar y ejecutar?**

Todos los modelos se instalaron de manera similar mediante `ollama pull`, sin pasos adicionales de configuración. Sin embargo, en cuanto a ejecución, TinyLlama 1.1B fue el más inmediato: arrancó y respondió en segundos, sin tiempo de espera perceptible. Phi4-mini también resultó ágil, con una latencia notablemente menor que los modelos de mayor tamaño.

**¿Qué modelo respondió mejor en español?**

TinyLlama, Phi4-mini y Llama 3.2 3B respondieron correctamente en español sin necesidad de ajustes adicionales en el prompt. De los tres, Llama 3.2 y Phi4-mini ofrecieron respuestas más estructuradas y con mayor coherencia académica, aunque TinyLlama destacó por su velocidad de respuesta. Gemma 3 4B, en cambio, no respondió de forma del todo adecuada al contexto solicitado.

**¿Qué diferencia observaste entre un modelo pequeño y uno más grande?**

La diferencia más evidente fue el tiempo de respuesta. TinyLlama 1.1B respondió de manera casi inmediata, mientras que Llama 3.2 3B tardó aproximadamente un minuto o más en generar su respuesta. Sin embargo, los modelos más grandes tendieron a producir respuestas más elaboradas y mejor redactadas. Esto sugiere que existe un balance entre velocidad y calidad: los modelos pequeños son más ágiles pero pueden sacrificar profundidad, mientras que los modelos más grandes generan contenido de mayor calidad a costa de mayor tiempo de cómputo.

**¿Qué importancia tiene la licencia del modelo?**

La licencia determina cómo puede usarse el modelo legalmente. Por ejemplo, modelos con licencia Apache 2.0 como Qwen2.5 y Mistral permiten uso comercial y modificación libre, mientras que la Llama 3.2 Community License de Meta impone restricciones que deben leerse antes de usar el modelo en proyectos públicos o comerciales. En un contexto académico, ignorar la licencia puede representar un problema ético o legal, especialmente si el trabajo se publica o distribuye.

**¿Por qué no debe usarse un LLM como única fuente académica?**

Los LLM generan respuestas con base en patrones estadísticos aprendidos durante el entrenamiento, no a partir de una búsqueda verificada de información. Esto significa que pueden producir afirmaciones incorrectas, desactualizadas o directamente inventadas con apariencia de veracidad, fenómeno conocido como alucinación. En un contexto universitario, esto representa un riesgo serio: una respuesta fluida no equivale a una respuesta correcta. Por ello, cualquier información generada por un LLM debe verificarse con fuentes primarias como artículos científicos, documentación oficial o libros especializados.

**¿Qué ventajas y limitaciones tiene ejecutar modelos localmente?**

La principal ventaja de ejecutar modelos localmente con Ollama es la privacidad: los datos no salen de la computadora y no se depende de una API externa ni de conexión a internet constante. Además, permite experimentar libremente con distintos modelos sin costo por uso. Como limitación, el rendimiento depende directamente del hardware disponible: en equipos sin GPU dedicada, los modelos de 7B pueden ser lentos o difíciles de correr fluidamente. También el espacio en disco es un factor, ya que cada modelo ocupa entre 600 MB y más de 4 GB.

---

## Referencias

- Ollama. (2025). *CLI Reference*. [https://docs.ollama.com/cli](https://docs.ollama.com/cli)
- Hugging Face. (2025). *Model Cards*. [https://huggingface.co/docs/hub/en/model-cards](https://huggingface.co/docs/hub/en/model-cards)
- Meta. *Llama-3.2-3B-Instruct*. [https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
- Google. *Gemma 3 4B IT*. [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)
- Qwen / Alibaba. *Qwen2.5-7B-Instruct*. [https://huggingface.co/Qwen/Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- Mistral AI. *Mistral-7B-Instruct-v0.3*. [https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)
- Microsoft. *Phi-4-mini-instruct*. [https://huggingface.co/microsoft/Phi-4-mini-instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct)
- TinyLlama. *TinyLlama-1.1B-Chat-v1.0*. [https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0)