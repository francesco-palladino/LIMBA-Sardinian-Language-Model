# Changelog

All notable changes to the LIMBA project and its public GitHub repository are documented in this file.

## Unreleased

### Planned

- Expand the Italian–Limba Sarda Comuna training dataset
- Introduce a held-out evaluation set
- Compare LIMBA outputs with the base model
- Add structured translation-quality assessment
- Improve linguistic consistency across model versions
- Extend regression testing
- Refine the retrieval-assisted generation workflow

## 2.0 — Public repository release

### Added

- Public documentation for the LIMBA language model
- Hugging Face model and interactive demo links
- Unsloth and LoRA training notebook
- GGUF local inference script
- Gradio application with conversational history
- Wikipedia-assisted retrieval
- Curated public dataset sample
- Dataset validation utility
- Automated dataset validation with GitHub Actions
- Training methodology documentation
- Qualitative evaluation framework
- Limitations and responsible-use documentation
- Example prompts
- Runtime and training dependency files
- Demo screenshot and visual project assets

### Model configuration

- Base model: Meta Llama 3.1 8B
- Fine-tuning framework: Unsloth
- Fine-tuning method: LoRA
- Context length: 4096 tokens
- LoRA rank: 32
- LoRA alpha: 64
- Training epochs: 3
- GGUF quantization: Q4_K_M
