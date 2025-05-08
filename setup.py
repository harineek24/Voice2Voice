#!/usr/bin/env python3
"""
Simple setup script for the voice-to-voice application
"""
import os
import shutil
import subprocess
import platform

def main():
    print("Setting up the Voice-to-Voice application...")
    
    # Check if virtual environment exists
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run(["python", "-m", "venv", "venv"])
    
    # Activate virtual environment and install requirements
    print("Installing dependencies...")
    
    if platform.system() == "Windows":
        pip_path = os.path.join("venv", "Scripts", "pip")
        python_path = os.path.join("venv", "Scripts", "python")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")
    
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("Creating .env file...")
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("Please edit the .env file to add your OpenAI API key.")
        else:
            with open(".env", "w") as f:
                f.write("# OpenAI API Key\nOPENAI_API_KEY=your_openai_api_key_here\n")
            print("Created .env file. Please add your OpenAI API key.")
    
    print("\nSetup complete!")
    print("\nTo run the application:")
    if platform.system() == "Windows":
        print("1. Run: .\\venv\\Scripts\\python app.py")
    else:
        print("1. Run: ./venv/bin/python app.py")
    print("2. Open your browser to: http://localhost:8000")

if __name__ == "__main__":
    main()