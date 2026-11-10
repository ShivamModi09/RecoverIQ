"""
RecoverIQ — Groq LLM Client
Pure Python Standard Library wrapper for Groq Cloud API.
Zero third-party package dependencies.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

DEFAULT_MODEL = "openai/gpt-oss-120b"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def _load_env_file() -> Dict[str, str]:
    """Lightweight .env file reader using Python Standard Library."""
    env_vars = {}
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        env_vars[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass
    return env_vars

class GroqClient:

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        env_from_file = _load_env_file()
        self.api_key = (
            api_key 
            or os.getenv("GROQ_API_KEY") 
            or env_from_file.get("GROQ_API_KEY", "")
        )
        self.model = model

    def chat_completion(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        json_mode: bool = False,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Sends chat completion request to Groq OpenAI-compatible endpoint.
        Returns parsed JSON or raw text response.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        req = urllib.request.Request(
            GROQ_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "RecoverIQ-Client/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                return {
                    "success": True,
                    "content": json.loads(content) if json_mode else content,
                    "model": data.get("model", self.model),
                    "usage": usage
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }

