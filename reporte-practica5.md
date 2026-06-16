---
layout: default
title: Práctica 5 — Chatbot híbrido con APIs externas de LLM
nav_order: 7
---

## 1. Objetivo

Modificar un chatbot con Ollama para que el backend FastAPI pueda consultar no solo un modelo local, sino también modelos remotos mediante APIs externas. El objetivo es comparar tres formas de usar modelos de lenguaje — local, remoto cerrado y remoto abierto — en términos de velocidad, tokens, calidad de respuesta, privacidad y facilidad de integración.

---

## 2. Arquitectura del sistema

El sistema mantiene la misma arquitectura de tres capas del proyecto base, agregando una capa de selección de proveedor en el backend:

```
Frontend (HTML/CSS/JS)
        ↓
Backend FastAPI (main.py)
        ↓
┌───────────────────────────────┐
│   Selector de proveedor       │
├──────────┬────────────────────┤
│  Ollama  │  Gemini  │  Groq  │
│  local   │   API    │   API  │
└──────────┴──────────┴────────┘
```

El frontend nunca accede directamente a las APIs externas — todas las llaves se guardan en el backend mediante variables de entorno (`.env`), nunca expuestas al navegador.

---

## 3. Estructura del proyecto

```
chatbot-copilotos-apis/
├── backend/
│   ├── main.py             # Backend FastAPI con soporte multi-proveedor
│   ├── requirements.txt    # Dependencias de Python
│   ├── .env                # Llaves de API (no se sube a GitHub)
│   └── .env.example        # Plantilla sin llaves reales
└── frontend/
    ├── index.html          # Interfaz del chatbot
    ├── styles.css          # Estilos visuales
    └── app.js              # Lógica de comunicación con el backend
```

### Archivos del proyecto

| Archivo | Descripción | Descarga |
|---------|-------------|---------|
| `main.py` | Backend FastAPI completo | [⬇ main.py](./backend/main.py) |
| `requirements.txt` | Dependencias de Python | [⬇ requirements.txt](./backend/requirements.txt) |
| `.env.example` | Plantilla de variables de entorno | [⬇ .env.example](./backend/.env.example) |
| `index.html` | Interfaz del chatbot | [⬇ index.html](./frontend/index.html) |
| `styles.css` | Estilos visuales | [⬇ styles.css](./frontend/styles.css) |
| `app.js` | Lógica del frontend | [⬇ app.js](./frontend/app.js) |

---

## 4. Proveedores y modelos utilizados

| Prueba | Proveedor | Modelo | Tipo |
|--------|-----------|--------|------|
| 1 | Ollama local | `llama3.2:3b` | Abierto / local |
| 2 | Google Gemini API | `gemini-2.5-flash-lite` | Cerrado / remoto |
| 3 | Groq API | `llama-3.3-70b-versatile` | Abierto / remoto |

---

## 5. Perfiles de copiloto implementados

Los perfiles se adaptaron a un caso de uso de gestión de alacena inteligente:

| Clave | Nombre | Descripción |
|-------|--------|-------------|
| `general` | Asistente general | Responde cualquier pregunta de forma clara y honesta |
| `nutriologo` | Nutriólogo | Planes de alimentación, porciones y valor nutricional |
| `compras` | Gestor de compras de alacena | Listas de supermercado, organización por sección, qué falta |
| `chef` | Chef inventarecetas | Recetas creativas con ingredientes disponibles |

---

## 6. Prompt de prueba

Se usó el mismo prompt en los tres proveedores para comparar en igualdad de condiciones:

> Explica qué es la odometría diferencial en un robot móvil de dos ruedas.  
> Incluye:  
> 1. explicación conceptual;  
> 2. ecuaciones básicas;  
> 3. ejemplo para estudiantes de ingeniería;  
> 4. una limitación práctica.  
> Responde en máximo 250 palabras.

**Configuración usada:**

| Parámetro | Valor |
|-----------|-------|
| `temperature` | 0.7 |
| `top_p` | 0.9 |
| `max_tokens` | 300 |
| `perfil` | Asistente general |

