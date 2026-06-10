---
layout: default
title: Práctica 4 — Copilotos especializados con Ollama
nav_order: 6
---

# Práctica 4 — Ingeniería de prompting y copilotos especializados con Ollama

## Objetivo

Modificar el chatbot local de la Práctica 3 para convertirlo en un sistema de copilotos especializados mediante perfiles de system prompt, prompting estructurado, parámetros configurables y evaluación crítica de respuestas. Los perfiles fueron diseñados específicamente para el proyecto de **Alacena Inteligente**.

---

## 1. Del chatbot genérico al copiloto especializado

En la Práctica 3 se construyó un chatbot que respondía como asistente general. En esta práctica, el mismo modelo actúa como un copiloto especializado según el perfil seleccionado. La diferencia puede resumirse así:

```
Chatbot genérico =
Modelo + pregunta del usuario

Copiloto especializado =
Modelo + identidad + rol + contexto + instrucciones + límites + formato + pregunta del usuario
```

El cambio técnico principal consiste en controlar explícitamente el contenido del mensaje `system` dentro del endpoint `/api/chat` de Ollama, a través del campo `system_prompt` enviado desde el frontend.

---

## 2. Arquitectura actualizada

```
Usuario (navegador)
       ↓
Frontend — index.html + styles.css + app.js (puerto 5500)
       ↓  perfil + system_prompt + mensaje + parámetros
Backend — FastAPI (puerto 8000)
       ↓  messages[{role:system},{role:user}]
Ollama API local (puerto 11434)
       ↓
Modelo LLM — qwen2.5:7b
```

---

## 3. Perfiles de copiloto implementados

Se implementaron 4 perfiles adaptados al proyecto de alacena inteligente:

### Perfil 1 — Asistente genérico

| Elemento | Descripción |
|---|---|
| Identidad | Asistente general de alacena |
| Rol | Responde preguntas generales sobre inventario, recetas y compras |
| Audiencia | Usuario del hogar |
| Formato | Respuesta libre, amigable |
| Límites | Si falta información, pregunta antes de asumir |

```
Eres un asistente de alacena inteligente. Respondes preguntas generales sobre
el inventario, recetas y compras. Usa lenguaje claro y amigable.
Si no tienes información suficiente, pregunta antes de asumir.
```

---

### Perfil 2 — Administrador de alacena

| Elemento | Descripción |
|---|---|
| Identidad | Administrador del inventario |
| Rol | Gestiona productos, reporta existencias y advierte sobre agotamiento |
| Audiencia | Responsable de la alacena |
| Formato | Organizado por categorías, preciso |
| Límites | No inventa cantidades ni productos; pregunta si falta información |

```
Eres el administrador de una alacena inteligente. Tu rol es gestionar el
inventario de productos: agregar, consultar y reportar existencias.
Cuando el usuario reporte productos nuevos, confirma qué se agregó.
Cuando consulte el inventario, preséntalo organizado por categorías.
Advierte cuando un producto esté por agotarse (cantidad menor a 2).
Responde de forma precisa, sin inventar cantidades ni productos.
Si falta información sobre un producto, pregunta antes de registrarlo.
```

---

### Perfil 3 — Nutriólogo virtual

| Elemento | Descripción |
|---|---|
| Identidad | Nutriólogo virtual especializado |
| Rol | Analiza el inventario y sugiere recetas balanceadas |
| Audiencia | Usuario interesado en alimentación saludable |
| Formato | Recetas con valor nutricional explicado |
| Límites | No diagnostica enfermedades ni sustituye consulta médica |

```
Eres un nutriólogo virtual especializado en alimentación saludable.
Tu rol es analizar el inventario de la alacena del usuario y sugerir
recetas balanceadas, combinaciones nutritivas y hábitos alimenticios saludables.
Considera macronutrientes, vitaminas y balance calórico en tus sugerencias.
Siempre explica brevemente el valor nutricional de los ingredientes que uses.
No diagnostiques enfermedades ni sustituyas consulta médica.
Si el inventario tiene pocos ingredientes, sugiere qué comprar para mejorar
el balance nutricional. Responde en español con tono profesional pero accesible.
```

---

### Perfil 4 — Asistente de compras

| Elemento | Descripción |
|---|---|
| Identidad | Asistente de compras inteligente |
| Rol | Genera listas de compras organizadas y económicas |
| Audiencia | Familia que planea sus compras semanales |
| Formato | Lista organizada por categorías con cantidades |
| Límites | Ajusta cantidades si el usuario indica diferente |

```
Eres un asistente de compras inteligente para una alacena familiar.
Tu rol es generar listas de compras organizadas, prácticas y económicas.
Cuando el usuario comparta su inventario actual, analiza qué falta para
una semana completa de comidas. Organiza la lista por categorías:
frutas y verduras, proteínas, lácteos, abarrotes, otros.
Estima cantidades para una familia de 4 personas por defecto,
pero ajusta si el usuario indica diferente.
Responde en español de forma clara y estructurada.
```

---

## 4. Cambios técnicos

### 4.1 Backend — nuevos endpoints

Se agregaron dos endpoints al `main.py`:

```
GET  /profiles    ← devuelve los perfiles disponibles con su system_prompt
POST /chat/admin  ← recibe perfil, system_prompt editable y parámetros
```

El endpoint `/chat/admin` construye el payload para Ollama con el system prompt del perfil seleccionado (o uno editado por el usuario) y devuelve la respuesta junto con métricas.

**Evidencia — endpoint /profiles:**

<!-- Insertar captura de http://localhost:8000/profiles -->
![Endpoint profiles](assets/img/practica4/profiles-endpoint.png)

**Evidencia — backend corriendo:**

