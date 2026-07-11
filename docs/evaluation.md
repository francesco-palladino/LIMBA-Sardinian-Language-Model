# Model Evaluation

## Evaluation approach

LIMBA is currently evaluated through structured qualitative testing across translation, conversational interaction, text generation and educational assistance.

The evaluation process focuses on the model's behaviour after fine-tuning and on its ability to work consistently with Italian and Limba Sarda Comuna (LSC).

## Evaluation criteria

| Criterion | Description |
|---|---|
| Translation fidelity | Preservation of meaning, tone and relevant details |
| Linguistic consistency | Consistent use of Limba Sarda Comuna vocabulary and structures |
| Instruction following | Ability to complete the requested task without unnecessary additions |
| Factual accuracy | Correctness of informational and educational responses |
| Clarity | Readability and logical organization of the output |
| Completeness | Coverage of the relevant elements of the request |
| Conversational stability | Consistency across follow-up questions and repeated prompts |
| Hallucination control | Avoidance of unsupported or fabricated information |

## Test categories

The current qualitative test set includes:

- Italian → Limba Sarda Comuna translation;
- Limba Sarda Comuna → Italian translation;
- Sardinian text generation;
- general conversation;
- educational explanations;
- programming assistance;
- questions involving Sardinian language and culture;
- repeated prompts used to assess response stability.

## Retrieval-assisted responses

The Hugging Face Spaces application includes lightweight retrieval from Sardinian and Italian Wikipedia.

Responses involving retrieved information should be evaluated separately for:

- relevance of the retrieved page;
- correct use of the retrieved context;
- translation quality;
- factual consistency between the source context and the generated response.

## Current status

The repository currently documents a qualitative evaluation workflow rather than a formal benchmark.

Future evaluation work may include:

- a dedicated held-out test set;
- human review by LSC speakers;
- comparison with the base model;
- translation quality scoring;
- error categorization;
- regression testing across model versions;
- quantitative reporting of evaluation results.
