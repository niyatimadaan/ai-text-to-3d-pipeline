import streamlit as st
import os
import base64
from pathlib import Path
import logging
import time
from typing import Dict, List, Optional

# Import the needed components from our application
from core.stub import Stub
from core.memory.memory_manager import MemoryManager
from core.pipeline.generator import CreativePipeline
from core.llm.ollama_llama import OllamaLlama

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="3D Creation Pipeline",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .creation-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .model-viewer {
        width: 100%;
        height: 400px;
        border: none;
    }
    .prompt-box {
        background-color: #f9f9f9;
        border-left: 3px solid #4CAF50;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline_initialized' not in st.session_state:
    st.session_state.pipeline_initialized = False
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'current_model' not in st.session_state:
    st.session_state.current_model = None

# Function to initialize the pipeline
@st.cache_resource
def initialize_pipeline():
    try:
        # App IDs for the services
        app_ids = [
            "c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network",  # Text-to-Image
            "f0b5f319156c4819b9827000b17e511a.node3.openfabric.network"   # Image-to-3D
        ]
        
        # Initialize the stub with app IDs
        stub = Stub(app_ids)
        
        # Initialize memory manager
        memory_manager = MemoryManager(db_path="memory.db")
        
        # Initialize LLM client
        llm_client = OllamaLlama()
        
        # Create the creative pipeline
        pipeline = CreativePipeline(
            stub=stub,
            memory_manager=memory_manager,
            llm_client=llm_client,
            text_to_image_app_id=app_ids[0],
            image_to_3d_app_id=app_ids[1],
            output_dir="outputs"
        )
        
        logger.info("Pipeline initialized successfully")
        return pipeline, memory_manager
    except Exception as e:
        logger.error(f"Error initializing pipeline: {e}")
        st.error(f"Failed to initialize pipeline: {str(e)}")
        return None, None

# Function to display image
def display_image(image_path):
    if image_path and os.path.exists(image_path):
        st.image(image_path, caption="Generated Image", use_container_width=True)
    else:
        st.warning("Image not available")

# Function to display 3D model
def display_model(model_path):
    if model_path and os.path.exists(model_path):
        # Create an iframe with the 3D viewer (Not working)
        # link = f"https://modelviewer.dev/share/viewer.html?src=http://localhost:8501/{model_path}"
        # model_url = f"http://localhost:8501/{model_path.replace(os.sep, '/')}"
        # model_url2 = model_path.replace(os.sep, '/')
        # logging.info(f"Model URL: {model_url}, {link}")
        # html = f"""
        # <div class="model-viewer">
        # <model-viewer src="{model_url}" alt="3D model" auto-rotate camera-controls background-color="#ffffff" style="width: 100%; height: 500px;"></model-viewer>
        # <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        # </div>
        # """
        # st.markdown(html, unsafe_allow_html=True)

        # Add download button
        with open(model_path, "rb") as file:
            model_bytes = file.read()
            model_base64 = base64.b64encode(model_bytes).decode()
            
        download_link = f'<a href="data:application/octet-stream;base64,{model_base64}" download="{os.path.basename(model_path)}" target="_blank">Download 3D Model</a>'
        st.markdown(download_link, unsafe_allow_html=True)
    else:
        st.warning("3D model not available")

# Function to load history from memory
def load_history(memory_manager, limit=5):
    try:
        creations = memory_manager.get_all_creations(limit=limit)
        return creations
    except Exception as e:
        logger.error(f"Error loading history: {e}")
        return []

# Title and description
st.title("🎨 3D Creation Pipeline")
st.markdown("""
Transform your text descriptions into beautiful 3D models with AI. 
Just type your idea, and watch as it becomes a 3D reality!
""")

# Initialize pipeline
if not st.session_state.pipeline_initialized:
    with st.spinner("Initializing AI pipeline..."):
        pipeline, memory_manager = initialize_pipeline()
        if pipeline and memory_manager:
            st.session_state.pipeline_initialized = True
            st.session_state.pipeline = pipeline
            st.session_state.memory_manager = memory_manager
            # Load initial history
            st.session_state.generation_history = load_history(memory_manager)
            st.success("AI pipeline initialized!")
        else:
            st.error("Failed to initialize AI pipeline")

# Only show the main interface if pipeline is initialized
if st.session_state.pipeline_initialized:
    # Sidebar with history
    with st.sidebar:
        st.header("Generation History")
        if st.button("Refresh History"):
            st.session_state.generation_history = load_history(st.session_state.memory_manager)
        
        for idx, creation in enumerate(st.session_state.generation_history):
            with st.expander(f"{idx+1}. {creation['prompt'][:30]}..."):
                st.write(f"**Original Prompt:** {creation['prompt']}")
                st.write(f"**Enhanced Prompt:** {creation['enhanced_prompt'][:100]}...")
                
                # Add buttons to load this creation
                if st.button(f"Load Creation #{idx+1}", key=f"load_{idx}"):
                    st.session_state.current_image = creation['image_path']
                    st.session_state.current_model = creation['model_path']
                    st.rerun()
    
    # Main content area
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.header("Generate New Creation")
        
        # Text input for prompt
        prompt = st.text_area("Enter your creative idea", 
                              placeholder="E.g., A majestic dragon perched on a mountain, scales glistening in the sunlight",
                              height=100)
        
        # Generate button
        if st.button("🚀 Generate 3D Creation", type="primary"):
            if not prompt:
                st.warning("Please enter a prompt first")
            else:
                with st.spinner("Working on your creation... This may take a few minutes"):
                    try:
                        # Run the pipeline
                        result = st.session_state.pipeline.process(prompt, 'super-user')
                        
                        if "error" in result:
                            st.error(f"Generation failed: {result['error']}")
                        else:
                            # Update current image and model
                            st.session_state.current_image = result['image_path']
                            st.session_state.current_model = result['model_path'] 
                            
                            # Add to history at the beginning
                            st.session_state.generation_history = load_history(st.session_state.memory_manager)
                            
                            st.success("Creation completed successfully!")
                            
                            # Display enhanced prompt
                            st.subheader("Enhanced Prompt")
                            st.markdown(f"""<div class="prompt-box">{result['enhanced_prompt']}</div>""", unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"Error during generation: {str(e)}")
    
    with col2:
        st.header("Current Creation")
        
        # Display image if available
        if st.session_state.current_image:
            display_image(st.session_state.current_image)
        
        # Display 3D model if available
        if st.session_state.current_model:
            st.subheader("3D Model")
            display_model(st.session_state.current_model)
            
        if not st.session_state.current_image and not st.session_state.current_model:
            st.info("Generate a new creation or select one from history to view")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit + AI 🤖")
