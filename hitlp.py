import os
import sys
from typing import List, Dict, Optional

PIPELINE_STEPS: List[Dict[str, str]] = [
    {
        "name": "Step 1: Generate a tweet",
        "prompt": "Write a short, engaging tweet about the importance of human oversight in AI systems."
    },
    {
        "name": "Step 2: Expand to a LinkedIn post",
        "prompt": "Using the tweet as inspiration, expand it into a professional LinkedIn post of about 150 words."
    },
    {
        "name": "Step 3: Create a summary bullet list",
        "prompt": "From the LinkedIn post, extract the three most important points as a bullet list."
    },
]

SYSTEM_PROMPT = "You are a helpful assistant that writes high-quality content. You will receive feedback and revise accordingly."
TEMPERATURE = 0.7

def get_provider() -> str:
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    if provider not in ("openai", "google"):
        sys.exit("Error: LLM_PROVIDER must be 'openai' or 'google'.")
    return provider

def get_model_name(provider: str) -> str:
    if provider == "openai":
        return os.environ.get("LLM_MODEL", "gpt-4o-mini")
    else:
        return os.environ.get("LLM_MODEL", "gemini-1.5-flash")

def get_client(provider: str):
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            sys.exit("Error: OPENAI_API_KEY environment variable is not set.")
        try:
            from openai import OpenAI
            return OpenAI(api_key=api_key)
        except ImportError:
            sys.exit("Error: 'openai' package is required. Install with: pip install openai")
    else:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            sys.exit("Error: GOOGLE_API_KEY environment variable is not set.")
        try:
            from google import genai
            return genai.Client(api_key=api_key)
        except ImportError:
            sys.exit("Error: 'google-genai' package is required. Install with: pip install google-genai")

def call_openai(client, messages: List[Dict[str, str]], model: str) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {e}")

def call_google(client, messages: List[Dict[str, str]], model: str) -> str:
    system_instruction = ""
    contents = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            system_instruction += content + "\n"
        elif role == "user":
            contents.append({"role": "user", "parts": [content]})
        elif role == "assistant":
            contents.append({"role": "model", "parts": [content]})
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config={
                "system_instruction": system_instruction.strip(),
                "temperature": TEMPERATURE,
            }
        )
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Google API call failed: {e}")

def call_llm(provider: str, client, messages: List[Dict[str, str]], model: str) -> str:
    if provider == "openai":
        return call_openai(client, messages, model)
    else:
        return call_google(client, messages, model)

def run_step_with_human_loop(
    provider: str,
    client,
    model: str,
    step_name: str,
    step_prompt: str,
    permanent_context: List[Dict[str, str]],
) -> Optional[str]:
    working_messages: List[Dict[str, str]] = [
        {"role": "user", "content": step_prompt}
    ]

    print(f"\n{'='*60}")
    print(f"Executing: {step_name}")
    print(f"{'='*60}")

    while True:
        messages = []
        if SYSTEM_PROMPT:
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.extend(permanent_context)
        messages.extend(working_messages)

        try:
            assistant_output = call_llm(provider, client, messages, model)
        except RuntimeError as e:
            print(f"\nError during LLM call: {e}")
            choice = input("Retry? [y/n]: ").strip().lower()
            if choice == 'y':
                continue
            else:
                return None

        print("\n--- LLM Output ---")
        print(assistant_output)
        print("------------------\n")

        while True:
            user_input = input("[y] approve / [e] edit / [q] quit: ").strip().lower()
            if user_input in ('y', 'e', 'q'):
                break
            else:
                print("Invalid input. Please enter 'y', 'e', or 'q'.")

        if user_input == 'y':
            permanent_context.append({"role": "user", "content": step_prompt})
            permanent_context.append({"role": "assistant", "content": assistant_output})
            return assistant_output

        elif user_input == 'e':
            edit_instruction = input("Enter your edit instruction: ").strip()
            if not edit_instruction:
                print("Empty instruction ignored. Please provide feedback.")
                continue
            working_messages.append({"role": "assistant", "content": assistant_output})
            working_messages.append({"role": "user", "content": f"Revise the previous output according to this feedback: {edit_instruction}"})
            print("\nRevising based on your feedback...\n")

        else:
            print("\nQuitting as requested.")
            return None

def main():
    provider = get_provider()
    client = get_client(provider)
    model = get_model_name(provider)

    print("Starting Human-in-the-loop LLM Pipeline")
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print(f"Number of steps: {len(PIPELINE_STEPS)}")

    permanent_context: List[Dict[str, str]] = []

    for step in PIPELINE_STEPS:
        step_name = step["name"]
        step_prompt = step["prompt"]
        result = run_step_with_human_loop(provider, client, model, step_name, step_prompt, permanent_context)
        if result is None:
            print("\nPipeline terminated early.")
            sys.exit(0)
        else:
            print(f"\nStep approved and added to context.")

    print("\nAll steps completed successfully!")

if __name__ == "__main__":
    main()