<!-- Insertar captura de la terminal con Application startup complete -->
![Backend corriendo](assets/img/practica4/backend.png)

### 4.2 Frontend — 3 archivos separados

La interfaz se dividió en tres archivos:

| Archivo | Función |
|---|---|
| `index.html` | Estructura visual: selector de perfil, sliders, chat y métricas |
| `styles.css` | Estilos: paleta verde/oscuro, burbujas de chat, métricas |
| `app.js` | Lógica: carga perfiles desde `/profiles`, envía mensajes, renderiza métricas |

El flujo de `app.js`:
1. Al cargar, hace `GET /profiles` y llena el textarea de system prompt
2. Al cambiar perfil, actualiza el system prompt automáticamente
3. Al enviar, manda `POST /chat/admin` con mensaje + perfil + parámetros
4. Muestra la respuesta y actualiza las 8 métricas

**Evidencia — frontend con perfil Administrador:**

<!-- Insertar captura del frontend con el perfil administrador seleccionado -->
![Frontend perfil administrador](assets/img/practica4/frontend-admin.png)

**Evidencia — frontend con perfil Nutriólogo:**

<!-- Insertar captura del frontend con el perfil nutriólogo seleccionado -->
![Frontend perfil nutriólogo](assets/img/practica4/frontend-nutriologo.png)

**Evidencia — frontend con perfil Comprador:**

<!-- Insertar captura del frontend con el perfil comprador seleccionado -->
![Frontend perfil comprador](assets/img/practica4/frontend-comprador.png)

---

## 5. Tabla de pruebas

| Perfil | Prompt | ¿Cumple rol? | ¿Cumple formato? | ¿Alucina? | Tokens salida | Latencia | Observación |
|---|---|---|---|---|---|---|---|
| Genérico | "¿Qué puedo cocinar con lo que tengo?" | | | | | | |
| Genérico | "¿Qué me falta comprar esta semana?" | | | | | | |
| Genérico | "¿Es saludable lo que tengo en la alacena?" | | | | | | |
| Administrador | "Agrega 3 tomates y 2 aguacates al inventario" | | | | | | |
| Administrador | "¿Qué productos están por agotarse?" | | | | | | |
| Administrador | "Muéstrame el inventario organizado por categorías" | | | | | | |
| Nutriólogo | "¿Qué receta balanceada puedo hacer con pollo, brócoli y arroz?" | | | | | | |
| Nutriólogo | "¿Mi inventario tiene buena variedad nutricional?" | | | | | | |
| Nutriólogo | "Dame una cena alta en proteína con lo que tengo" | | | | | | |
| Comprador | "Hazme la lista del super para esta semana" | | | | | | |
| Comprador | "¿Qué me falta para hacer desayunos completos?" | | | | | | |
| Comprador | "Lista económica para 4 personas por 7 días" | | | | | | |

**Evidencia — prueba con perfil Genérico:**

<!-- Insertar captura de una conversación con el perfil genérico -->
![Prueba genérico](assets/img/practica4/prueba-generico.png)

**Evidencia — prueba con perfil Nutriólogo:**

<!-- Insertar captura de una conversación con el perfil nutriólogo -->
![Prueba nutriólogo](assets/img/practica4/prueba-nutriologo.png)

**Evidencia — prueba con perfil Comprador:**

<!-- Insertar captura de una conversación con el perfil comprador -->
![Prueba comprador](assets/img/practica4/prueba-comprador.png)

**Evidencia — métricas visibles:**

<!-- Insertar captura del panel de métricas con datos reales -->
![Métricas](assets/img/practica4/metricas.png)

---

## 6. Comparación genérico vs especializado

| Criterio | Asistente genérico | Copiloto especializado |
|---|---|---|
| Claridad | | |
| Uso de ejemplos | | |
| Nivel adecuado | | |
| Advertencias técnicas | | |
| Formato de respuesta | | |
| Utilidad para el proyecto | | |

---

## 7. Reflexión técnica

**¿Qué perfil fue más útil para el proyecto de alacena inteligente?**

<!-- Escribir respuesta aquí -->

**¿Qué diferencias observaste entre el asistente genérico y los perfiles especializados?**

<!-- Escribir respuesta aquí -->

**¿Qué instrucciones del system prompt redujeron la ambigüedad en las respuestas?**

<!-- Escribir respuesta aquí -->

**¿Qué instrucciones hicieron la respuesta demasiado rígida o limitada?**

<!-- Escribir respuesta aquí -->

**¿El modelo inventó información en algún caso? ¿En cuál?**

<!-- Escribir respuesta aquí -->

**¿Qué guardrails agregarías para mejorar la confiabilidad del copiloto?**

<!-- Escribir respuesta aquí -->

**¿Cómo conectarías este copiloto con los documentos de inventario en un sistema RAG?**

<!-- Escribir respuesta aquí -->

---

## Referencias

- Ollama. (s. f.). *Chat API*. [https://docs.ollama.com/api/chat](https://docs.ollama.com/api/chat)
- FastAPI. (s. f.). *Request body*. [https://fastapi.tiangolo.com/tutorial/body/](https://fastapi.tiangolo.com/tutorial/body/)
- OpenAI. (s. f.). *Prompt engineering*. [https://developers.openai.com/api/docs/guides/prompt-engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
- Google AI for Developers. (2026). *Prompt design strategies*. [https://ai.google.dev/gemini-api/docs/prompting-strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- OWASP. (2025). *LLM01:2025 Prompt Injection*. [https://genai.owasp.org/llmrisk/llm01-prompt-injection/](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- Qwen / Alibaba. *Qwen2.5-7B-Instruct*. [https://huggingface.co/Qwen/Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)