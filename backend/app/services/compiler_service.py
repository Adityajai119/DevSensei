import subprocess

def run_code(language: str, code: str):
    if language.lower() == 'python':
        try:
            result = subprocess.run(['python', '-c', code], capture_output=True, text=True, timeout=5)
            return result.stdout or result.stderr
        except Exception as e:
            return str(e)
    # TODO: Add support for other languages (C, C++, Java, etc.)
    return f"Running {language} code is not supported yet." 