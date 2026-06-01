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

Cada modelo se ejecutó con el comando `ollama run` seguido del mismo prompt. Ejemplo con el primer modelo:

```
ollama run llama3.2:3b "Explica la diferencia entre inteligencia artificial, aprendizaje automático, IA generativa y LLM para estudiantes universitarios. Responde en español, con tono académico y máximo 200 palabras."
```

**Evidencia — ejecución de modelos:**

<!-- Insertar capturas de pantalla de cada modelo respondiendo -->
![Ejecución de llama3.2:3b](assets/img/practica1/run-llama.png)

<!-- Insertar captura de pantalla de gemma3:4b -->
![Ejecución de gemma3:4b](assets/img/practica1/run-gemma.png)

<!-- Insertar captura de pantalla de qwen2.5:7b -->
![Ejecución de qwen2.5:7b](assets/img/practica1/run-qwen.png)

<!-- Insertar captura de pantalla de mistral:7b -->
![Ejecución de mistral:7b](assets/img/practica1/run-mistral.png)

<!-- Insertar captura de pantalla de phi4-mini -->
![Ejecución de phi4-mini](assets/img/practica1/run-phi4.png)

<!-- Insertar captura de pantalla de tinyllama -->
![Ejecución de tinyllama](assets/img/practica1/run-tinyllama.png)

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

<!-- Escribir respuesta aquí -->

**¿Qué modelo respondió mejor en español?**

<!-- Escribir respuesta aquí -->

**¿Qué diferencia observaste entre un modelo pequeño y uno más grande?**

<!-- Escribir respuesta aquí -->

**¿Qué importancia tiene la licencia del modelo?**

<!-- Escribir respuesta aquí -->

**¿Por qué no debe usarse un LLM como única fuente académica?**

<!-- Escribir respuesta aquí -->

**¿Qué ventajas y limitaciones tiene ejecutar modelos localmente?**

<!-- Escribir respuesta aquí -->

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
