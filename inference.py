"""
Local command-line inference for LIMBA 2.0.

The script downloads the quantized GGUF model from Hugging Face Hub
and runs inference locally through llama.cpp.

Example:
    python inference.py --prompt "Traduci in sardo: La tecnologia può aiutare la scuola."
"""

import argparse
import os
from typing import Final

from huggingface_hub import hf_hub_download
from llama_cpp import Llama


REPO_ID: Final[str] = "FPll/limba-mentor-llama3-gguf"
MODEL_FILENAME: Final[str] = "Meta-Llama-3.1-8B.Q4_K_M.gguf"

SYSTEM_PROMPT: Final[str] = (
    "Sei LIMBA 2.0, un assistente linguistico basato su Llama 3.1. "
    "Parli italiano e Limba Sarda Comuna (LSC). "
    "Puoi conversare, generare testi e tradurre tra italiano e sardo. "
    "Segui accuratamente le istruzioni dell'utente e non aggiungere "
    "informazioni non richieste nelle traduzioni."
)


def build_prompt(user_prompt: str) -> str:
    """Format the request using the Llama 3.1 chat template."""

    return (
        "<|start_header_id|>system<|end_header_id|>\n\n"
        f"{SYSTEM_PROMPT}<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )


def load_model(context_length: int, threads: int) -> Llama:
    """Download and initialize the GGUF model."""

    model_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=MODEL_FILENAME,
        token=os.environ.get("HF_TOKEN"),
    )

    return Llama(
        model_path=model_path,
        n_ctx=context_length,
        n_threads=threads,
        verbose=False,
    )


def generate_response(
    model: Llama,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
) -> str:
    """Generate a response from LIMBA."""

    result = model(
        build_prompt(user_prompt),
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=0.9,
        repeat_penalty=1.15,
        stop=[
            "<|eot_id|>",
            "<|start_header_id|>",
            "<|end_header_id|>",
        ],
    )

    return result["choices"][0]["text"].strip()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local inference with LIMBA 2.0."
    )

    parser.add_argument(
        "--prompt",
        required=True,
        help="Instruction or question to send to LIMBA.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=512,
        help="Maximum number of generated tokens.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Sampling temperature.",
    )
    parser.add_argument(
        "--context-length",
        type=int,
        default=4096,
        help="Context-window size.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=max(1, (os.cpu_count() or 2) // 2),
        help="Number of CPU threads used by llama.cpp.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    try:
        model = load_model(args.context_length, args.threads)
        response = generate_response(
            model=model,
            user_prompt=args.prompt,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
        print(response)

    except Exception as exc:
        raise SystemExit(f"Unable to run LIMBA: {exc}") from exc


if __name__ == "__main__":
    main()
