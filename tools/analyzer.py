import json
import re
import requests
from .mcp_server import get_spring_boot_context

try:
    import json5
except ImportError:
    json5 = None

# OpenRouter API configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "poolside/laguna-m.1:free"

def extract_json_from_response(content: str) -> dict:
    """Extract JSON from response, handling markdown code blocks and JSON5-like output."""
    # Try to parse as-is first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    if json5 is not None:
        try:
            return json5.loads(content)
        except Exception:
            pass
    
    # Try to extract from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        candidate = json_match.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            if json5 is not None:
                try:
                    return json5.loads(candidate)
                except Exception:
                    pass
    
    # Try to find JSON object/array directly
    json_match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
    if json_match:
        candidate = json_match.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            if json5 is not None:
                try:
                    return json5.loads(candidate)
                except Exception:
                    pass
    
    raise ValueError(
        "Could not extract valid JSON from response. "
        f"Response start: {content[:200]!r}"
    )

def analyze(text: str) -> dict:
    # Get enhanced context from MCP server
    try:
        from .mcp_server import get_spring_boot_context
        mcp_context = get_spring_boot_context(text)
        context_info = f"\nAdditional Context from MCP:\n{mcp_context}\n"
    except Exception as e:
        # Fallback if MCP server is not available
        context_info = "\nUsing standard Spring Boot best practices.\n"
    
    prompt = f"""
    Act as a senior Spring Boot architect.

    From this requirement:
    {text}
    
    {context_info}

    Respond with only valid JSON and nothing else.
    Do not include markdown, explanations, or extra text.
    Use double quotes for all keys and string values.
    The JSON output must exactly match this structure:
    {{
      "entities": [
        {{
          "name": "EntityName",
          "fields": [
            {{"name": "fieldName", "type": "String", "annotations": ["@NotBlank"]}}
          ]
        }}
      ],
      "apis": [
        {{"endpoint": "/example", "method": "GET"}}
      ]
    }}

    Generate STRICT JSON for the requirement above.
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Code Generator"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "top_p": 1.0,
        "max_tokens": 1200,
        "n": 1
    }

    if not text.strip():
        raise ValueError("Cannot generate JSON from empty requirement text.")

    response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()

    content = response.json()['choices'][0]['message']['content']
    
    return extract_json_from_response(content)