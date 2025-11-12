from pathlib import Path

def read_prompt(prompt_path) -> str:
    """
    Loads prompt text from the specified path. Raises a clear error if not found.
    """
    if not prompt_path.is_file():
        candidates = [
            prompt_path,
            Path.cwd() / "prompts" / prompt_path.name,
            Path(__file__).resolve().parents[3] / "prompts" / prompt_path.name,
        ]
        for c in candidates:
            if c.is_file():
                prompt_path = c
                break

    if not prompt_path.is_file():
        raise FileNotFoundError(
            f"Prompt file not found. Looked at: {prompt_path}"
        )

    return prompt_path.read_text(encoding="utf-8")