---

## 7. Capturas de pantalla

### Prueba 1 — Ollama local · `llama3.2:3b`

![Captura Ollama](_includes/practica5/capturas/captura-ollama.png)
> Tiempo backend: **44.782 s** · Tokens entrada: **143** · Tokens salida: **300** · Tokens/s: **9.75**  
> La respuesta quedó cortada al llegar al límite de 300 tokens antes de completar el punto 4.

---

### Prueba 2 — Google Gemini API · `gemini-2.5-flash-lite`

![Captura Gemini](_includes/practica5/capturas/captura-gemini.png)
> Tiempo backend: **2.484 s** · Tokens entrada: **106** · Tokens salida: **300** · Tokens/s: **120.77**  
> Respuesta más rápida de las tres pruebas, aunque también quedó cortada en el punto 3.

---

### Prueba 3 — Groq API · `llama-3.3-70b-versatile`

![Captura Groq](_includes/practica5/capturas/captura-groq.png)
> Tiempo backend: **8.633 s** · Tokens entrada: **153** · Tokens salida: **294** · Tokens/s: **34.06**  
> Única respuesta que completó los cuatro puntos solicitados sin ser cortada.

---

## 8. Tabla de métricas

| Variable | Ollama local | Gemini Flash Lite | Groq 70B |
|---|---|---|---|
| Proveedor | Ollama | Google | Groq |
| Modelo | `llama3.2:3b` | `gemini-2.5-flash-lite` | `llama-3.3-70b-versatile` |
| Tipo | Abierto / local | Cerrado / remoto | Abierto / remoto |
| Parámetros aprox. | 3B | No divulgado | 70B |
| Tokens entrada | 143 | 106 | 153 |
| Tokens salida | 300 | 300 | 294 |
| Tokens totales | 443 | 406 | 447 |
| Tiempo backend | 44.782 s | 2.484 s | 8.633 s |
| Tokens/s aprox. | 9.75 | 120.77 | 34.06 |
| Respuesta completa |  Cortada |  Cortada |  Completa |
| Requiere internet | No | Sí | Sí |
| Requiere API key | No | Sí | Sí |
| Costo | Hardware local | Tier gratuito / pago | Free plan / pago |
| Privacidad | Alta (datos locales) | Depende del proveedor | Depende del proveedor |

---

## 9. Evaluación cualitativa de respuestas

Escala: 1 = deficiente · 2 = básico · 3 = aceptable · 4 = bueno · 5 = excelente

| Criterio | Ollama `llama3.2:3b` | Gemini `flash-lite` | Groq `llama-3.3-70b` |
|---|:---:|:---:|:---:|
| Claridad conceptual | 4 | 3 | 4 |
| Precisión técnica | 5 | 3 | 3 |
| Calidad del ejemplo | 5 | 5 | 5 |
| Identificación de limitaciones | 0 | 0 | 5 |
| Utilidad general | 5 | 5 | 5 |
| **Promedio** | **3.8** | **3.2** | **4.4** |

> **Nota:** Ollama e Identificación de limitaciones recibieron 0 porque la respuesta fue cortada antes de llegar al punto 4, no necesariamente porque el modelo sea incapaz de identificarlas.

---

## 10. Análisis comparativo

### ¿Qué modelo respondió más rápido?

Gemini Flash Lite fue el más rápido con **2.484 s** y **120.77 tokens/s** — aproximadamente 18 veces más rápido que Ollama local (44.782 s) y 5 veces más rápido que Groq (8.633 s). Esto se explica porque Gemini corre en infraestructura optimizada de Google, mientras que Ollama depende del hardware local disponible sin GPU dedicada.

### ¿Qué modelo dio la mejor explicación técnica?

En términos de calidad global, **Groq con llama-3.3-70b** obtuvo el mejor promedio (4.4/5). Su respuesta fue la única que completó los cuatro puntos solicitados sin ser cortada, incluyendo una limitación práctica clara sobre el deslizamiento de ruedas. Ollama fue preciso técnicamente pero incompleto. Gemini fue el más débil en precisión técnica en esta prueba.

