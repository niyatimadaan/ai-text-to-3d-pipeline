import logging
from typing import Dict

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub

from core.llm.deepseek_client import LocalPromptEnhancer
from core.memory.memory_manager import MemoryManager
from core.pipeline.generator import CreativePipeline
from core.llm.model_downloader import ModelDownloader
from core.llm.local_llm import LLMFactory
from core.llm.ollama_llama import OllamaLlama

# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf


############################################################
# Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """
    print(f"request recieved")
    logging.info(f"request recieved")

    # Retrieve input
    request: InputClass = model.request

    # Retrieve user config
    user_config: ConfigClass = configurations.get('super-user', None)
    logging.info(f"{configurations}")
    print(f"{configurations} recieved")

    # Initialize the Stub with app IDs
    app_ids = user_config.app_ids if user_config else []
    logging.info(f"App IDs: {app_ids}")
    stub = Stub(app_ids)

    # ------------------------------
    # TODO : add your magic here
    # ------------------------------
    global creative_pipeline, memory_manager, llm_client
    creative_pipeline = None
    memory_manager = None
    llm_client = None
    user_prompt = request.prompt
    response: OutputClass = model.response

    try:
        # Initialize memory manager and LLM client
        memory_manager = MemoryManager(db_path="memory.db")
        llm_client = OllamaLlama()

        # Execute internal logic
        response_message =  executeInternal(stub, app_ids, user_prompt)
        model.response = response_message
        # return

    except Exception as e:
        logging.error(f"Error during execution: {e}")
        model.response.message = f"Error occurred during processing: {str(e)}"
        # return


    # Prepare response
    
    # response.message = f"Echo: {request.prompt}"


def executeInternal(stub, app_ids, user_prompt) -> None:
    """
    Internal execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """
    global creative_pipeline, memory_manager, llm_client
    # Initialize pipeline if needed
    if creative_pipeline is None and memory_manager is not None and llm_client is not None:
        creative_pipeline = CreativePipeline(
            stub=stub,
            memory_manager=memory_manager,
            llm_client=llm_client,
            text_to_image_app_id=app_ids[0],
            image_to_3d_app_id=app_ids[1],
            output_dir="outputs"
        )
        logging.info("Creative pipeline initialized")
        
    # Process the request
    if creative_pipeline:
        # Check if this is a reference to previous creation
        # E.g., "Make something like the dragon I created last week"
        if "like" in user_prompt.lower() and any(word in user_prompt.lower() for word in ["last", "previous", "before"]):
            logging.info("Detected reference to previous creation")
            # Search for relevant previous creations
            search_terms = [word for word in user_prompt.split() if len(word) > 3]
            previous_creations = []
            for term in search_terms:
                results = memory_manager.search_creations(term)
                if results:
                    previous_creations.extend(results)
            
            # If found, include reference in the response
            if previous_creations:
                reference = previous_creations[0]
                response_message = f"I found a previous creation similar to what you're asking for. Using '{reference['prompt']}' as reference."
                # You might modify the prompt here to include reference to previous creation
            else:
                response_message = "I couldn't find any previous creations matching your request. Creating something new!"
        else:
            response_message = "Processing your creative request..."
            
        # Run the creative pipeline
        result = creative_pipeline.process(user_prompt, 'super-user')
        
        # Update response message with results
        if "error" in result:
            response_message = f"Error: {result['error']}"
        else:
            response_message = f"""
            Successfully created your vision!
            
            Original prompt: "{user_prompt}"
            Enhanced prompt: "{result['enhanced_prompt']}"
            
            Generated image saved to: {result['image_path']}
            Generated 3D model saved to: {result['model_path']}
            
            Creation ID: {result['creation_id']} (saved to memory for future reference)
            """
    else:
        response_message = "Error: Creative pipeline not initialized properly."
        
    return response_message