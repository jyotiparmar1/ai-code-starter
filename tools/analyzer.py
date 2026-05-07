import json
import re
import requests

# OpenRouter API configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "poolside/laguna-m.1:free"

def extract_json_from_response(content: str) -> dict:
    """Extract JSON from response, handling markdown code blocks."""
    # Try to parse as-is first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # Try to extract from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object/array directly
    json_match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # If all attempts fail, raise error with helpful info
    raise ValueError(f"Could not extract valid JSON from response. Content: {content[:200]}")

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

    if not text.strip():
        raise ValueError("Cannot generate JSON from empty requirement text.")

    response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()

    content = response.json()['choices'][0]['message']['content']
    
    return extract_json_from_response(content)