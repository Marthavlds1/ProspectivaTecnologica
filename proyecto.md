---
layout: default
title: Portafolio — Alacena Inteligente 
nav_order: 10
---
# Alacena Inteligente

**A Multi-Agent Architecture Based on Vision and Language Models for Intelligent Food Inventory Management**

Proyecto final — Prospectiva de IA — Ingenieria Mecatronica y Sistemas Ciberfisicos
Universidad Iberoamericana Ciudad de Mexico — 2026

 Martha Valdes · Renata Badillo · Marco Calixto

---

## Indice

1. [Resumen del proyecto](#1-resumen-del-proyecto)
2. [Problema que resuelve](#2-problema-que-resuelve)
3. [Arquitectura del sistema](#3-arquitectura-del-sistema)
4. [Etapa 1 — Hardware y percepcion visual](#4-etapa-1--hardware-y-percepcion-visual)
5. [Etapa 2 — Backend y base de datos](#5-etapa-2--backend-y-base-de-datos)
6. [Etapa 3 — Orquestador LLM](#6-etapa-3--orquestador-llm)
7. [Etapa 4 — Agentes especializados](#7-etapa-4--agentes-especializados)
8. [Etapa 5 — Integracion con WhatsApp](#8-etapa-5--integracion-con-whatsapp)
9. [Etapa 6 — Dashboard de observabilidad](#9-etapa-6--dashboard-de-observabilidad)
10. [Prueba final del sistema completo](#10-prueba-final-del-sistema-completo)
11. [Resultados y metricas](#11-resultados-y-metricas)
12. [Stack tecnologico](#12-stack-tecnologico)
13. [Instalacion](#13-instalacion)
14. [Descargas](#14-descargas)
15. [Estructura del proyecto](#15-estructura-del-proyecto)

---

## 1. Descripción General

Alacena Inteligente es un sistema multi-agente para la gestion automatizada de inventario alimentario domestico. El sistema detecta productos en una despensa mediante una camara ESP32-CAM, los registra en una base de datos, y permite al usuario consultar su inventario, generar recetas, obtener listas de compras, calcular su perfil nutricional y recibir planes de alimentacion — todo mediante lenguaje natural a traves de WhatsApp.

A diferencia de los asistentes conversacionales convencionales, donde un unico modelo de lenguaje es responsable de interpretar solicitudes y generar respuestas, la arquitectura propuesta distribuye las responsabilidades entre agentes especializados coordinados por una capa de orquestacion. Un modelo de lenguaje visual (VLM) detecta productos alimenticios mediante imagenes capturadas por una camara ESP32-CAM. Un LLM opera exclusivamente como agente orquestador que interpreta solicitudes en lenguaje natural, extrae entidades estructuradas y delega la ejecucion a agentes de dominio especializados.

La arquitectura incorpora ademas una capa de observabilidad que registra latencia, consumo de tokens, velocidad de inferencia, precision de clasificacion de intenciones, validacion de salidas estructuradas y trazas de ejecucion a traves de un dashboard administrativo.

### Funcionalidades principales

| Funcionalidad | Descripcion |
|---|---|
| Deteccion visual | ESP32-CAM captura la alacena y Gemini Vision identifica productos |
| Inventario automatico | Los productos detectados se agregan o actualizan en SQLite |
| Orquestacion LLM | llama3.2:3b interpreta intenciones y genera JSON estructurado |
| Agentes especializados | Inventario, recetas, nutricion, compras y plan semanal |
| WhatsApp | Interfaz conversacional via whatsapp-web.js |
| Observabilidad | Dashboard con metricas en tiempo real de toda la arquitectura |

El articulo tecnico completo del proyecto esta disponible en la seccion de [Descargas](#14-descargas).


---

## 2. Problema que resuelve

La gestion del inventario alimentario en el hogar tiene un costo real: alimentos que se vencen sin ser consumidos, compras repetidas de lo que ya existe, y falta de visibilidad sobre lo disponible al momento de cocinar o planear comidas.

Las soluciones actuales — aplicaciones de registro manual, codigos de barras, hojas de calculo — requieren intervencion activa y constante del usuario, lo que limita su adopcion.

Este proyecto propone una alternativa donde la alacena se actualiza sola mediante vision por computadora, y el usuario puede interactuar con ella en lenguaje natural desde la aplicacion de mensajeria que ya usa todos los dias.

Objetivos - Desarrollar un asistente nutrimental inteligente que permita:

Gestionar inventario de alimentos.
Generar recetas personalizadas.
Crear listas de compras.
Generar planes alimenticios.
Interactuar mediante WhatsApp.
Utilizar modelos de lenguaje (LLM) ejecutados localmente.
Reconocer productos automáticamente mediante visión computacional (VLM)
Automatizar la gestión de una alacena doméstica.

---

## 3. Arquitectura del sistema

El sistema sigue una arquitectura de cinco capas independientes y coordinadas:

```
+----------------------------------------------------------+
|                    CAPA DE PERCEPCION                    |
|                                                          |
|   ESP32-CAM (OV2640)                                     |
|   Captura imagen --> POST /vision/upload                 |
+------------------------+---------------------------------+
                         |
                         v
+----------------------------------------------------------+
|                CAPA DE ORQUESTACION                      |
|                                                          |
|   LLM Orchestrator (llama3.2:3b via Ollama)              |
|   Comprension de lenguaje natural                        |
|   Clasificacion de intenciones                           |
|   Extraccion de entidades --> JSON estructurado          |
+------------------------+---------------------------------+
                         |
                         v
+----------------------------------------------------------+
|            CAPA DE EJECUCION (AGENTES)                   |
|                                                          |
|   Inventory Agent  |  Recipe Agent  |  Nutrition Agent   |
|   Shopping Agent   |  Meal Planner                       |
+------------------------+---------------------------------+
                         |
                         v
+----------------------------------------------------------+
|                 CAPA DE PERSISTENCIA                     |
|                                                          |
|   SQLite: inventory | users | llm_metrics                |
|           chat_history | intent_tests                    |
+----------------------------------------------------------+
                         |
                         v
+----------------------------------------------------------+
|                CAPA DE OBSERVABILIDAD                    |
|                                                          |
|   Dashboard web (HTML/CSS/JS)                            |
|   Metricas en tiempo real via REST APIs                  |
+----------------------------------------------------------+
```

El usuario accede al sistema a traves de dos interfaces: WhatsApp para conversacion cotidiana, y el dashboard administrativo para monitoreo y evaluacion tecnica.

---

## 4. Etapa 1 — Hardware y percepcion visual

### Que se hizo

Se integro una camara ESP32-CAM con sensor OV2640 al sistema. La camara se conecta a la red Wi-Fi local y expone un endpoint HTTP en la direccion `http://192.168.100.204/capture`. Cuando el sistema necesita actualizar el inventario, el backend envia una solicitud POST a ese endpoint, la camara toma la foto y la envia de regreso. La imagen se guarda como `backend/images/latest.jpg`.

Para la deteccion de productos se uso Gemini 2.5 Flash Vision mediante la API de Google. El reto principal fue que la resolucion de la ESP32-CAM es baja y las condiciones de iluminacion de una alacena no son ideales. Para compensar esto, en lugar de pedir al modelo que identifique cualquier objeto en la imagen, se le proporciono un catalogo cerrado de 26 productos con sus descripciones visuales especificas: color del empaque, forma del envase, texto visible en la etiqueta y logotipo. Este enfoque actua como un refuerzo contextual que mejora significativamente la precision de deteccion bajo condiciones de imagen no perfectas.

El sistema solo acepta detecciones con nivel de confianza mayor o igual a 0.5. Si el modelo no puede identificar un producto con esa certeza, lo omite en lugar de asumir.

### Catalogo de productos

| Producto | Descripcion visual proporcionada al modelo |
|---|---|
| Refresco Ameyal | Botella color rosa |
| Paquete Gelatina Dany | Dos vasos morados |
| Jugo de Mango Jumex | Caja azul con mango amarillo |
| Cereal Trix | Caja predominantemente roja, logo Trix en verde |
| Carton Nutri Leche | Caja blanca con logo de letras blancas |
| Carton LALA leche | Caja blanca con logo azul y franja roja bajo el logo |
| Aceite Nutrioli | Botella dorada con etiqueta y tapa verdes |
| Botella Bonafont | Botella de agua transparente |
| Chocolate Larin | Barra de color verde |
| Mantequilla Primavera | Barra de color amarillo |
| ChocoMilk | Lata cilindrica de color azul |
| Paquete Espagueti | Paquete transparente con logo amarillo-negro, se ve el espagueti crudo |
| Jugo de fresa Boing | Lata roja con letras verdes |
| Papas Pringles | Lata roja con logo blanco |
| Jugo de mango del Valle | Lata amarilla con logo negro-blanco |
| Salsa de tomate | Lata negra con logo rojo |
| Mayonesa McCormick | Frasco blanco con etiqueta y tapa rojas |
| Sal La Fina | Frasco blanco con etiqueta azul-rojo y tapa amarilla |
| Jugo FuseTea | Lata amarilla con letras negras |
| Jugo pera Jumex | Lata azul con logo verde-rojo |
| Bebida Energetica Red Bull | Lata azul-gris con logo rojo-amarillo |
| Refresco CocaCola | Botella negra con etiqueta roja |
| Cereal Nesquik | Caja amarilla con logo cafe y azul |
| Cereal ChocoKrispis | Caja cafe con letras amarillas |
| Refresco Fanta | Lata naranja con logo de letras verdes |

### Capturas — Hardware y deteccion visual

---

**Captura 1 — Modulo ESP32-CAM fisico**

<!-- ![ESP32-CAM modulo fisico](./assets/esp32cam_hardware.jpg) -->

> Fotografia del modulo ESP32-CAM con sensor OV2640 utilizado en el proyecto. El modulo se coloco apuntando hacia el interior de la alacena y conectado a la red Wi-Fi local para comunicarse con el backend mediante HTTP.

---

**Captura 2 — Alacena con los productos del catalogo**

<!-- ![Alacena con productos](./assets/alacena_productos.jpg) -->

> Vista de la alacena fisica utilizada para las pruebas, con los 26 productos del catalogo dispuestos de manera visible. Esta es la escena que la ESP32-CAM captura para que Gemini Vision realice la deteccion.

---

**Captura 3 — Imagen capturada por la ESP32-CAM**

<!-- ![Imagen latest.jpg capturada por ESP32-CAM](./assets/latest_captura.jpg) -->

> Imagen real tomada por la ESP32-CAM y guardada como `latest.jpg` en el servidor. Se puede observar la diferencia de resolucion respecto a una camara convencional, lo que justifica el uso de descripciones visuales especificas en el prompt de Gemini.

---

**Captura 4 — Resultado JSON de Gemini Vision**

<!-- ![Respuesta JSON de Gemini Vision](./assets/gemini_json_resultado.png) -->

> Salida del endpoint `/vision/detect` mostrando el JSON generado por Gemini Vision con los productos detectados, sus niveles de confianza y cantidades. Solo los productos con confianza mayor o igual a 0.5 se insertan en el inventario.

---

## 5. Etapa 2 — Backend y base de datos

### Que se hizo

El backend se implemento con FastAPI. Actua como la capa central de coordinacion: recibe solicitudes desde WhatsApp y el dashboard, invoca al orquestador, valida el JSON generado, delega la ejecucion al agente correspondiente, registra metricas operacionales y devuelve la respuesta al usuario.

La base de datos usa SQLite con cinco tablas independientes, cada una con una responsabilidad clara. La decision de usar SQLite responde a simplicidad de despliegue, mantenimiento minimo y suficiencia para el volumen de datos esperado en un hogar.

Una decision de diseno importante fue la logica upsert en el inventario: cuando la camara detecta un producto que ya existe en la base de datos, su cantidad se incrementa en lugar de crear un registro duplicado.

### Esquema de base de datos

```sql
-- Inventario de productos
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    quantity INTEGER NOT NULL,
    source TEXT,           -- 'vision', 'api', 'manual', 'seed'
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Perfil nutricional del usuario
CREATE TABLE users (
    usuario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp_number TEXT UNIQUE,
    nombre TEXT,
    edad INTEGER,
    sexo TEXT,
    peso REAL,
    altura REAL,
    activity_level TEXT,   -- sedentary, light, moderate, active, very_active
    objetivo TEXT,         -- muscle_gain, weight_loss, maintenance, recomposition
    dietary_restrictions TEXT,
    food_preferences TEXT,
    budget REAL,
    ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Metricas de cada llamada al LLM
CREATE TABLE llm_metrics (
    model TEXT,
    provider TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    latency_seconds REAL,
    tokens_per_second REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Historial completo de conversaciones con metricas del orquestador
CREATE TABLE chat_history (
    numero TEXT,
    mensaje TEXT,
    respuesta TEXT,
    intent TEXT,
    latency_seconds REAL,
    success INTEGER,
    orchestrator_intent TEXT,
    orchestrator_confidence REAL,
    orchestrator_json_valid INTEGER,
    orchestrator_schema_valid INTEGER,
    orchestrator_tokens INTEGER,
    orchestrator_model TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dataset de pruebas controladas de clasificacion de intenciones
CREATE TABLE intent_tests (
    message TEXT,
    expected_intent TEXT,
    detected_intent TEXT,
    response TEXT,
    latency_seconds REAL,
    is_correct INTEGER,
    has_response INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Capturas — Backend y base de datos

---

**Captura 5 — Documentacion automatica de la API (Swagger UI)**

<!-- ![Swagger UI FastAPI](./assets/swagger_ui.png) -->

> Vista del endpoint interactivo generado automaticamente por FastAPI en `http://localhost:8000/docs`. Muestra todos los endpoints disponibles del sistema organizados por router: inventario, chat, vision, metricas y orquestador.

---

**Captura 6 — Inventario actualizado en la base de datos**

<!-- ![Inventario en SQLite](./assets/inventario_sqlite.png) -->

> Vista de la tabla `inventory` en SQLite despues de una deteccion visual. Se pueden ver los productos detectados por Gemini Vision con su nombre normalizado, cantidad, fuente de origen (`vision`) y la marca de tiempo de la ultima actualizacion.

---

## 6. Etapa 3 — Orquestador LLM

### Que se hizo

El orquestador es el componente que diferencia esta arquitectura de un chatbot convencional. En lugar de que el LLM responda directamente al usuario y manipule la base de datos, opera exclusivamente como un clasificador de intenciones y extractor de entidades. Su unica salida es un JSON estructurado que el backend valida antes de delegar la ejecucion al agente correspondiente.

Para cada mensaje del usuario, el orquestador ejecuta la siguiente secuencia internamente:

1. Comprension del lenguaje natural
2. Clasificacion de la intencion del usuario
3. Extraccion de entidades (productos, cantidades, nombres)
4. Estimacion de nivel de confianza
5. Generacion del JSON estructurado
6. El backend valida el esquema
7. Seleccion y ejecucion del agente

Si la validacion del esquema falla, el backend activa un fallback basado en reglas de palabras clave para mantener la disponibilidad del sistema.

### Intenciones soportadas

| Intencion | Ejemplos de frases que la activan |
|---|---|
| `inventory` | "que tengo", "que hay en mi alacena", "mis productos", "que comida tengo" |
| `add_inventory` | "compre leche", "agregue 2 jugos", "tengo ahora cereal" |
| `remove_inventory` | "me comi las papas", "ya no tengo cereal", "use el aceite" |
| `rename_inventory` | "cambia leche por LALA", "quise decir Bonafont" |
| `recipe` | "que puedo cocinar hoy", "dame una receta con lo que tengo" |
| `shopping` | "que me falta comprar", "genera mi lista del super" |
| `meal_plan` | "hazme un plan semanal", "dieta para la semana" |
| `nutrition` | "cuantas calorias necesito", "calcula mi TMB y GET" |
| `reminders` | "que se va a echar a perder", "que debo consumir pronto" |
| `profile_register` | "registrar perfil" |
| `general` | cualquier mensaje que no encaje en las anteriores |

### Ejemplo de salida del orquestador

```json
{
  "intent": "add_inventory",
  "action": "add_food",
  "confidence": 0.95,
  "entities": {
    "items": [
      {
        "name": "mangos",
        "quantity": 2
      }
    ],
    "old_name": null,
    "new_name": null
  },
  "needs_profile": false,
  "reason": "El usuario indica que compro productos para agregar al inventario."
}
```

### Capturas — Orquestador LLM

---

**Captura 7 — Respuesta del orquestador en el dashboard**

<!-- ![Orquestador JSON en dashboard](./assets/orquestador_json.png) -->

> Vista del dashboard mostrando el JSON estructurado generado por el orquestador para un mensaje de usuario. Se puede ver la intencion detectada, las entidades extraidas (producto y cantidad), el nivel de confianza y el razonamiento del modelo. Esta informacion se registra en `chat_history` para analisis posterior.

---

**Captura 8 — Tasa de validacion de esquema JSON**

<!-- ![Validacion JSON orquestador](./assets/validacion_json.png) -->

> Panel del dashboard mostrando la tasa de JSON valido y la tasa de validacion de esquema del orquestador durante las pruebas. Ambas metricas alcanzaron 100% en los experimentos controlados, indicando que el modelo produce salidas estructuradas compatibles con los agentes de forma consistente.

---

## 7. Etapa 4 — Agentes especializados

### Que se hizo

Se implementaron cinco agentes de software independientes. Cada agente tiene una responsabilidad unica, recibe entidades estructuradas del orquestador y nunca procesa lenguaje natural directamente. Esto mantiene la logica de negocio determinista e independiente de la implementacion del modelo de lenguaje.

### Inventory Agent

Gestiona todas las operaciones sobre el inventario: consulta, insercion, actualizacion de cantidad, eliminacion y renombrado de productos. La separacion entre comprension del lenguaje (orquestador) y manipulacion del inventario (este agente) reduce la ambiguedad y simplifica el mantenimiento.

Ejemplo de flujo: el usuario dice "compre dos mangos" — el orquestador extrae `{name: "mangos", quantity: 2}` — el Inventory Agent ejecuta el upsert en SQLite.

### Recipe Agent

Genera recetas usando exclusivamente los ingredientes disponibles en el inventario. Prioriza los ingredientes existentes para reducir desperdicio y evitar compras innecesarias. Incorpora restricciones nutricionales del perfil del usuario cuando este ha sido registrado. El prompt del agente (NutriChefAI) exige un formato estructurado con nombre, resumen, ingredientes, preparacion paso a paso, informacion nutrimental estimada y consejos.

### Nutrition Agent

Calcula indicadores nutricionales personalizados usando la ecuacion de Mifflin-St Jeor:

- TMB (Tasa Metabolica Basal): calculo diferenciado por sexo, peso, altura y edad
- GET (Gasto Energetico Total): TMB multiplicado por factor de actividad
- Calorias objetivo: ajustadas segun el objetivo del usuario (perdida de peso, ganancia muscular, mantenimiento, recomposicion)
- Distribucion de macronutrientes

Los resultados de este agente son consumidos por el Recipe Agent y el Meal Planning Agent para personalizar sus recomendaciones.

### Shopping Agent

Analiza el inventario actual y genera recomendaciones de compra priorizadas en tres niveles: alta prioridad (agotados o alimentos basicos), media prioridad (stock bajo o mejora variedad nutricional) y baja prioridad (variedad no critica). El agente tambien detecta riesgos de desperdicio y oportunidades de mejora en el balance nutricional de la despensa.

### Meal Planning Agent

Genera planes de alimentacion semanales combinando tres fuentes de informacion: disponibilidad en el inventario, requisitos nutricionales del perfil del usuario y objetivo alimentario. Maximiza el uso de ingredientes existentes mientras mantiene la consistencia nutricional a lo largo de la semana.

### Capturas — Agentes especializados

---

**Captura 9 — Respuesta del Recipe Agent en WhatsApp**

<!-- ![Receta generada en WhatsApp](./assets/whatsapp_receta.jpg) -->

> Mensaje de WhatsApp mostrando una receta completa generada por el Recipe Agent (NutriChefAI) con los ingredientes disponibles en el inventario. La respuesta incluye nombre de la receta, resumen, ingredientes con cantidades, pasos de preparacion, informacion nutrimental estimada, tiempo y consejos.

---

**Captura 10 — Respuesta del Shopping Agent en WhatsApp**

<!-- ![Lista de compras en WhatsApp](./assets/whatsapp_compras.jpg) -->

> Mensaje de WhatsApp con la lista de compras generada por el Shopping Agent (SmartPantryAI). Muestra los productos organizados por prioridad de compra, con la justificacion de cada recomendacion y el impacto esperado en el balance nutricional de la despensa.

---

**Captura 11 — Respuesta del Nutrition Agent en WhatsApp**

<!-- ![Calculo nutricional en WhatsApp](./assets/whatsapp_nutricion.jpg) -->

> Mensaje de WhatsApp con el calculo del perfil nutricional personalizado del usuario: TMB, GET, calorias objetivo y distribucion de macronutrientes. Los valores se calculan con base en el perfil registrado (edad, peso, altura, nivel de actividad y objetivo alimentario).

---

**Captura 12 — Plan semanal generado por el Meal Planning Agent**

<!-- ![Plan semanal en WhatsApp](./assets/whatsapp_plan_semanal.jpg) -->

> Mensaje de WhatsApp con el plan de alimentacion semanal generado combinando el inventario disponible y el perfil nutricional del usuario. El plan distribuye comidas a lo largo de la semana priorizando ingredientes ya existentes en la alacena.

---

## 8. Etapa 5 — Integracion con WhatsApp

### Que se hizo

La interfaz de usuario principal se implemento mediante WhatsApp usando la libreria whatsapp-web.js. El servicio de WhatsApp normaliza los mensajes entrantes y los envia al backend FastAPI. El backend procesa la solicitud completa (orquestador, agente, base de datos) y devuelve la respuesta al usuario por el mismo canal.

La eleccion de WhatsApp como interfaz principal elimina la necesidad de desarrollar y mantener una aplicacion movil dedicada, y ofrece una experiencia de interaccion familiar para cualquier usuario.

Una consideracion tecnica importante: el procesamiento de mensajes comienza solo despues de que el cliente esta completamente inicializado, para evitar que mensajes historicos sean procesados multiples veces tras una reconexion.

### Capturas — Integracion con WhatsApp

---

**Captura 13 — Consulta de inventario por WhatsApp**

<!-- ![Consulta inventario WhatsApp](./assets/whatsapp_inventario.jpg) -->

> Conversacion de WhatsApp donde el usuario pregunta que tiene en su alacena. El sistema detecta la intencion `inventory`, consulta la tabla `inventory` en SQLite y responde con la lista de productos disponibles con sus cantidades.

---

**Captura 14 — Registro de producto por voz o texto natural**

<!-- ![Agregar producto WhatsApp](./assets/whatsapp_agregar.jpg) -->

> Conversacion donde el usuario dice en lenguaje natural que compro un producto. El orquestador detecta la intencion `add_inventory`, extrae el nombre y la cantidad, y el Inventory Agent actualiza la base de datos. El sistema confirma la operacion al usuario.

---

**Captura 15 — Alerta de productos proximos a caducar**

<!-- ![Recordatorio caducidad WhatsApp](./assets/whatsapp_recordatorio.jpg) -->

> Respuesta del sistema ante la pregunta de que productos deberian consumirse pronto. El sistema identifica productos perecederos en el inventario (comida preparada: 3 dias, frutas y verduras: 5 dias) y genera una alerta con recomendaciones de consumo.

---

## 9. Etapa 6 — Dashboard de observabilidad

### Que se hizo

Se desarrollo un dashboard administrativo web que transforma el monitoreo del sistema en una plataforma de evaluacion cuantitativa. A diferencia de paneles de administracion convencionales, el dashboard no solo muestra el estado de la base de datos sino el comportamiento interno de cada capa de la arquitectura durante cada interaccion.

### Variables monitoreadas en tiempo real

| Variable | Descripcion |
|---|---|
| Latencia extremo a extremo | Tiempo total desde que llega el mensaje hasta que se entrega la respuesta |
| Latencia de inferencia LLM | Tiempo que tarda el modelo de lenguaje en generar la respuesta |
| Prompt tokens | Numero de tokens enviados al modelo en cada llamada |
| Completion tokens | Numero de tokens generados por el modelo |
| Total tokens | Consumo total acumulado |
| Tokens por segundo | Velocidad de inferencia del modelo |
| Confianza del orquestador | Nivel de certeza del LLM sobre la intencion detectada |
| Validez JSON | Tasa de respuestas del orquestador que son JSON parseable |
| Validacion de esquema | Tasa de respuestas que cumplen el esquema exacto esperado |
| Precision de intenciones | Accuracy de clasificacion en pruebas controladas |
| Tasa de exito de ejecucion | Porcentaje de solicitudes completadas sin error |
| Historial de conversaciones | Registro completo con intencion detectada y metadatos |
| Trazas de ejecucion | Secuencia de agentes invocados por cada solicitud |

El dashboard incluye ademas herramientas de evaluacion controlada que ejecutan suites de pruebas predefinidas para medir el desempeno del orquestador bajo condiciones repetibles.

### Capturas — Dashboard de observabilidad

---

**Captura 16 — Vista general del dashboard**

<!-- ![Dashboard vista general](./assets/dashboard_general.png) -->

> Vista principal del dashboard administrativo mostrando el resumen operacional del sistema: total de mensajes procesados, latencia promedio, tokens consumidos, tasa de exito de arquitectura y tasa de validacion de JSON. Esta vista permite evaluar el estado general del sistema de un vistazo.

---

**Captura 17 — Metricas de latencia del LLM**

<!-- ![Dashboard metricas LLM](./assets/dashboard_llm.png) -->

> Panel de metricas del modelo de lenguaje mostrando la latencia de inferencia por sesion, consumo de tokens por llamada y velocidad de generacion (tokens por segundo). Se puede observar la latencia promedio de 27.15 segundos correspondiente a inferencia local en hardware de consumo con Ollama.

---

**Captura 18 — Precision de clasificacion de intenciones**

<!-- ![Dashboard clasificacion intenciones](./assets/dashboard_intenciones.png) -->

> Panel de evaluacion del orquestador mostrando los resultados de las pruebas controladas de clasificacion de intenciones. La tabla muestra el mensaje enviado, la intencion esperada, la intencion detectada y si la clasificacion fue correcta. Los resultados obtenidos fueron 100% de accuracy en el dataset de prueba.

---

**Captura 19 — Historial de conversaciones con trazas**

<!-- ![Dashboard historial conversaciones](./assets/dashboard_historial.png) -->

> Vista del historial de conversaciones en el dashboard, mostrando cada interaccion con su intencion detectada, confianza del orquestador, validez del JSON, latencia y estado de ejecucion. Esta informacion permite depurar el comportamiento del sistema y analizar patrones de uso.

---

## 10. Prueba final del sistema completo

Esta seccion documenta una prueba de extremo a extremo del sistema completo, desde la captura de imagen hasta la respuesta final al usuario.

### Descripcion de la prueba

La prueba cubre el flujo completo de la arquitectura en una sola sesion:

1. La ESP32-CAM captura una imagen de la alacena con varios productos del catalogo
2. El sistema detecta los productos mediante Gemini Vision y actualiza el inventario
3. El usuario consulta su inventario por WhatsApp
4. El usuario solicita una receta con lo que tiene disponible
5. El usuario pide su lista de compras
6. El dashboard muestra las metricas de toda la sesion

---

**Captura 20 — Imagen capturada por ESP32-CAM al inicio de la prueba**

<!-- ![Captura ESP32-CAM prueba final](./assets/prueba_final_captura.jpg) -->

> Imagen tomada por la ESP32-CAM al inicio de la prueba final. En ella se pueden distinguir varios de los 26 productos del catalogo. Esta imagen es la entrada al pipeline de vision: se guarda como `latest.jpg` y se envia a Gemini Vision para deteccion.

---

**Captura 21 — Resultado de deteccion y actualizacion del inventario**

<!-- ![Resultado deteccion prueba final](./assets/prueba_final_deteccion.png) -->

> Respuesta del endpoint `/vision/detect` mostrando los productos identificados por Gemini Vision con sus niveles de confianza. Los productos con confianza mayor o igual a 0.5 se insertan o actualizan en la tabla `inventory` de SQLite. Se puede observar que el sistema descarto detecciones de baja confianza.

---

**Captura 22 — Consulta de inventario por WhatsApp tras la deteccion**

<!-- ![WhatsApp inventario actualizado prueba final](./assets/prueba_final_inventario.jpg) -->

> Conversacion de WhatsApp donde el usuario consulta el inventario inmediatamente despues de la deteccion visual. El sistema responde con la lista de productos que se acaban de registrar, confirmando que el pipeline de vision actualizo correctamente la base de datos.

---

**Captura 23 — Receta generada con los productos detectados**

<!-- ![WhatsApp receta prueba final](./assets/prueba_final_receta.jpg) -->

> El usuario solicita una receta con lo que tiene disponible. El Recipe Agent genera una propuesta usando exclusivamente ingredientes del inventario recien actualizado por vision. La respuesta incluye nombre de la receta, ingredientes con cantidades, pasos de preparacion, informacion nutrimental y tiempo estimado.

---

**Captura 24 — Lista de compras generada tras el analisis del inventario**

<!-- ![WhatsApp lista compras prueba final](./assets/prueba_final_compras.jpg) -->

> El usuario pide su lista de compras. El Shopping Agent analiza el inventario actual, detecta productos agotados y con stock bajo, evalua el balance nutricional de lo disponible y genera recomendaciones priorizadas. La lista indica que comprar primero y por que.

---

**Captura 25 — Dashboard con metricas de la sesion completa**

<!-- ![Dashboard metricas sesion prueba final](./assets/prueba_final_dashboard.png) -->

> Vista del dashboard al finalizar la prueba, mostrando las metricas acumuladas de la sesion: numero de interacciones procesadas, latencia promedio, tokens consumidos en total, confianza promedio del orquestador, tasa de JSON valido y trazas de ejecucion de cada agente invocado. Esta vista permite evaluar el comportamiento de la arquitectura completa en condiciones reales de uso.

---

## 11. Resultados y metricas

Los resultados se obtuvieron mediante dos estrategias de evaluacion: experimentos controlados con un dataset predefinido de mensajes representativos, y evaluacion con usuarios reales a traves de WhatsApp con lenguaje coloquial y expresiones espontaneas.

### Clasificacion de intenciones — Evaluacion controlada

| Metrica | Valor |
|---|---|
| Accuracy | 100% |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |

El orquestador clasifico correctamente todos los casos del benchmark. Ademas, todas las respuestas pasaron la validacion de JSON y la verificacion de esquema, indicando que el modelo produce de forma consistente salidas estructuradas compatibles con los agentes especializados.

### Rendimiento del modelo de lenguaje

| Metrica | Promedio |
|---|---|
| Prompt tokens | 340 |
| Completion tokens | 52 |
| Total tokens | 392 |
| Latencia de inferencia | 27.15 s |
| Tokens por segundo | 1.92 |

La latencia corresponde a ejecucion local del LLM en hardware de consumo con Ollama. Aunque es mayor que servicios en la nube, el despliegue local elimina costos de API y garantiza privacidad completa de los datos del usuario.

### Metricas operacionales del sistema

| Metrica | Valor |
|---|---|
| Latencia promedio del backend | 0.003 s |
| Latencia promedio del chat | 2.55 s |
| Latencia maxima del chat | 27.97 s |
| Tasa de exito de arquitectura | 100% |
| Validez de JSON estructurado | 100% |
| Tasa de validacion de esquema | 100% |

El backend contribuye solo 0.003 segundos del tiempo total de respuesta. El costo computacional principal proviene de la inferencia del modelo de lenguaje, confirmando que la arquitectura de software en si misma introduce una sobrecarga minima.

---

## 12. Stack tecnologico

| Componente | Tecnologia | Version |
|---|---|---|
| Hardware camara | ESP32-CAM (OV2640) | --- |
| VLM deteccion visual | Gemini 2.5 Flash Vision | API v2 |
| LLM orquestador | llama3.2:3b via Ollama | 3b |
| Backend | FastAPI + Uvicorn | 0.136+ |
| Base de datos | SQLite | 3.x |
| Mensajeria | whatsapp-web.js | --- |
| Libreria VLM | google-genai | 2.8+ |
| Procesamiento de imagen | Pillow | 12.x |
| Cliente HTTP async | httpx | 0.28+ |
| Frontend dashboard | HTML / CSS / JavaScript | --- |
| Variables de entorno | python-dotenv | 1.x |

---

## 13. Instalacion

### Requisitos previos

- Python 3.11 o superior
- Node.js (para whatsapp-web.js)
- Ollama instalado con el modelo llama3.2:3b
- API Key de Gemini (disponible en https://aistudio.google.com)
- Modulo ESP32-CAM con firmware configurado en la red local

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Marthavlds1/ProspectivaTecnologica.git
cd ProspectivaTecnologica/backend

# 2. Crear entorno virtual
python -m venv .venv

# Windows:
.\.venv\Scripts\Activate.ps1

# Linux / Mac:
source .venv/bin/activate

# 3. Instalar dependencias Python
pip install fastapi uvicorn google-genai pillow python-dotenv httpx

# 4. Crear archivo .env en la raiz del proyecto
# El archivo debe contener:
# GEMINI_API_KEY=tu_key_de_gemini_aqui

# 5. Inicializar la base de datos
python iniciardb.py

# 6. Arrancar Ollama con el modelo necesario
ollama serve
ollama pull llama3.2:3b

# 7. Correr el backend
python -m uvicorn app.main:app --reload --port 8000
```

### Verificacion

- Documentacion interactiva de la API: http://localhost:8000/docs
- Frontend administrativo: abrir frontend/admin.html con Live Server en VS Code
- Endpoint de salud: http://localhost:8000/

---

## 14. Descargas

| Recurso | Descripcion |
|---|---|
| [Repositorio en GitHub](https://github.com/Marthavlds1/ProspectivaTecnologica) | Codigo fuente completo del proyecto |
| [Articulo tecnico IEEE (PDF)](./ReporteProspectivaTecnologica.pdf) | Reporte completo: A Multi-Agent Architecture Based on Vision and Language Models for Intelligent Food Inventory Management |
| [Descargar ZIP del proyecto](https://github.com/Marthavlds1/ProspectivaTecnologica/archive/refs/heads/main.zip) | Descarga directa de todo el repositorio en formato ZIP |
| [.env.example](./backend/app/vision/.env.example) | Plantilla de variables de entorno necesarias para ejecutar el sistema |

---

## 15. Estructura del proyecto

```
ProspectivaTecnologica/
├── ReporteProspectivaTecnologica.pdf
├── README.md
├── backend/
│   ├── iniciardb.py
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes_chat.py
│   │   │   ├── routes_inventory.py
│   │   │   ├── routes_metrics.py
│   │   │   ├── routes_orchestrator.py
│   │   │   └── routes_vision.py
│   │   ├── data/
│   │   │   ├── food_catalog.py
│   │   │   └── foods.json
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   ├── create_db.py
│   │   │   ├── metrics_repository.py
│   │   │   ├── seed_demo.py
│   │   │   └── user_repository.py
│   │   ├── models/
│   │   │   ├── chat_message.py
│   │   │   ├── inventory.py
│   │   │   ├── nutrition_profile.py
│   │   │   ├── recipe.py
│   │   │   ├── shopping_list.py
│   │   │   └── user_profile.py
│   │   ├── prompts/
│   │   │   ├── recipe_prompt.txt
│   │   │   ├── shopping_prompt.txt
│   │   │   ├── nutrition_prompt.txt
│   │   │   ├── meal_plan_prompt.txt
│   │   │   ├── general_prompts.txt
│   │   │   └── inventory_analysis_prompt.txt
│   │   ├── services/
│   │   │   ├── agent_decision_service.py
│   │   │   ├── chat_router_service.py
│   │   │   ├── inventory_analysis_service.py
│   │   │   ├── inventory_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── meal_plan_service.py
│   │   │   ├── nutrition_service.py
│   │   │   ├── orchestrator_service.py
│   │   │   ├── recipe_service.py
│   │   │   └── shopping_service.py
│   │   ├── utils/
│   │   │   ├── inventory_formatter.py
│   │   │   └── prompt_manager.py
│   │   └── vision/
│   │       ├── vision_camera.py
│   │       ├── vision_inventory.py
│   │       └── vision_llm.py
│   └── images/
│       └── latest.jpg
└── frontend/
    ├── admin.html
    ├── app.js
    └── styles.css
```

---

Proyecto desarrollado como parte del curso de Prospectiva de IA
Ingenieria Mecatronica y Sistemas Ciberfisicos
Universidad Iberoamericana Ciudad de Mexico — 2026
