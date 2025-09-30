from pathlib import Path

def read_prompt(prompt_path) -> str:
    """
    Loads prompt text from prompt.md. Raises a clear error if not found.
    """
    if not prompt_path.is_file():
        candidates = [
            prompt_path,
            Path.cwd() / "prompt.md",
            Path(__file__).resolve().parents[3] / "prompt.md",
        ]
        for c in candidates:
            if c.is_file():
                prompt_path = c
                break

    if not prompt_path.is_file():
        raise FileNotFoundError(
            f"prompt.md not found. Looked at: {prompt_path}"
        )

    return prompt_path.read_text(encoding="utf-8")
