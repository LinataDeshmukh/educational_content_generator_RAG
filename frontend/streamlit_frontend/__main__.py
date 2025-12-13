"""Entry point for running the frontend server."""

import subprocess
import sys
from pathlib import Path


def main():
    """Main entry point for frontend server."""
    main_py = Path(__file__).parent / "main.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(main_py)], check=False)


if __name__ == "__main__":
    main()

