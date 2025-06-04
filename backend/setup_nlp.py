"""
Setup script for downloading required NLP models
"""
import subprocess
import sys
import nltk
import os


def setup_spacy():
    """Download spaCy language model"""
    print("Downloading spaCy English language model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✅ spaCy model downloaded successfully!")
    except Exception as e:
        print(f"❌ Error downloading spaCy model: {e}")
        print("Please run manually: python -m spacy download en_core_web_sm")


def setup_nltk():
    """Download required NLTK data"""
    print("\nDownloading NLTK data...")
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')
        print("✅ NLTK data downloaded successfully!")
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")


def create_directories():
    """Create required directories"""
    directories = ['vector_db', 'logs', 'temp']
    
    print("\nCreating required directories...")
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")


def main():
    print("=== DevSensei NLP Setup ===\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Setup components
    setup_spacy()
    setup_nltk()
    create_directories()
    
    print("\n=== Setup Complete! ===")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and add your API keys:")
    print("   - GEMINI_API_KEY: Get from https://makersuite.google.com/app/apikey")
    print("   - GITHUB_TOKEN: Get from https://github.com/settings/tokens")
    print("\n2. Run the backend server:")
    print("   uvicorn main:app --reload")
    print("\n3. The API will be available at: http://localhost:8000")
    print("   API documentation: http://localhost:8000/docs")


if __name__ == "__main__":
    main() 