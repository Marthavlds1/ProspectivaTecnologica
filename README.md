# Multi-Agent Architecture for Intelligent Pantry Management

Este repositorio contiene la arquitectura backend, documentación y el reporte técnico del sistema modular multi-agente para la gestión inteligente de inventarios de alimentos utilizando **Vision Language Models (VLMs)** y **Large Language Models (LLMs)**.

* **Reporte Técnico:** [Leer artículo en PDF](https://marthavlds1.github.io/ProspectivaTecnologica/assets/files/AlacenaInteligente.pdf)
* **Sitio del Proyecto:** [Ver Presentación y Observabilidad](https://marthavlds1.github.io/ProspectivaTecnologica/proyecto/)

---

## Resumen del Sistema

El proyecto resuelve el problema del desperdicio de alimentos mediante la separación arquitectónica entre percepción visual, procesamiento de lenguaje natural, ejecución determinista, persistencia y observabilidad operacional.

* **Percepción Visual Automática:** Procesamiento de imágenes capturadas con una ESP32-CAM utilizando **Gemini 2.0 Flash Vision** para registrar productos sin entrada manual.
* **Orquestación y Lenguaje:** Clasificación de intenciones y extracción de entidades en local con **Llama 3.2:3B** ejecutado vía **Ollama**.
* **Agentes Especializados:** Lógica determinista dividida en 5 agentes (Inventario, Recetas, Nutrición, Compras y Menú Semanal).
* **Interfaz Conversacional:** Integración para interacción de usuarios a través de **WhatsApp (WhatsApp Web.js)**.
* **Observabilidad Operacional:** Dashboard web en tiempo real para medir latencia end-to-end, tiempo de inferencia del LLM, rendimiento (tokens/s) y consumo de tokens (prompt vs. completion).

---

## Stack Tecnológico

* **Backend:** Python 3.12, FastAPI, Pydantic
* **Modelos de IA:** Llama 3.2:3B (Ollama), Gemini 2.0 Flash Vision API
* **Base de Datos:** SQLite 3
* **Integraciones:** WhatsApp Web.js, ESP32-CAM
* **Frontend y Dashboard:** HTML5, CSS3, JavaScript

---

## Arquitectura General

```
[ Usuario (WhatsApp / Dashboard) ]
                │
                ▼
      [ Backend (FastAPI) ]
                │
        ┌───────┴───────┐
        ▼               ▼
[ Orchestrator LLM ]  [ Vision Layer (Gemini) ]
 (Llama 3.2:3B)         (ESP32-CAM)
        │
        ▼
 [ Agent Router ] ──► [ Specialized Agents ] (Inventory, Recipe, Nutrition, Shopping, Menu)
                             │
                             ▼
                    [ SQLite & Observability ]

```

---

## Autores

* **Martha Esther Valdés Cruz**
* **Renata Darany Badillo Cabrera**
* **Marco Alfonso Rodriguez Calixto**

## Tutores
  
* **Huber Giron Nieto**
* **Joel Arango Ramirez**

*Departamento de Ingeniería Mecatrónica y Sistemas Ciberfísicos — Universidad Iberoamericana, Ciudad de México.*
