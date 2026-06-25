import os
import json
import time
import uuid
from typing import Optional, Literal

import requests
import paho.mqtt.client as mqtt

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt.mecatronica-ibero.mx")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
CMD_TOPIC = os.getenv("CMD_TOPIC", "public/llm-led/cmd")

ALLOWED_ACTIONS = {"on", "off", "none"}

SYSTEM_PROMPT = """
Eres un clasificador de intención para controlar un LED conectado a un ESP32 por MQTT.

Tu tarea es decidir si el usuario quiere:
- "on": encender, prender o activar el LED.
- "off": apagar o desactivar el LED.
- "none": no hay una instrucción clara para cambiar el LED.

Reglas:
1. Responde únicamente JSON válido.
2. No escribas texto fuera del JSON.
3. Si el usuario pregunta algo general, responde action = "none".
4. Si el usuario dice "no enciendas", "no prendas" o algo equivalente, responde action = "none".
5. Si el usuario pide explícitamente apagar, responde action = "off".
6. Si el usuario pide explícitamente encender, responde action = "on".
7. confidence debe estar entre 0 y 1.

Formato obligatorio:
{
  "action": "on" | "off" | "none",
  "confidence": número entre 0 y 1,
  "reason": "explicación breve"
}
""".strip()

OLLAMA_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["on", "off", "none"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string"}
    },
    "required": ["action", "confidence", "reason"],
    "additionalProperties": False
}

app = FastAPI(title="LLM LED Agent Evaluation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LedAgentRequest(BaseModel):
    prompt: str
    expected_action: Optional[Literal["on", "off", "none"]] = None


class LedAgentResponse(BaseModel):
    request_id: str
    prompt: str
    expected_action: Optional[str]
    llm_action: Optional[str]
    confidence: Optional[float]
    reason: Optional[str]
    schema_valid: bool
    mqtt_published: bool
    architecture_success: bool
    api_elapsed_ms: float
    backend_elapsed_ms: float
    ollama_elapsed_ms: float
    mqtt_publish_ms: float
    prompt_eval_count: int
    eval_count: int
    total_tokens: int
    input_tokens_per_s: float
    output_tokens_per_s: float
    raw_llm_response: str
    error: Optional[str]


def now_ms() -> float:
    return time.perf_counter() * 1000


def wall_unix_ms() -> int:
    return int(time.time() * 1000)


def safe_float(value, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def validate_llm_json(raw_text: str):
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return False, None, "La respuesta del LLM no es JSON parseable."

    if not isinstance(data, dict):
        return False, None, "La respuesta JSON no es un objeto."

    required = {"action", "confidence", "reason"}
    missing = required - set(data.keys())

    if missing:
        return False, data, f"Faltan campos requeridos: {missing}"

    if data.get("action") not in ALLOWED_ACTIONS:
        return False, data, "El campo action no pertenece a on, off o none."

    confidence = data.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        return False, data, "El campo confidence debe ser numérico entre 0 y 1."

    if not isinstance(data.get("reason"), str):
        return False, data, "El campo reason debe ser texto."

    return True, data, None


def call_ollama(prompt: str):
    full_prompt = f"{SYSTEM_PROMPT}\n\nUsuario:\n{prompt}\n"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "format": OLLAMA_RESPONSE_SCHEMA,
        "options": {
            "temperature": 0.0,
            "top_p": 0.9,
            "num_predict": 120,
            "num_ctx": 2048,
            "repeat_penalty": 1.1
        }
    }

    start = now_ms()
    response = requests.post(OLLAMA_URL, json=payload, timeout=180)
    elapsed = now_ms() - start
    response.raise_for_status()

    data = response.json()
    raw_text = data.get("response", "").strip()

    metrics = {
        "ollama_elapsed_ms": elapsed,
        "prompt_eval_count": int(data.get("prompt_eval_count", 0) or 0),
        "eval_count": int(data.get("eval_count", 0) or 0),
        "prompt_eval_duration_ms": safe_float(data.get("prompt_eval_duration", 0)) / 1e6,
        "eval_duration_ms": safe_float(data.get("eval_duration", 0)) / 1e6,
    }

    prompt_duration_s = metrics["prompt_eval_duration_ms"] / 1000
    eval_duration_s = metrics["eval_duration_ms"] / 1000

    metrics["input_tokens_per_s"] = (
        metrics["prompt_eval_count"] / prompt_duration_s if prompt_duration_s > 0 else 0
    )
    metrics["output_tokens_per_s"] = (
        metrics["eval_count"] / eval_duration_s if eval_duration_s > 0 else 0
    )

    return raw_text, metrics


def publish_mqtt(payload: dict):
    start = now_ms()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=30)

    result = client.publish(CMD_TOPIC, json.dumps(payload), qos=0)
    result.wait_for_publish(timeout=5)

    client.disconnect()

    elapsed = now_ms() - start
    success = result.rc == mqtt.MQTT_ERR_SUCCESS

    return success, elapsed


