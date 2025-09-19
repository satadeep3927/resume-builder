#!/usr/bin/env python3
"""
Launch script for CV Enhancement Streamlit App
"""

import os
import subprocess
import sys
from pathlib import Path


def install_requirements():
    """Install required packages."""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True


def check_environment():
    """Check if environment is set up correctly."""
    print("🔍 Checking environment...")

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Copy .env.template to .env and configure it.")
        return False

    # Check if logo exists
    logo_file = Path("assets/brainium-logo.svg")
    if not logo_file.exists():
        print(
            f"⚠️  Logo not found at {logo_file}. The app will work but without the logo."
        )

    print("✅ Environment check completed!")
    return True


def launch_app():
    """Launch the Streamlit app."""
    print("🚀 Launching CV Enhancement App...")
    print("📱 App will open in your browser at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the app")

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "streamlit_app.py",
                "--server.port",
                "8501",
                "--server.address",
                "localhost",
            ]
        )
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Failed to launch app: {e}")


def main():
    """Main launch function."""
    print("🎯 CV Enhancement Agent Launcher")
    print("=" * 40)

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Install requirements
    if not install_requirements():
        return

    # Check environment
    if not check_environment():
        print("\n💡 Setup help:")
        print("1. Copy .env.template to .env")
        print("2. Add your COPILOT_ACCESS_TOKEN to .env")
        print("3. Ensure brainium-logo.svg is in assets/ folder")
        return

    # Launch app
    launch_app()


if __name__ == "__main__":
    main()
