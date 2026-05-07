import json
import openai

openai.api_key = "YOUR_API_KEY"

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

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response['choices'][0]['message']['content']

    return json.loads(content)