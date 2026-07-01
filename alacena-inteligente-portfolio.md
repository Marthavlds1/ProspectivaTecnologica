---
layout: default
title: Proyecto final
nav_order: 9
---

# 🧠 Alacena Inteligente

**Sistema ciber-físico para la gestión autónoma de inventario alimentario mediante visión por computadora y modelos de lenguaje de gran escala**

> Proyecto final · Prospectiva de IA · Ingeniería Mecatrónica · Universidad Iberoamericana Ciudad de México · 2026

**Equipo:** Martha Valdés · Marco [Apellido] · Renata [Apellido]

---

## Tabla de contenidos

1. [Descripción general](#descripción-general)
2. [Arquitectura del sistema](#arquitectura-del-sistema)
3. [Pipeline de visión por computadora](#pipeline-de-visión-por-computadora)
4. [Copilotos conversacionales](#copilotos-conversacionales)
5. [API REST](#api-rest)
6. [Base de datos](#base-de-datos)
7. [Métricas y evaluación](#métricas-y-evaluación)
8. [Pruebas realizadas](#pruebas-realizadas)
9. [Stack tecnológico](#stack-tecnológico)
10. [Instalación y uso](#instalación-y-uso)
11. [Estructura del proyecto](#estructura-del-proyecto)

---

## Descripción general

**Alacena Inteligente** es un sistema que detecta automáticamente productos alimenticios en una despensa doméstica mediante una cámara ESP32-CAM, los registra en una base de datos SQLite y permite consultar el inventario, generar recetas, listas de compras y planes nutricionales mediante copilotos conversacionales especializados.

El sistema opera de forma **híbrida**: usa Gemini 2.5 Flash (API de Google) para visión y un modelo local (`llama3.2:3b` vía Ollama) para el chat, garantizando que los datos personales del usuario no salgan de la red local.

### Funcionalidades principales

| Funcionalidad | Descripción |
|---|---|
| 📷 Detección visual | ESP32-CAM captura la alacena y Gemini identifica productos |
| 📦 Inventario automático | Los productos detectados se agregan/actualizan en SQLite |
| 💬 Chat con copilotos | 4 copilotos especializados vía LLM local |
| 🍳 Generación de recetas | Recetas basadas en el inventario disponible |
| 🛒 Lista de compras | Sugerencias de qué comprar según el inventario |
| 🥗 Plan nutricional | Planes semanales personalizados por perfil del usuario |
| ⏰ Recordatorios | Alertas de productos próximos a caducar |

---

## Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE PERCEPCIÓN                     │
│                                                             │
│   ESP32-CAM (OV2640)                                        │
│   Captura imagen → POST /vision/upload                      │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP (bytes)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PROCESAMIENTO                    │
│                    FastAPI + Python                         │
│                                                             │
│  ┌─────────────────┐    ┌──────────────────────────────┐   │
│  │  vision_llm.py  │    │   ChatRouterService           │   │
│  │                 │    │   OrchestratorService         │   │
│  │  Gemini 2.5     │    │   llama3.2:3b (Ollama local)  │   │
│  │  Flash Vision   │    │                              │   │
│  └────────┬────────┘    └─────────────┬────────────────┘   │
│           │                           │                     │
│           ▼                           ▼                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SQLite (inventory.db)                   │   │
│  │  inventory · users · llm_metrics                     │   │
│  │  chat_history · intent_tests                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/JSON
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE PRESENTACIÓN                      │
│                                                             │
│   Frontend web (HTML/CSS/JS)                                │
│   Panel inventario · Chat · Visión · Métricas               │
└─────────────────────────────────────────────────────────────┘
```

---

## Pipeline de visión por computadora

### Motivación del enfoque

La cámara seleccionada (ESP32-CAM con sensor OV2640) tiene una resolución máxima de 2 MP con limitaciones en condiciones de baja iluminación y enfoque. Para compensar esta restricción, se implementó un **entrenamiento reforzado del prompt** del VLM: en lugar de pedir al modelo que identifique cualquier objeto, se le proporcionan:

1. Un **catálogo cerrado de 26 productos** exactamente los que forman parte de la alacena real del proyecto.
2. **Descripciones visuales específicas** de cada producto (color del empaque, forma, texto visible, logotipo).
3. **Reglas estrictas de no-alucinación**: si el texto del empaque no es legible o la marca no puede distinguirse con claridad, el modelo debe omitir el producto.

Este enfoque actúa como un refuerzo contextual que compensa la baja resolución de la cámara, permitiendo al VLM hacer inferencias más precisas sobre los productos incluso cuando la imagen no es perfectamente nítida.

### Catálogo de productos soportados

| # | Producto | Descripción visual para el VLM |
|---|---|---|
| 1 | Refresco Ameyal | Botella color rosa |
| 2 | Paquete Gelatina Dany | Dos vasos morados |
| 3 | Jugo de Mango Jumex | Caja azul con mango amarillo |
| 4 | Cereal Trix | Caja roja con logo Trix en verde |
| 5 | Cartón Nutri Leche | Caja blanca, logo con letras blancas |
| 6 | Cartón LALA leche | Caja blanca, logo azul con franja roja |
| 7 | Aceite Nutrioli | Botella dorada con etiqueta verde |
| 8 | Botella Bonafont | Botella de agua transparente |
| 9 | Chocolate Larín | Barra de color verde |
| 10 | Mantequilla Primavera | Barra de color amarillo |
| 11 | ChocoMilk | Lata cilíndrica azul |
| 12 | Paquete Espagueti | Paquete transparente con logo amarillo-negro |
| 13 | Jugo de fresa Boing | Lata roja con letras verdes |
| 14 | Papas Pringles | Lata roja con logo blanco |
| 15 | Jugo de mango del Valle | Lata amarilla con logo negro-blanco |
| 16 | Salsa de tomate | Lata negra con logo rojo |
| 17 | Mayonesa McCormick | Frasco blanco con etiqueta y tapa rojas |
| 18 | Sal La Fina | Frasco blanco con etiqueta azul-rojo y tapa amarilla |
| 19 | Jugo FuseTea | Lata amarilla con letras negras |
| 20 | Jugo pera Jumex | Lata azul con logo verde-rojo |
| 21 | Bebida Energética Red Bull | Lata azul-gris con logo rojo-amarillo |
| 22 | Refresco CocaCola | Botella negra con etiqueta roja |
| 23 | Cereal Nesquik | Caja amarilla con logo café y azul |
| 24 | Cereal ChocoKrispis | Caja café con letras amarillas |
| 25 | Refresco Fanta | Lata naranja con logo letras verdes |

### Flujo de detección

```
ESP32-CAM
    │
    │ POST /vision/upload (bytes)
    ▼
Backend guarda latest.jpg
    │
    │ detectar_alimentos(path)
    ▼
Pillow abre imagen
    │
    │ Gemini 2.5 Flash
    │ + prompt con catálogo + descripciones visuales
    │ + response_mime_type: application/json
    ▼
JSON estructurado:
{
  "foods": [
    {"name": "Papas Pringles", "confidence": 0.95, "quantity": "1"},
    ...
  ]
}
    │
    │ Filtro: confidence >= 0.5
    ▼
VisionInventory.compare_inv()
    │ Compara detectados vs inventario actual
    │ Clasifica en: nuevos | presentes | faltantes
    ▼
InventoryService.add_food() → SQLite
```

### Lógica de sincronización de inventario

El módulo `VisionInventory` no sobreescribe ciegamente el inventario. Compara lo detectado con el estado actual y clasifica los cambios en tres categorías:

- **Nuevos**: productos detectados que no estaban en el inventario → se agregan
- **Presentes**: productos detectados que ya estaban → se confirman
- **Faltantes**: productos que estaban en el inventario pero no se detectaron en la foto → se marcan para revisión

---

## Copilotos conversacionales

El sistema implementa una arquitectura de **doble clasificador** para el enrutamiento de intenciones:

### Nivel 1: Clasificador por palabras clave (`ChatRouterService`)

Clasificador rápido basado en coincidencia de términos clave. Procesa el mensaje del usuario y asigna una de 11 intenciones posibles:

| Intención | Palabras clave disparadoras |
|---|---|
| `inventory` | "qué tengo", "qué hay", "alacena", "despensa", "mis productos" |
| `add_inventory` | "compré", "agregué", "añade", "tengo ahora" |
| `remove_inventory` | "elimina", "quita", "consumí", "me comí", "ya no tengo" |
| `rename_inventory` | "cambia", "renombra", "corrige", "quise decir" |
| `recipe` | "receta", "cocinar", "qué puedo cocinar", "qué preparo" |
| `shopping` | "compras", "lista de compras", "qué falta", "qué necesito" |
| `meal_plan` | "dieta", "plan semanal", "plan alimenticio" |
| `nutrition` | "calorías", "macros", "TMB", "GET" |
| `reminders` | "caducidad", "consumir pronto", "qué se va a echar a perder" |
| `profile_register` | "registrar perfil" |
| `general` | cualquier otro mensaje |

### Nivel 2: Orquestador LLM (`OrchestratorService`)

Para mensajes ambiguos o complejos, el orquestador usa `llama3.2:3b` para interpretar la intención y extraer entidades estructuradas:

```json
{
  "intent": "add_inventory",
  "action": "add_food",
  "confidence": 0.95,
  "entities": {
    "items": [
      {"name": "mangos", "quantity": 2}
    ]
  },
  "needs_profile": false,
  "reason": "El usuario indica que compró productos."
}
```

### Servicios especializados

| Servicio | Función |
|---|---|
| `RecipeService` | Genera recetas basadas en el inventario actual |
| `ShoppingService` | Crea listas de compras organizadas por categoría |
| `MealPlanService` | Diseña planes alimenticios semanales |
| `NutritionService` | Calcula macros, TMB y GET según el perfil del usuario |
| `InventoryAnalysisService` | Análisis del estado general de la despensa |

Todos los servicios construyen un prompt enriquecido con el inventario actual y el perfil nutricional del usuario, y lo envían a `llama3.2:3b` mediante la API local de Ollama (`http://localhost:11434/api/generate`).

---

## API REST

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Health check |
| GET | `/inventory/db` | Consulta inventario desde SQLite |
| POST | `/inventory/add` | Agrega producto manualmente |
| POST | `/inventory/remove` | Elimina o reduce cantidad de producto |
| POST | `/vision/upload` | Recibe imagen del ESP32-CAM |
| POST | `/vision/detect` | Analiza `latest.jpg` y actualiza inventario |
| POST | `/vision/upload-and-detect` | Sube imagen y detecta en un solo paso |
| POST | `/chat` | Consulta al copiloto activo |
| POST | `/orchestrator` | Enrutamiento avanzado con LLM |
| GET | `/metrics` | Historial de métricas del LLM |
| GET | `/metrics/summary` | Resumen estadístico del sistema |
| GET | `/metrics/intent-tests` | Resultados de pruebas de intención |

---

## Base de datos

SQLite con 5 tablas:

```sql
-- Inventario de productos
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    quantity INTEGER NOT NULL,
    source TEXT,              -- 'vision', 'api', 'manual'
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

-- Métricas de inferencia del LLM
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

-- Historial de conversaciones
CREATE TABLE chat_history (
    numero TEXT,
    mensaje TEXT,
    respuesta TEXT,
    intent TEXT,
    latency_seconds REAL,
    success INTEGER,
    orchestrator_intent TEXT,
    orchestrator_confidence REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Pruebas de intención
CREATE TABLE intent_tests (
    message TEXT,
    expected_intent TEXT,
    detected_intent TEXT,
    is_correct INTEGER,
    latency_seconds REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Lógica upsert en inventario

Las inserciones de visión usan `ON CONFLICT ... DO UPDATE` para que una segunda detección del mismo producto sume cantidad en lugar de crear un duplicado:

```sql
INSERT INTO inventory(name, quantity, source, last_update)
VALUES (?, ?, 'vision', CURRENT_TIMESTAMP)
ON CONFLICT(name)
DO UPDATE SET
    quantity = inventory.quantity + excluded.quantity,
    source = 'vision',
    last_update = CURRENT_TIMESTAMP;
```

---

## Métricas y evaluación

El sistema registra métricas en tres dimensiones:

### 1. Métricas de inferencia LLM

Cada llamada a Ollama registra:

| Métrica | Descripción |
|---|---|
| `prompt_tokens` | Tokens de entrada |
| `completion_tokens` | Tokens generados |
| `latency_seconds` | Tiempo total de respuesta |
| `tokens_per_second` | Velocidad de generación |

### 2. Métricas del orquestador

| Métrica | Descripción |
|---|---|
| `orchestrator_confidence` | Confianza del LLM en la intención detectada |
| `orchestrator_json_valid` | Si el JSON devuelto por el LLM es parseable |
| `orchestrator_schema_valid` | Si el JSON cumple el esquema esperado |

### 3. Métricas de calidad de intención

El sistema calcula automáticamente:

| Métrica | Fórmula |
|---|---|
| Accuracy | correctas / total |
| Precision | TP / (TP + FP) |
| Recall | TP / (TP + FN) |
| F1-score | 2 × P × R / (P + R) |

Estas métricas se consultan en tiempo real desde el panel de métricas del frontend mediante `GET /metrics/summary`.

---

## Pruebas realizadas

### Pruebas de detección visual

Se realizaron capturas con la ESP32-CAM en condiciones de iluminación variable. El prompt enriquecido con descripciones visuales específicas mejoró significativamente la tasa de detección correcta frente al prompt genérico:

| Condición | Sin descripciones visuales | Con descripciones visuales |
|---|:---:|:---:|
| Iluminación óptima | ~60% | ~90% |
| Iluminación reducida | ~30% | ~70% |
| Productos parcialmente ocultos | ~20% | ~45% |

> Nota: los porcentajes son estimaciones basadas en pruebas cualitativas con el catálogo de 26 productos.

### Pruebas de intención del chat

Se probaron los 11 tipos de intención con variaciones de lenguaje natural en español:

| Intención | Ejemplos probados | Resultado |
|---|---|---|
| `inventory` | "qué tengo", "qué hay en mi alacena" | ✅ Correcto |
| `add_inventory` | "compré leche", "agregué 2 jugos" | ✅ Correcto |
| `remove_inventory` | "me comí las papas", "ya no tengo cereal" | ✅ Correcto |
| `recipe` | "qué puedo cocinar hoy", "dame una receta" | ✅ Correcto |
| `shopping` | "qué me falta comprar", "lista del súper" | ✅ Correcto |
| `nutrition` | "cuántas calorías necesito", "calcula mi TMB" | ✅ Correcto |
| `reminders` | "qué se va a echar a perder" | ✅ Correcto |

### Pruebas de pipeline completo

| Prueba | Resultado |
|---|---|
| ESP32-CAM → upload → detect → SQLite | ✅ Funcional |
| Chat → OrchestratorService → JSON → acción | ✅ Funcional |
| Upsert: misma detección dos veces | ✅ Suma cantidad, no duplica |
| Perfil de usuario → plan nutricional personalizado | ✅ Funcional |
| Recordatorio de productos perecederos | ✅ Funcional |

---

## Stack tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Hardware cámara | ESP32-CAM (OV2640) | — |
| VLM (visión) | Gemini 2.5 Flash | API v2 |
| LLM (chat) | llama3.2:3b vía Ollama | 3b |
| Backend | FastAPI + Uvicorn | 0.136+ |
| Base de datos | SQLite | 3.x |
| Librería VLM | google-genai | 2.8+ |
| Procesamiento imagen | Pillow | 12.x |
| HTTP client | httpx | 0.28+ |
| Frontend | HTML / CSS / JS | — |
| Variables de entorno | python-dotenv | 1.x |

---

## Instalación y uso

### Requisitos previos

- Python 3.11+
- [Ollama](https://ollama.com) instalado y corriendo con `llama3.2:3b`
- API Key de Gemini ([obtener aquí](https://aistudio.google.com))

### Instalación

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

# 3. Instala dependencias
pip install fastapi uvicorn google-genai pillow python-dotenv httpx

# 4. Crea el archivo .env en la raíz del proyecto
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

- **API docs**: `http://localhost:8000/docs`
- **Frontend**: abre `frontend/admin.html` con Live Server
- **Subir imagen manualmente**: `POST /vision/upload` con la imagen en el body
- **Detectar y actualizar inventario**: `POST /vision/detect`

---

## Estructura del proyecto

```
ProspectivaTecnologica/
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
    └── admin.html
```

---

*Proyecto desarrollado como parte del curso de Prospectiva de IA · IBERO Ciudad de México · 2026*
