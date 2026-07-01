---
layout: default
title: Portafolio — Proyecto Final  
nav_order: 9
---

# A Multi-Agent Architecture Based on Vision and Language Models for Intelligent

**Sistema ciberfísico para la gestión autónoma de inventario alimentario mediante visión por computadora y modelos de lenguaje de gran escala**

> Proyecto final · Prospectiva de IA · Ingeniería Mecatrónica · Universidad Iberoamericana Ciudad de México · 2026

**Equipo:** Martha Valdés · Marco Calixto · Renata Badillo

---

## Tabla de contenidos

1. [Descripcion general](#descripcion-general)
2. [Arquitectura multi-agente](#arquitectura-multi-agente)
3. [Pipeline de vision por computadora](#pipeline-de-vision-por-computadora)
4. [Orquestador LLM](#orquestador-llm)
5. [Agentes especializados](#agentes-especializados)
6. [Integracion con WhatsApp](#integracion-con-whatsapp)
7. [Dashboard de observabilidad](#dashboard-de-observabilidad)
8. [API REST](#api-rest)
9. [Base de datos](#base-de-datos)
10. [Metodologia experimental](#metodologia-experimental)
11. [Resultados](#resultados)
12. [Stack tecnologico](#stack-tecnologico)
13. [Instalacion y uso](#instalacion-y-uso)
14. [Descargas](#descargas)
15. [Estructura del proyecto](#estructura-del-proyecto)

---

## Descripcion general

Alacena Inteligente es un sistema de gestion inteligente de inventario alimentario que integra vision por computadora, modelos de lenguaje de gran escala y agentes de software especializados en una arquitectura multi-agente unificada.

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

---

## Arquitectura multi-agente

La arquitectura sigue un diseno en capas que separa percepcion, razonamiento, ejecucion y monitoreo en componentes de software independientes.

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

La principal decision de diseno es que el LLM nunca ejecuta logica de negocio directamente. En cambio, produce representaciones JSON estructuradas que son validadas por el backend antes de delegar la ejecucion a agentes especializados. Esta separacion mejora la modularidad, escalabilidad, mantenibilidad y confiabilidad del sistema.

---

## Pipeline de vision por computadora

### Motivacion del enfoque

La camara ESP32-CAM con sensor OV2640 tiene limitaciones de resolucion y condiciones de iluminacion. Para compensar, se implemento un prompt enriquecido con descripciones visuales especificas de cada producto del catalogo. El VLM recibe no solo los nombres de los productos permitidos sino tambien caracteristicas visuales detalladas (color del empaque, forma, texto visible, logotipo), actuando como un refuerzo contextual que mejora la precision de deteccion bajo condiciones de imagen no ideales.

### Flujo de deteccion

```
ESP32-CAM
    |
    | POST /vision/upload (bytes)
    v
Backend guarda latest.jpg
    |
    | detectar_alimentos(path)
    v
Pillow abre imagen
    |
    | Gemini 2.5 Flash Vision
    | + catalogo de 26 productos
    | + descripciones visuales especificas
    | + response_mime_type: application/json
    v
JSON estructurado:
{
  "foods": [
    {"name": "Papas Pringles", "confidence": 0.95, "quantity": "1"}
  ]
}
    |
    | Filtro: confidence >= 0.5
    v
Normalizacion: estandarizacion de nombres, eliminacion de duplicados
    |
    v
InventoryService.add_food() --> SQLite
```

### Catalogo de productos soportados

| Producto | Descripcion visual para el VLM |
|---|---|
| Refresco Ameyal | Botella color rosa |
| Paquete Gelatina Dany | Dos vasos morados |
| Jugo de Mango Jumex | Caja azul con mango amarillo |
| Cereal Trix | Caja roja con logo Trix en verde |
| Carton Nutri Leche | Caja blanca con logo de letras blancas |
| Carton LALA leche | Caja blanca con logo azul y franja roja |
| Aceite Nutrioli | Botella dorada con etiqueta y tapa verdes |
| Botella Bonafont | Botella de agua transparente |
| Chocolate Larin | Barra de color verde |
| Mantequilla Primavera | Barra de color amarillo |
| ChocoMilk | Lata cilindrica de color azul |
| Paquete Espagueti | Paquete transparente con logo amarillo-negro |
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

### Capturas del sistema de vision

<!-- Agregar aqui capturas de la camara ESP32-CAM y las detecciones -->
<!-- Ejemplo: -->
<!-- ![Captura ESP32-CAM alacena](./assets/vision_captura1.jpg) -->
<!-- ![Resultado deteccion Gemini](./assets/vision_resultado1.png) -->

> Insertar capturas de la camara ESP32-CAM apuntando a la alacena y los resultados de deteccion de Gemini Vision.

---

## Orquestador LLM

El orquestador es el componente central de la arquitectura. A diferencia de los chatbots tradicionales, el LLM nunca ejecuta logica de negocio ni modifica directamente la base de datos. Para cada mensaje entrante ejecuta la siguiente secuencia:

1. Comprension del lenguaje natural
2. Clasificacion de intencion
3. Extraccion de entidades
4. Estimacion de confianza
5. Generacion de JSON estructurado
6. Validacion de esquema
7. Seleccion de agente

Ejemplo de salida estructurada del orquestador:

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
    ]
  },
  "needs_profile": false,
  "reason": "El usuario indica que compro productos para agregar al inventario."
}
```

Cuando la respuesta falla la validacion de esquema, el backend activa un mecanismo de fallback basado en reglas para mantener la disponibilidad del sistema sin interrumpir la interaccion del usuario.

### Intenciones soportadas

| Intencion | Palabras clave disparadoras |
|---|---|
| `inventory` | "que tengo", "que hay", "alacena", "despensa", "mis productos" |
| `add_inventory` | "compre", "agregue", "aniade", "tengo ahora" |
| `remove_inventory` | "elimina", "quita", "consumi", "me comi", "ya no tengo" |
| `rename_inventory` | "cambia", "renombra", "corrige", "quise decir" |
| `recipe` | "receta", "cocinar", "que puedo cocinar", "que preparo" |
| `shopping` | "compras", "lista de compras", "que falta", "que necesito" |
| `meal_plan` | "dieta", "plan semanal", "plan alimenticio" |
| `nutrition` | "calorias", "macros", "TMB", "GET" |
| `reminders` | "caducidad", "consumir pronto", "que se va a echar a perder" |
| `profile_register` | "registrar perfil" |
| `general` | cualquier otro mensaje |

---

## Agentes especializados

| Agente | Responsabilidad |
|---|---|
| Inventory Agent | Consulta, insercion, actualizacion, eliminacion y renombrado de productos |
| Recipe Agent | Generacion de recetas priorizando ingredientes del inventario actual |
| Nutrition Agent | Calculo de TMB, GET, calorias recomendadas y distribucion de macronutrientes |
| Shopping Agent | Recomendaciones de compra segun niveles de inventario y balance nutricional |
| Meal Planning Agent | Planes semanales combinando disponibilidad en inventario y requisitos nutricionales |

Cada agente recibe entidades estructuradas del orquestador, nunca lenguaje natural. Esto mantiene la logica de negocio determinista e independiente de la implementacion del modelo de lenguaje.

---

## Integracion con WhatsApp

La interaccion del usuario se implemento mediante WhatsApp usando la libreria whatsapp-web.js. Los mensajes entrantes se normalizan automaticamente antes de ser enviados al backend FastAPI. Una vez completado el procesamiento, las respuestas se devuelven al usuario por el mismo canal.

El uso de WhatsApp como interfaz principal elimina la necesidad de una aplicacion movil dedicada y proporciona un mecanismo de interaccion familiar para la mayoria de los usuarios.

### Capturas del chat de WhatsApp

<!-- Agregar aqui capturas del chat de WhatsApp con el sistema -->
<!-- Ejemplo: -->
<!-- ![Chat WhatsApp - consulta inventario](./assets/whatsapp_inventario.jpg) -->
<!-- ![Chat WhatsApp - solicitud de receta](./assets/whatsapp_receta.jpg) -->
<!-- ![Chat WhatsApp - lista de compras](./assets/whatsapp_compras.jpg) -->

> Insertar capturas del chat de WhatsApp mostrando consultas de inventario, solicitudes de recetas, listas de compras y planes nutricionales.

---

## Dashboard de observabilidad

Una de las principales contribuciones de la arquitectura es la capa de observabilidad que monitorea continuamente el comportamiento interno de cada componente. A diferencia de los asistentes conversacionales convencionales que exponen solo la respuesta final, el dashboard proporciona informacion detallada sobre cada etapa de la pipeline de ejecucion.

### Variables monitoreadas

| Variable | Descripcion |
|---|---|
| Latencia extremo a extremo | Tiempo total de respuesta |
| Latencia de inferencia LLM | Tiempo de procesamiento del modelo de lenguaje |
| Prompt tokens | Tokens de entrada |
| Completion tokens | Tokens generados |
| Total tokens | Consumo total de tokens |
| Tokens por segundo | Velocidad de inferencia |
| Precision de clasificacion de intenciones | Accuracy del orquestador |
| Validez JSON estructurado | Tasa de salidas parseables |
| Validacion de esquema | Tasa de cumplimiento del esquema esperado |
| Tasa de exito de ejecucion | Porcentaje de solicitudes completadas correctamente |
| Historial de conversacion | Registro completo de interacciones |
| Trazas de ejecucion de agentes | Secuencia de agentes invocados por solicitud |

### Capturas del dashboard

<!-- Agregar aqui capturas del dashboard administrativo -->
<!-- Ejemplo: -->
<!-- ![Dashboard - metricas generales](./assets/dashboard_general.png) -->
<!-- ![Dashboard - clasificacion de intenciones](./assets/dashboard_intenciones.png) -->
<!-- ![Dashboard - metricas del LLM](./assets/dashboard_llm.png) -->

> Insertar capturas del dashboard mostrando metricas de latencia, consumo de tokens, precision de clasificacion de intenciones y trazas de ejecucion.

### Capturas del frontend

<!-- Agregar aqui capturas del panel de administracion web -->
<!-- Ejemplo: -->
<!-- ![Frontend - panel de inventario](./assets/frontend_inventario.png) -->
<!-- ![Frontend - panel de chat](./assets/frontend_chat.png) -->
<!-- ![Frontend - panel de metricas](./assets/frontend_metricas.png) -->

> Insertar capturas del frontend web mostrando el panel de inventario, la interfaz de chat y el panel de metricas.

---

## API REST

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/` | Health check |
| GET | `/inventory/db` | Consulta inventario desde SQLite |
| POST | `/inventory/add` | Agrega producto manualmente |
| POST | `/inventory/remove` | Elimina o reduce cantidad de producto |
| POST | `/vision/upload` | Recibe imagen del ESP32-CAM |
| POST | `/vision/detect` | Analiza latest.jpg y actualiza inventario |
| POST | `/vision/upload-and-detect` | Sube imagen y detecta en un solo paso |
| POST | `/chat` | Consulta al copiloto activo |
| POST | `/orchestrator` | Enrutamiento avanzado con LLM |
| GET | `/metrics` | Historial de metricas del LLM |
| GET | `/metrics/summary` | Resumen estadistico del sistema |
| GET | `/metrics/intent-tests` | Resultados de pruebas de intencion |

---

## Base de datos

SQLite con tablas independientes para cada dominio de informacion:

```sql
-- Inventario de productos
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    quantity INTEGER NOT NULL,
    source TEXT,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Perfil nutricional del usuario
CREATE TABLE users (
    usuario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp_number TEXT UNIQUE,
    nombre TEXT,
    edad INTEGER,
    peso REAL,
    altura REAL,
    activity_level TEXT,
    objetivo TEXT,
    dietary_restrictions TEXT,
    budget REAL
);

-- Metricas de inferencia del LLM
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

-- Historial de conversaciones con metricas del orquestador
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dataset de pruebas de intencion
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

Las inserciones de inventario usan `ON CONFLICT ... DO UPDATE` para que una segunda deteccion del mismo producto sume cantidad en lugar de crear un duplicado.

---

## Metodologia experimental

Se implementaron dos estrategias de evaluacion complementarias.

### Evaluacion controlada

Se construyo un dataset de mensajes representativos cubriendo todas las operaciones soportadas por el sistema. Cada mensaje tiene una etiqueta de intencion esperada que permite evaluar cuantitativamente las predicciones del orquestador. Para cada caso de prueba el sistema registra automaticamente:

- Intencion esperada y predicha
- Respuesta generada
- Latencia extremo a extremo
- Validez del JSON
- Resultado de validacion del esquema
- Estado de ejecucion

Esto permite calcular Accuracy, Precision, Recall y F1-score, ademas de matrices de confusion para visualizar ambiguedades entre intenciones.

### Evaluacion con usuarios reales via WhatsApp

Los usuarios interactuaron naturalmente con el sistema sin seguir plantillas predefinidas, usando lenguaje coloquial, oraciones incompletas y expresiones conversacionales. Cada interaccion genero una traza de ejecucion completa almacenada en la base de datos para analisis posterior.

---

## Resultados

### Clasificacion de intenciones (evaluacion controlada)

| Metrica | Valor |
|---|---|
| Accuracy | 100% |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |

Todos los casos del benchmark fueron clasificados correctamente. Ademas, todas las respuestas pasaron la validacion de JSON y la verificacion de esquema, indicando que el modelo produce de forma consistente salidas estructuradas compatibles con los agentes especializados.

### Rendimiento del modelo de lenguaje

| Metrica | Promedio |
|---|---|
| Prompt Tokens | 340 |
| Completion Tokens | 52 |
| Total Tokens | 392 |
| Latencia de inferencia | 27.15 s |
| Tokens/s | 1.92 |

La latencia corresponde principalmente a la ejecucion local del LLM en hardware de consumo mediante Ollama. Aunque la latencia es considerablemente mayor que servicios comerciales en la nube, el despliegue local proporciona control completo sobre los datos del usuario, elimina costos de API externos y preserva la privacidad.

### Metricas operacionales del sistema

| Metrica | Valor |
|---|---|
| Latencia promedio del backend | 0.003 s |
| Latencia promedio del chat | 2.55 s |
| Latencia maxima del chat | 27.97 s |
| Tasa de exito de arquitectura | 100% |
| Validez de JSON estructurado | 100% |
| Tasa de validacion de esquema | 100% |

El backend contribuye solo una fraccion minima del tiempo total de ejecucion. La mayor parte del costo computacional proviene de la inferencia del modelo de lenguaje, confirmando que la arquitectura de software en si misma introduce una sobrecarga minima.

---

## Stack tecnologico

| Componente | Tecnologia | Version |
|---|---|---|
| Hardware camara | ESP32-CAM (OV2640) | --- |
| VLM (vision) | Gemini 2.5 Flash Vision | API v2 |
| LLM (orquestador) | llama3.2:3b via Ollama | 3b |
| Backend | FastAPI + Uvicorn | 0.136+ |
| Base de datos | SQLite | 3.x |
| Mensajeria | whatsapp-web.js | --- |
| Libreria VLM | google-genai | 2.8+ |
| Procesamiento imagen | Pillow | 12.x |
| HTTP client | httpx | 0.28+ |
| Frontend | HTML / CSS / JavaScript | --- |
| Variables de entorno | python-dotenv | 1.x |

---

## Instalacion y uso

### Requisitos previos

- Python 3.11+
- Node.js (para whatsapp-web.js)
- Ollama instalado y corriendo con llama3.2:3b
- API Key de Gemini (obtener en https://aistudio.google.com)

### Instalacion

```bash
# 1. Clona el repositorio
git clone https://github.com/Marthavlds1/ProspectivaTecnologica.git
cd ProspectivaTecnologica/backend

# 2. Crea y activa entorno virtual
python -m venv .venv

# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# 3. Instala dependencias Python
pip install fastapi uvicorn google-genai pillow python-dotenv httpx

# 4. Crea el archivo .env en la raiz del proyecto
echo "GEMINI_API_KEY=tu_key_aqui" > ../.env

# 5. Inicializa la base de datos
python iniciardb.py

# 6. Arranca Ollama en otra terminal
ollama serve
ollama pull llama3.2:3b

# 7. Corre el backend
python -m uvicorn app.main:app --reload --port 8000
```

### Uso

- API docs interactivos: http://localhost:8000/docs
- Frontend admin: abrir frontend/admin.html con Live Server
- Subir imagen manualmente: POST /vision/upload con la imagen en el body
- Detectar y actualizar inventario: POST /vision/detect

---

## Descargas

| Archivo | Descripcion | Enlace |
|---|---|---|
| Repositorio completo | Codigo fuente del proyecto | [Ver en GitHub](https://github.com/Marthavlds1/ProspectivaTecnologica) |
| Articulo IEEE | Reporte tecnico completo en formato IEEE | [Descargar PDF](./ReporteProspectivaTecnologica.pdf) |
| .env.example | Plantilla de variables de entorno | [Ver archivo](./backend/app/vision/.env.example) |

> Para descargar el repositorio completo como ZIP: Code -> Download ZIP en la pagina principal del repositorio de GitHub.

---

## Estructura del proyecto

```
ProspectivaTecnologica/
├── ReporteProspectivaTecnologica.pdf
├── backend/
│   ├── app/
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
│   │   │   └── user_repository.py
│   │   ├── models/
│   │   ├── services/
│   │   │   ├── chat_router_service.py
│   │   │   ├── inventory_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── meal_plan_service.py
│   │   │   ├── nutrition_service.py
│   │   │   ├── orchestrator_service.py
│   │   │   ├── recipe_service.py
│   │   │   └── shopping_service.py
│   │   ├── vision/
│   │   │   ├── vision_llm.py
│   │   │   ├── vision_camera.py
│   │   │   └── vision_inventory.py
│   │   └── main.py
│   └── images/
│       └── latest.jpg
└── frontend/
    ├── admin.html
    ├── app.js
    └── styles.css
```

---

Proyecto desarrollado como parte del curso de Prospectiva de IA · IBERO Ciudad de Mexico · 2026

Publicado en formato IEEE: *A Multi-Agent Architecture Based on Vision and Language Models for Intelligent Food Inventory Management*