### ¿El modelo más grande fue siempre mejor?

No necesariamente. Groq con 70B obtuvo el mejor promedio cualitativo, pero Ollama con solo 3B fue más preciso en las ecuaciones que presentó. El tamaño del modelo es un factor, pero la infraestructura, el límite de tokens y el tipo de tarea también influyen en el resultado final.

### ¿Qué diferencia hubo entre ejecutar localmente y usar una API?

La diferencia más notable fue la velocidad: las APIs externas respondieron en segundos mientras que Ollama tardó casi 45 segundos corriendo en CPU local. En términos de calidad, los resultados fueron comparables. La principal ventaja de Ollama es que los datos no salen de la computadora.

### ¿Qué riesgos aparecen al enviar datos a un proveedor externo?

Al usar Gemini o Groq, el prompt completo viaja por internet hacia servidores de terceros. No se tiene control sobre cómo se almacena, procesa o utiliza esa información. Para datos sensibles — información médica, datos personales, documentos institucionales — esto representa un riesgo real de privacidad y gobernanza de datos.

### ¿Cuándo conviene usar Ollama local vs API externa?

**Ollama local conviene cuando:** los datos son sensibles o confidenciales, se trabaja sin internet, se quiere control total del entorno, o el costo por tokens sería elevado a largo plazo.

**API externa conviene cuando:** se necesita velocidad de respuesta, se requiere un modelo más grande del que el hardware puede correr, se está prototipando rápidamente, o se necesitan capacidades avanzadas sin inversión en hardware.

### ¿Qué proveedor fue más fácil de integrar?

Groq fue el más directo porque usa la misma interfaz compatible con OpenAI, lo que significa que el mismo código `call_openai_compatible()` sirve para ambos sin modificaciones. Gemini requirió su propio SDK (`google-genai`) con una estructura de llamada diferente.

### ¿Qué información técnica no fue publicada por los proveedores?

Google no divulga el número de parámetros de sus modelos Gemini ni detalles de arquitectura interna. Groq usa modelos abiertos (Llama) cuyos parámetros son conocidos públicamente, pero su hardware de inferencia (LPU) no se documenta en detalle.

---

## 11. Consideraciones de seguridad

- El archivo `.env` con las API keys **no se sube a GitHub** — está incluido en `.gitignore`.
- El frontend nunca contiene llaves de API; toda autenticación ocurre en el backend.
- Para esta práctica se usaron prompts técnicos genéricos sin información personal ni institucional sensible.
- Si en el futuro se integraran documentos internos o datos de usuarios reales, se deberá revisar la política de datos de cada proveedor antes de usarlo.

---

## 12. Conclusiones

Esta práctica permitió observar de forma concreta que un LLM no es solo un modelo, sino parte de un sistema completo que involucra interfaz, backend, red, costos, seguridad y experiencia del usuario. Los tres enfoques comparados tienen ventajas y limitaciones reales que dependen del contexto de uso.

La velocidad de las APIs externas es una ventaja clara para prototipos, pero la privacidad y el control que ofrece Ollama local son irreemplazables cuando los datos son sensibles. La decisión correcta no es "cuál es mejor" sino **cuál es adecuado para esta tarea, con estos datos, este presupuesto y esta latencia esperada**.

---

## 13. Referencias

1. Ollama. (s. f.). *Chat API*. https://docs.ollama.com/api/chat  
2. FastAPI. (s. f.). *Request body*. https://fastapi.tiangolo.com/tutorial/body/  
3. Google AI for Developers. (2026). *Gemini API Documentation*. https://ai.google.dev/gemini-api/docs  
4. Groq. (s. f.). *GroqCloud Documentation*. https://console.groq.com/docs  
5. OpenAI. (s. f.). *API Documentation*. https://platform.openai.com/docs  
6. Giron, H. (2026). *APIs externas LLM*. https://hubergiron.github.io/llm-ollama/tema5-apis-llm-externas/
