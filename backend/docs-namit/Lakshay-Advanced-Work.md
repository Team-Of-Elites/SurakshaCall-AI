# Lakshay — Advanced Safety Intelligence & Identity Engineering Handbook

> **Project:** SurakshaCall AI — Privacy-First Scam Call Interceptor  
> **Role:** Owner of Fast Stage 1 Detection, Rules, ML Classifier, and Identity Governance  
> **Purpose of this Handbook:** Provide Lakshay with an advanced execution guide for low-latency text normalization, optimized ML inference on CPU, dataset scaling, and high-load streaming integration.

---

## 1. Advanced Multilingual Text Normalization & Code-Mixing

Whisper ASR models often produce phonetically matching spelling errors when transcribing Hindi spoken in Roman script (Hinglish) or mixed with English. 

### A. Core Hinglish Word Mappings
To ensure your regular expressions (`rules.py`) do not miss matches due to spelling variations, we use a mapping normalizer in `normalizer.py`:

```python
HINGLISH_CANONICAL_MAPS = {
    "otp": ["otp", "o t p", "one time password", "one-time password", "otpee"],
    "code": ["code", "cod", "six digit", "chhe digit", "ank", "digit", "six digit code"],
    "anydesk": ["anydesk", "any desk", "anidesk", "ani desk", "any-desk"],
    "teamviewer": ["teamviewer", "team viewer", "temviewer", "team-viewer"],
    "quicksupport": ["quicksupport", "quick support", "qsupport", "qs"],
    "rustdesk": ["rustdesk", "rust desk", "rust-desk"]
}
```

### B. Normalizer Pipeline Implementation
Always normalize multi-character punctuation, strip accents, lower-case, and map phonetics before sending text to the classifier:
```python
def advanced_normalize(text: str) -> str:
    # 1. Clean casing and punctuation
    text = text.lower().strip()
    # 2. Map Hinglish phonetics to canonical representation
    for canonical, variants in HINGLISH_CANONICAL_MAPS.items():
        for variant in variants:
            text = text.replace(variant, canonical)
    return text
```

---

## 2. ONNX Optimization for Fast CPU Classifier Inference

To maintain our real-time budget ($< 50\text{ ms}$ latency), we compile our multilingual SentenceTransformer model to **ONNX (Open Neural Network Exchange)** format. This speeds up CPU inference by **3x to 5x**.

### A. ONNX Conversion Steps
Run this script to export the Hugging Face SentenceTransformer model to ONNX:
```python
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

model_id = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
save_dir = "models/onnx_classifier"

# Load and export to ONNX
model = ORTModelForFeatureExtraction.from_pretrained(model_id, export=True)
tokenizer = AutoTokenizer.from_pretrained(model_id)

model.save_pretrained(save_dir)
tokenizer.save_pretrained(save_dir)
```

### B. Fast ONNX Inference Wrapper
Replace standard HuggingFace loader with ONNX runtime in `classifier.py`:
```python
import onnxruntime as ort
import numpy as np

class ONNXEmbeddingProvider:
    def __init__(self, model_dir: str):
        self.session = ort.InferenceSession(f"{model_dir}/model.onnx", providers=['CPUExecutionProvider'])
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)

    def get_embedding(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="np", padding=True, truncation=True)
        # Run ONNX inference
        outputs = self.session.run(None, dict(inputs))
        # Mean pooling of output embeddings
        return np.mean(outputs[0], axis=1)
```

---

## 3. Active Learning & Automatic Dataset Expansion

To expand the dataset from 210 dialogues to thousands of real-world call logs without manual labeling, we implement an **Active Learning Loop**:

```text
Incoming Call Transcript
       │
       ▼
 Stage 1 Classifier Prediction
       │
  ┌────┴───────────────────────────┐
  ▼ (High Confidence)              ▼ (Low Confidence: 0.35 - 0.65)
Silent Log (Auto-labeled)       Save to Review Pool
                                   │
                                   ▼
                             Manual Review
                                   │
                                   ▼
                             Append to JSONL & Retrain
```

### A. Uncertainty Sampling Rule
Flag turns where the classifier prediction probability $P$ is between $0.35$ and $0.65$:
```python
def is_uncertain(prediction_probabilities: dict) -> bool:
    for label, prob in prediction_probabilities.items():
        if 0.35 < prob < 0.65:
            return True
    return False
```
Save these flagged turns to `data/dialogues/review_pool.jsonl` for validation.

---

## 4. High-Load Live Audio Stream Testing

During live demos, transcripts arrive continuously as small sentence fragments. If the detector takes too long, it blocks the main event loop.

### A. Thread-Safe Async Detection Worker
Always wrap CPU-intensive ML embedding extraction in a background thread executor using `asyncio` to prevent UI lag on the dashboard:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

async def detect_async(raw_text: str):
    loop = asyncio.get_event_loop()
    # Run CPU embedding extraction in separate thread
    result = await loop.run_in_executor(executor, detect, raw_text)
    return result
```
