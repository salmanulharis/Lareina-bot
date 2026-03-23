import requests

# Change this to your Ollama server URL if needed
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ask_ollama(prompt, model="llama3"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "[No response from Ollama]")