@app.get("/")
def root():
    return {
        "service": "LLM LED Agent Evaluation",
        "endpoint": "/led-agent",
        "model": OLLAMA_MODEL,
        "mqtt_topic": CMD_TOPIC
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/led-agent", response_model=LedAgentResponse)
def led_agent(req: LedAgentRequest):
    request_id = str(uuid.uuid4())
    api_start = now_ms()
    error = None

    llm_action = None
    confidence = None
    reason = None
    schema_valid = False
    mqtt_published = False
    mqtt_publish_ms = 0.0

    prompt_eval_count = 0
    eval_count = 0
    input_tokens_per_s = 0.0
    output_tokens_per_s = 0.0
    raw_llm_response = ""
    ollama_metrics = {"ollama_elapsed_ms": 0.0}

    try:
        raw_llm_response, ollama_metrics = call_ollama(req.prompt)

        prompt_eval_count = ollama_metrics["prompt_eval_count"]
        eval_count = ollama_metrics["eval_count"]
        input_tokens_per_s = ollama_metrics["input_tokens_per_s"]
        output_tokens_per_s = ollama_metrics["output_tokens_per_s"]

        schema_valid, parsed, validation_error = validate_llm_json(raw_llm_response)

        if not schema_valid:
            error = validation_error

        if schema_valid and parsed:
            llm_action = parsed["action"]
            confidence = parsed["confidence"]
            reason = parsed["reason"]

            if llm_action in {"on", "off"}:
                mqtt_payload = {
                    "request_id": request_id,
                    "source": "llm_backend",
                    "device": "esp32_led_01",
                    "action": llm_action,
                    "value": 1 if llm_action == "on" else 0,
                    "confidence": confidence,
                    "reason": reason,
                    "sent_unix_ms": wall_unix_ms()
                }
                mqtt_published, mqtt_publish_ms = publish_mqtt(mqtt_payload)
            else:
                # none: no se publica MQTT pero se cuenta como éxito
                mqtt_published = True
                mqtt_publish_ms = 0.0

    except Exception as exc:
        error = str(exc)

    backend_elapsed_ms = now_ms() - api_start
    architecture_success = bool(schema_valid and mqtt_published)
    total_tokens = prompt_eval_count + eval_count

    return LedAgentResponse(
        request_id=request_id,
        prompt=req.prompt,
        expected_action=req.expected_action,
        llm_action=llm_action,
        confidence=confidence,
        reason=reason,
        schema_valid=schema_valid,
        mqtt_published=mqtt_published,
        architecture_success=architecture_success,
        api_elapsed_ms=backend_elapsed_ms,
        backend_elapsed_ms=backend_elapsed_ms,
        ollama_elapsed_ms=ollama_metrics.get("ollama_elapsed_ms", 0.0),
        mqtt_publish_ms=mqtt_publish_ms,
        prompt_eval_count=prompt_eval_count,
        eval_count=eval_count,
        total_tokens=total_tokens,
        input_tokens_per_s=input_tokens_per_s,
        output_tokens_per_s=output_tokens_per_s,
        raw_llm_response=raw_llm_response,
        error=error
    )
