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
![Endpoint profiles](/workspaces/ProspectivaTecnologica/assets/img/p4/activarFrontend.jpeg)

**Evidencia — backend corriendo:**

<!-- Insertar captura de la terminal con Application startup complete -->
![Backend corriendo](/workspaces/ProspectivaTecnologica/assets/img/p4/activarBackend.jpeg)

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
![Frontend perfil administrador](/workspaces/ProspectivaTecnologica/assets/img/p4/Agente_admin.jpeg)

**Evidencia — frontend con perfil Nutriólogo:**

<!-- Insertar captura del frontend con el perfil nutriólogo seleccionado -->
![Frontend perfil nutriólogo](/workspaces/ProspectivaTecnologica/assets/img/p4/agente_nutriologo.jpeg)

**Evidencia — frontend con perfil Comprador:**

<!-- Insertar captura del frontend con el perfil comprador seleccionado -->
![Frontend perfil comprador](/workspaces/ProspectivaTecnologica/assets/img/p4/agente_compras.jpeg)

---

## 5. Tabla de pruebas

| Perfil | Prompt | ¿Cumple rol? | ¿Cumple formato? | ¿Alucina? | Tokens salida | Latencia | Observación |
|---|---|---|---|---|---|---|---|
| Genérico | "¿Qué puedo cocinar con lo que tengo?" | Parcial — pidió el inventario primero | No aplica | No | 63 | 27.90 s | Respondió pidiendo más info, sin orientación adicional |
| Administrador | "Muéstrame el inventario organizado por categorías" | Sí — solicitó categorías y productos | Lista organizada | No | 56 | 18.65 s | Comportamiento correcto; pide datos antes de asumir |
| Nutriólogo | "Dame una receta balanceada con lo que tengo" | Sí — sugirió ingredientes básicos | Sugerencias + valor nutricional | Leve | 82 | 39.17 s | Sugirió arroz, frijoles, leche sin conocer el inventario real |
| Comprador | "Hazme la lista del super para esta semana" | Sí — generó lista por categorías | Lista organizada por categorías | Leve | 180 | 56.53 s | Generó productos sin conocer inventario real; lista genérica pero útil |

**Evidencia — prueba con perfil Genérico:**

<!-- Insertar captura de una conversación con el perfil genérico -->
![Prueba genérico](/workspaces/ProspectivaTecnologica/assets/img/p4/IA_GENERICA.jpeg)

**Evidencia — prueba con perfil Nutriólogo:**

<!-- Insertar captura de una conversación con el perfil nutriólogo -->
![Prueba nutriólogo](/workspaces/ProspectivaTecnologica/assets/img/p4/agente_nutriologo.jpeg)

**Evidencia — prueba con perfil Comprador:**

<!-- Insertar captura de una conversación con el perfil comprador -->
![Prueba comprador](/workspaces/ProspectivaTecnologica/assets/img/p4/agente_compras.jpeg)


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

El perfil de **Asistente de compras** resultó el más útil para el proyecto. Al preguntar "Hazme la lista del super para esta semana", el copiloto generó una lista organizada por categorías (frutas y verduras, proteínas, lácteos, abarrotes) sin que se le proporcionara el inventario completo. Esto demuestra que un system prompt bien definido puede guiar al modelo hacia respuestas estructuradas y accionables, directamente aplicables al flujo de la alacena inteligente.

**¿Qué diferencias observaste entre el asistente genérico y los perfiles especializados?**

El asistente genérico respondió la pregunta "¿Qué puedo cocinar con lo que tengo?" pidiendo primero que el usuario compartiera su inventario, sin ofrecer ninguna orientación adicional. Los perfiles especializados, en cambio, mostraron comportamientos más definidos: el Administrador solicitó las categorías del inventario de forma estructurada; el Nutriólogo sugirió ingredientes básicos como referencia mientras esperaba más información; y el Comprador generó directamente una lista genérica organizada por categorías para una familia de 4 personas. La diferencia principal no fue la calidad del modelo sino la dirección que le da el system prompt.

