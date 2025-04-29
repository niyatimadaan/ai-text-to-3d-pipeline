# 3D Creation Pipeline - AI-Powered Text to 3D Model Generator

This application transforms text descriptions into beautiful 3D models using AI. The pipeline enhances prompts with a local LLM, generates images, and converts them to 3D models while maintaining memory of all creations.

![3D Creation Pipeline](https://example.com/screenshot.png)

## 🚀 Features

- **Text-to-3D Generation**: Turn your creative text prompts into 3D models
- **LLM Prompt Enhancement**: Local LLM improves your descriptions for better visual results
- **History Management**: Browse and revisit your previous creations
- **Interactive UI**: User-friendly Streamlit interface for easy interaction
- **Memory System**: Both short-term (session) and long-term (database) memory

## 🛠️ System Architecture

```
User Prompt → Local LLM Enhancement → Text-to-Image Generation → Image-to-3D Conversion → Memory Storage
```

The system uses:
- **Local LLM** (OllamaLlama) for prompt enhancement
- **Openfabric Apps** for Text-to-Image and Image-to-3D conversion
- **SQLite Database** for long-term memory storage
- **Streamlit UI** for user interaction

## 📋 Requirements

- Python 3.8+
- poetry
- Openfabric SDK
- Streamlit

## 🏃‍♂️ Installation & Setup

### Setup with Poetry
```bash
cd app
python3 -m venv venv
poetry install
pip install openfabric_pysdk-0.3.0-py3-none-any.whl
pip uninstall python-magic
pip install python-magic-bin
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Unix/MacOS
```

## 🚀 Running the Application

```bash
python launch_app.py
```

[Watch demo video](app/static/Openfabric AI.mp4)

Open your browser and navigate to: http://localhost:8501

## 💾 Memory System

The application uses a two-tier memory system:

1. **Short-Term Memory**: Maintains context during a session
   - Last prompt used
   - Last image generated
   - Last 3D model created

2. **Long-Term Memory**: SQLite database that stores:
   - Original prompts
   - Enhanced prompts
   - Image paths
   - 3D model paths
   - Generated tags

This allows the application to reference past creations and maintain context across sessions.

## 🖼️ Example Usage

1. Enter a creative prompt like "A glowing dragon standing on a cliff at sunset"
2. Click "Generate 3D Creation"
3. Wait while the system:
   - Enhances your prompt with the LLM
   - Generates an image
   - Converts the image to a 3D model
4. View and download your 3D model
5. Browse previous creations in the sidebar

## 🔧 Troubleshooting

- **3D Model Viewer Issues**: If the 3D model doesn't display correctly, use the download button to view the model in a dedicated 3D viewer application.
- **Image Generation Fails**: Ensure your prompt is descriptive but not excessively long.
- **App Initialization Errors**: Check that the Openfabric services are properly configured and accessible.

## 📦 Project Structure

```
app/
├── app.py                     # Streamlit UI application
├── launch_app.py              # Application launcher
├── main.py                    # Main backend logic
├── core/
│   ├── llm/                   # LLM integration
│   │   └── ollama_llama.py    # Local LLM client
│   ├── memory/                # Memory system
│   │   └── memory_manager.py  # Memory management
│   ├── pipeline/              # Creative pipeline
│   │   └── generator.py       # Main generation pipeline
│   └── stub.py                # Openfabric API stub
├── outputs/                   # Generated outputs
│   ├── images/                # Generated images
│   └── models/                # Generated 3D models
└── memory.db                  # SQLite database for long-term memory
```

## ✨ Future Enhancements

- Voice-to-text interaction
- FAISS/ChromaDB for semantic similarity search
- Advanced 3D model viewer with interactive controls
- Batch processing of multiple prompts
- Style transfer and customization options
