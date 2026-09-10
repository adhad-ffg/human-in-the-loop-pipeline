# Human-in-the-Loop LLM Pipeline

A command-line tool for semi-automated LLM pipelines where humans can review each step. It supports OpenAI and Google GenAI, and lets you review, approve, and revise model output before using it as context for the next step.

## Features

- Multi-step LLM pipelines with human-in-the-loop review
- Supports OpenAI and Google GenAI
- Approve, edit, or quit at each step
- Preserves context between steps
- Configurable via environment variables
- Simple CLI interface

## Requirements

- Python 3.7 or higher
- `openai` package if using OpenAI
- `google-genai` package if using Google GenAI
- API key for the selected provider

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/adhad-ffg/human-in-the-loop-pipeline.git
   cd human-in-the-loop-pipeline
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Or install only the package for the provider you use:

   ```bash
   pip install openai
   # or
   pip install google-genai
   ```

## Configuration

Create a `.env` file or export environment variables.

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `openai` or `google` | `openai` |
| `LLM_MODEL` | Model name | `gpt-4o-mini` (OpenAI) / `gemini-1.5-flash` (Google) |
| `OPENAI_API_KEY` | OpenAI API key | Required if provider is `openai` |
| `GOOGLE_API_KEY` | Google API key | Required if provider is `google` |

Example `.env`:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key_here
```

Or export them in the shell:

```bash
export LLM_PROVIDER=google
export GOOGLE_API_KEY=your_google_api_key
```

## Usage

Run the script:

```bash
python3 hitlp.py
```

At each step, the LLM generates output. You are prompted to enter one of the following:

- `[y]` approve the output and continue
- `[e]` edit: enter feedback to revise the output
- `[q]` quit the pipeline

Approved output is added to the persistent context and used in subsequent steps.

## Pipeline Steps

The default pipeline consists of the following three steps:

1. “Generate a tweet” – Write a short, engaging tweet about the importance of human oversight in AI systems.
2. “Expand into a LinkedIn post” – Use the tweet as a hint to expand it into a professional LinkedIn post of about 150 words.
3. “Create summary bullet points” – Extract the three most important points from the LinkedIn post as bullet points.

To customize the pipeline, edit the `PIPELINE_STEPS` list in `hitlp.py`.

## Example Run

```bash
$ python3 hitlp.py
Starting Human-in-the-loop LLM Pipeline
Provider: openai
Model: gpt-4o-mini
Number of steps: 3

============================================================
Executing: Step 1: Generate a tweet
============================================================

--- LLM Output ---
Human oversight is essential for AI. Without it, we risk...
------------------

[y] approve / [e] edit / [q] quit: y

Step approved and added to context.
...
```

## License

This project is licensed under the terms of the LICENSE file included in the repository.
