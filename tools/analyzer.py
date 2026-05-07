import json
import requests

# OpenRouter API configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "poolside/laguna-m.1:free"
def analyze(text: str) -> dict:
    prompt = f"""
    Act as a senior Spring Boot architect.

    From this requirement:
    {text}

    Generate STRICT JSON:
    {{
      "entities": [
        {{
          "name": "User",
          "fields": [{{"name": "name", "type": "String"}}]
        }}
      ],
      "apis": [
        {{"endpoint": "/users", "method": "GET"}}
      ]
    }}
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Code Generator"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()

    content = response.json()['choices'][0]['message']['content']

    return json.loads(content)