---
layout: default
title: Práctica 3 — Implementación de chatbot web con LLM local
nav_order: 5
---

# Práctica 3 — Implementación de chatbot web con LLM local

## Objetivo

Implementar un chatbot web cliente-servidor que permita conversar con un LLM local mediante Ollama, configurar parámetros de generación desde el frontend y visualizar métricas técnicas por cada respuesta. En este caso, el chatbot fue extendido como panel de administración del sistema de alacena inteligente, integrando además la visualización del historial de mensajes de WhatsApp y el control del bot de notificaciones.

---

## 1. Arquitectura implementada

La arquitectura desarrollada sigue el modelo cliente-servidor propuesto en la guía, extendido con capas adicionales para la integración con WhatsApp y el inventario de la alacena.

```
Usuario (navegador)
       ↓
Frontend HTML/CSS/JS — admin.html (puerto 5500)
       ↓
Backend Python — FastAPI (puerto 8000)
       ↓
Ollama API local (puerto 11434)
       ↓
Modelo LLM local — qwen2.5:7b
```

El backend también se comunica con:
- `/inventory/db` — inventario real desde SQLite
- `/chat/historial` — historial de mensajes de WhatsApp
- `whatsapp_service.js` — bot de Node.js para WhatsApp Web

---

## 2. Estructura del proyecto

```
Proyecto-de-LLM-nutrimental/
├── backend/
│   └── app/
│       ├── main.py                        ← API principal con FastAPI
│       ├── api/
│       │   ├── routes_chat.py             ← Recibe mensajes de WhatsApp
│       │   └── routes_inventory.py        ← Gestión del inventario
│       └── services/
│           ├── llm_service.py             ← Lógica de intención y LLM
│           ├── recipe_service.py          ← Generación de recetas y lista de compras
│           └── whatsapp_service.js        ← Bot de WhatsApp Web (Node.js)
└── frontend/
    └── admin.html                         ← Panel de administración
```

---

## 3. Backend — FastAPI

El backend implementa tres grupos de endpoints:

**Chat con el LLM (panel admin):**
```
POST /chat/admin
```
Recibe el mensaje, modelo y parámetros desde el frontend, construye el payload para Ollama usando `/api/chat`, mide latencia y devuelve respuesta más métricas.

**Chat de WhatsApp:**
```
POST /chat          ← Recibe mensajes del bot de WhatsApp
GET  /chat/historial ← Devuelve el historial de conversaciones
```

**Control de servicios:**
```
GET  /services/status         ← Estado de Backend, Ollama y WhatsApp bot
POST /services/whatsapp/start ← Arranca el bot de Node.js
POST /services/whatsapp/stop  ← Detiene el bot
```

**Evidencia — backend corriendo:**

<!-- Insertar captura de pantalla del backend con Application startup complete -->
![Backend corriendo](assets/img/practica3/backend-running.png)

**Evidencia — prueba del endpoint /chat/admin:**

<!-- Insertar captura de pantalla de la prueba en /docs o con curl -->
![Prueba endpoint chat/admin](assets/img/practica3/endpoint-test.png)

---

## 4. Frontend — Panel de administración

El frontend es un archivo HTML/CSS/JS de una sola página dividido en tres columnas:

**Columna izquierda — Configuración del modelo:**
- Selector de modelo (llama3.2:3b, gemma3:4b, qwen2.5:7b, mistral:7b, phi4-mini, tinyllama)
- Sliders para temperature, top-p y repeat penalty
- Campo numérico para tokens máximos
- Selector de contexto (2048, 4096, 8192)
- Área de edición del system prompt

**Columna central — Chat con el LLM:**
- Área de conversación con burbujas de usuario y asistente
- Panel de métricas en tiempo real (tiempo total, tokens/s, tokens entrada/salida, tiempo Ollama, carga de modelo)
- Formulario de envío con soporte para Enter

**Columna derecha — Historial de WhatsApp:**
- Lista de mensajes recibidos y respuestas del bot
- Actualización automática cada 15 segundos

**Barra de estado superior:**
- Indicadores en tiempo real del estado de Backend, Ollama y WhatsApp Bot
- Botón para iniciar o detener el WhatsApp Bot desde el frontend

**Evidencia — frontend funcionando:**

<!-- Insertar captura de pantalla del panel de administración -->
![Panel de administración](assets/img/practica3/admin-panel.png)

**Evidencia — métricas visibles:**

<!-- Insertar captura de pantalla mostrando las métricas después de una respuesta -->
![Métricas visibles](assets/img/practica3/metricas.png)

**Evidencia — historial de WhatsApp:**

<!-- Insertar captura de pantalla del panel derecho con mensajes de WhatsApp -->
![Historial de WhatsApp](assets/img/practica3/whatsapp-historial.png)

---

## 5. Parámetros configurados

| Parámetro | Control | Rango | Valor seleccionado |
|---|---|---|---|
| model | Selector | Modelos instalados | qwen2.5:7b |
| temperature | Slider | 0.0 a 1.2 | 0.4 |
| top_p | Slider | 0.1 a 1.0 | 0.9 |
| num_predict | Campo numérico | 20 a 1000 | 160 |
| num_ctx | Selector | 2048, 4096, 8192 | 4096 |
| repeat_penalty | Slider | 1.0 a 2.0 | 1.1 |

