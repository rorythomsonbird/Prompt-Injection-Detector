from transformers import pipeline
import torch


MODEL_ID = "protectai/deberta-v3-base-prompt-injection-v2"


class PromptInjectionDetector:
    def __init__(self):
        print("Loading model... (first run will download ~400MB)")
        device = -1
        self.classifier = pipeline(
            "text-classification",
            model=MODEL_ID,
            device=device,
            truncation=True,
            max_length=512,
        )
        print("Model ready.")

    def analyze(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "verdict": "empty",
                "label": "N/A",
                "confidence": 0.0,
                "message": "No input provided.",
            }

        result = self.classifier(text.strip())[0]
        label = result["label"]  # "INJECTION" or "LEGITIMATE"
        score = round(result["score"] * 100, 1)
        is_injection = label == "INJECTION"

        return {
            "verdict": "injection" if is_injection else "safe",
            "label": label,
            "confidence": score,
            "message": self._message(is_injection, result["score"]),
        }

    def _message(self, is_injection: bool, score: float) -> str:
        if is_injection:
            if score >= 0.95:
                return "High confidence prompt injection attempt detected."
            elif score >= 0.75:
                return "This looks like a prompt injection attempt."
            else:
                return "Possible injection — lower confidence, worth reviewing."
        else:
            if score >= 0.95:
                return "Input looks clean."
            elif score >= 0.75:
                return "Probably safe, but confidence is moderate."
            else:
                return "Classified as safe — confidence is lower than usual."
