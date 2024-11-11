import requests

def query_ollama(prompt: str, model: str = "llama2", host: str = "http://127.0.0.1:11434") -> str:
    """
    Sends a prompt to the locally hosted Ollama instance and returns the response.

    Args:
        prompt (str): The prompt to send to the Ollama API.
        model (str): The model to use (e.g., 'llama2', 'gpt4all'). Default is 'llama2'.
        host (str): The URL of the locally hosted Ollama API. Default is 'http://127.0.0.1:11434'.

    Returns:
        str: The response text from the Ollama API.
    """
    url = f"{host}/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3",
        "prompt": "What is python. Response in JSON format",
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        print(data)
        return data.get("text", "No response text received.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {e}"

# Example usage
if __name__ == "__main__":
    response = query_ollama(prompt="Hello, how are you?", model="llama2")
    print("Response from Ollama:", response)