---

## 6. Pruebas realizadas

Se probaron los siguientes prompts con el modelo seleccionado:

| Tipo | Prompt | Resultado |
|---|---|---|
| Conceptual | "Explica qué es un sensor ultrasónico para estudiantes de primer semestre." | Respuesta clara y estructurada en español |
| Técnico | "Dame un ejemplo de código Arduino para leer un sensor HC-SR04." | Código funcional con comentarios |
| Aplicación al proyecto | "¿Cómo podría un LLM ayudar a una alacena inteligente a detectar ingredientes faltantes?" | Respuesta contextualizada y precisa |
| Robótica | "Explica cómo un robot móvil puede usar visión artificial para detectar objetos." | Respuesta ordenada y académica |

**Evidencia — prueba en el chat:**

<!-- Insertar captura de pantalla de una conversación en el chat del panel -->
![Prueba en el chat](assets/img/practica3/chat-test.png)

---

## 7. Métricas observadas

Las métricas se midieron con `qwen2.5:7b` a `temperature=0.4`:

| Métrica | Valor observado |
|---|---|
| Tiempo backend (wall_time_s) | ~28–35 s |
| Tiempo Ollama (total_duration_s) | ~27–34 s |
| Carga del modelo (load_duration_s) | ~0.01 s (ya cargado) |
| Tokens de entrada | ~55–70 |
| Tokens de salida | ~140–160 |
| Tokens totales | ~200–230 |
| Tokens por segundo | ~4.5–5.2 |

---

## 8. Reflexión técnica

**¿Qué modelo local utilizaste?**

Se utilizó `qwen2.5:7b` de Alibaba/Qwen como modelo principal. Fue el que produjo las respuestas más coherentes, precisas y bien estructuradas del conjunto evaluado en las prácticas anteriores. A diferencia de modelos más pequeños, qwen2.5:7b no inventa información ni genera respuestas genéricas repetitivas, lo que lo hace más confiable para el contexto de la alacena inteligente.

**¿Qué parámetros configuraste desde el frontend?**

Se configuró `temperature=0.4`, `top_p=0.9`, `num_predict=160`, `num_ctx=4096` y `repeat_penalty=1.1`. La temperatura baja (0.4) fue clave para obtener respuestas consistentes y precisas sin caer en respuestas completamente deterministas.

**¿Qué ocurre al aumentar num_predict?**

Al aumentar `num_predict` las respuestas son más largas y detalladas, pero la latencia aumenta proporcionalmente. Con valores altos como 500 o 1000, el tiempo de respuesta puede superar los 2 minutos en hardware sin GPU.

**¿Qué ocurre al modificar temperature?**

Con `temperature=0.0` las respuestas son completamente deterministas — siempre la misma respuesta al mismo prompt. Con valores altos como `1.1` las respuestas son más creativas pero pueden perder coherencia o inventar datos. Para aplicaciones de asistente de alacena, `temperature=0.4` ofrece el mejor equilibrio entre consistencia y variedad.

**¿Por qué es útil mostrar tokens y latencia?**

Las métricas permiten entender el costo computacional de cada respuesta. En un sistema como la alacena inteligente donde el usuario espera una respuesta por WhatsApp, conocer la latencia ayuda a decidir qué modelo usar en producción. Un modelo que tarda 45 segundos puede ser inaceptable para el usuario final, mientras que uno de 25 segundos puede ser tolerable.

**¿Por qué se recomienda usar backend en vez de conectar el navegador directamente a Ollama?**

El backend permite validar parámetros antes de enviarlos a Ollama, manejar errores de forma controlada, agregar autenticación, registrar métricas en base de datos, y extender la funcionalidad con otros servicios como el inventario y WhatsApp. Si el frontend se conectara directamente a Ollama, cualquier usuario podría enviar parámetros sin restricción y acceder al modelo sin control.

**¿Cómo extenderías este chatbot para tu proyecto?**

El chatbot ya está extendido en el proyecto de alacena inteligente. El siguiente paso es conectar el módulo de visión artificial (Teachable Machine) para que el inventario se actualice automáticamente cuando la cámara detecte nuevos productos, eliminando la necesidad de que el usuario los reporte manualmente por WhatsApp.

---

## Referencias

- Ollama. (s. f.). *Chat API*. [https://docs.ollama.com/api/chat](https://docs.ollama.com/api/chat)
- Ollama. (s. f.). *Usage*. [https://docs.ollama.com/api/usage](https://docs.ollama.com/api/usage)
- FastAPI. (s. f.). *CORS*. [https://fastapi.tiangolo.com/tutorial/cors/](https://fastapi.tiangolo.com/tutorial/cors/)
- FastAPI. (s. f.). *Request body*. [https://fastapi.tiangolo.com/tutorial/body/](https://fastapi.tiangolo.com/tutorial/body/)
- MDN Web Docs. (s. f.). *Fetch API*. [https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- Qwen / Alibaba. *Qwen2.5-7B-Instruct*. [https://huggingface.co/Qwen/Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
