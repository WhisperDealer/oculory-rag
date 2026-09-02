#!/usr/bin/env python3
"""embed.py -- the local embedding model, loaded lazily.

BAAI/bge-small-en-v1.5 through fastembed: 384 dimensions, ONNX on CPU, no API key and
no network once the model is cached. The whole corpus is ~2000 chunks, so brute-force
cosine over a numpy matrix is faster than any approximate index would be.

Loading onnxruntime costs a couple of seconds, and this module is imported by an MCP
server that starts in every Claude Code session, so nothing heavy happens at import:
the model is built on first use. If fastembed is missing or fails to load, available()
returns False and the callers fall back to lexical-only retrieval.
"""
from __future__ import annotations

import sys
from pathlib import Path

MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBED_DIM = 384
CACHE_DIR = Path(__file__).resolve().parent / "index" / "models"

_model = None
_failed: str | None = None


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def get_model():
    """Build the model on first call. Returns None when the stack is unavailable."""
    global _model, _failed
    if _model is not None or _failed is not None:
        return _model
    try:
        from fastembed import TextEmbedding
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _model = TextEmbedding(model_name=MODEL_NAME, cache_dir=str(CACHE_DIR))
    except Exception as exc:                       # noqa: BLE001 - degrade, never crash
        _failed = f"{type(exc).__name__}: {exc}"
        log(f"WARNING: embeddings unavailable ({_failed}); falling back to lexical search")
    return _model


def available() -> bool:
    return get_model() is not None


def failure() -> str | None:
    return _failed


def embed_passages(texts: list[str], batch_size: int = 32):
    """Document-side vectors, L2-normalised so cosine is a dot product."""
    import numpy as np
    model = get_model()
    if model is None:
        return np.zeros((0, EMBED_DIM), dtype="float32")
    vecs = np.asarray(list(model.embed(texts, batch_size=batch_size)), dtype="float32")
    return _normalise(vecs)


def embed_query(text: str):
    """Query-side vector. bge wants its retrieval prefix, which query_embed applies."""
    import numpy as np
    model = get_model()
    if model is None:
        return None
    vec = np.asarray(next(iter(model.query_embed([text]))), dtype="float32")
    return _normalise(vec.reshape(1, -1))[0]


def _normalise(mat):
    import numpy as np
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.maximum(norms, 1e-12)