**¿Qué instrucciones del system prompt redujeron la ambigüedad en las respuestas?**

Las instrucciones más efectivas fueron las que definían el formato de salida de forma explícita. En el perfil Comprador, la instrucción "Organiza la lista de compras por categorías: frutas y verduras, proteínas, lácteos, abarrotes, otros" produjo directamente una respuesta estructurada con encabezados y listas. También fue efectiva la instrucción "Estima cantidades para una familia de 4 personas por defecto", que evitó que el modelo pidiera ese dato antes de responder.

**¿Qué instrucciones hicieron la respuesta demasiado rígida o limitada?**

En el perfil Administrador, la instrucción "No inventes cantidades ni productos; pregunta si falta información" hizo que el modelo solicitara el inventario antes de dar cualquier respuesta, lo cual es correcto funcionalmente pero puede percibirse como poco fluido para el usuario. De forma similar, el Nutriólogo pidió la lista de ingredientes antes de sugerir recetas, lo que alarga el intercambio. En un sistema real, esto se resolvería conectando el copiloto directamente con el inventario de la BD en lugar de depender del usuario para proporcionarlo.

**¿El modelo inventó información en algún caso? ¿En cuál?**

En el perfil Comprador, el modelo generó una lista de compras con productos específicos (manzanas, naranjas, papas, zanahorias, pollo, carne de res, cerdo, lácteos) sin conocer el inventario real. Aunque la lista tiene sentido para una familia promedio, los productos y cantidades son inferidos, no basados en datos reales de la alacena. Esto es una alucinación leve — el modelo no inventó datos dañinos, pero presentó suposiciones como si fueran recomendaciones personalizadas.

**¿Qué guardrails agregarías para mejorar la confiabilidad del copiloto?**

Se agregarían tres guardrails principales: primero, validación en el backend que rechace mensajes que intenten modificar el system prompt mediante inyección de prompt (por ejemplo, "ignora tus instrucciones anteriores"). Segundo, un límite de longitud en el system_prompt editable del frontend para evitar instrucciones excesivamente largas que confundan al modelo. Tercero, conectar automáticamente el inventario real desde `/inventory/db` al inicio de cada conversación, para que el copiloto no dependa del usuario para conocer el estado de la alacena.

**¿Cómo conectarías este copiloto con los documentos de inventario en un sistema RAG?**

En un sistema RAG, el backend consultaría `/inventory/db` antes de llamar a Ollama y agregaría el inventario actual como contexto dentro del system prompt. Por ejemplo: "Inventario actual: pollo (2), leche (1), huevos (6), pasta (3)...". Esto eliminaría la necesidad de que el usuario escriba manualmente los ingredientes en cada conversación. En una versión más avanzada, se podría incluir también el historial de compras, las preferencias dietéticas del usuario y recetas anteriores como documentos de contexto, convirtiendo el copiloto en un asistente verdaderamente personalizado.

---

## Referencias

- Ollama. (s. f.). *Chat API*. [https://docs.ollama.com/api/chat](https://docs.ollama.com/api/chat)
- FastAPI. (s. f.). *Request body*. [https://fastapi.tiangolo.com/tutorial/body/](https://fastapi.tiangolo.com/tutorial/body/)
- OpenAI. (s. f.). *Prompt engineering*. [https://developers.openai.com/api/docs/guides/prompt-engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
- Google AI for Developers. (2026). *Prompt design strategies*. [https://ai.google.dev/gemini-api/docs/prompting-strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- OWASP. (2025). *LLM01:2025 Prompt Injection*. [https://genai.owasp.org/llmrisk/llm01-prompt-injection/](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- Qwen / Alibaba. *Qwen2.5-7B-Instruct*. [https://huggingface.co/Qwen/Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)