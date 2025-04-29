# core/pipeline/generator.py
import os
import logging
import uuid
import base64
from typing import Dict, Any, Tuple, Optional

from core.memory.memory_manager import MemoryManager
from core.stub import Stub
from core.llm.ollama_llama import OllamaLlama
class CreativePipeline:
    """
    Manages the end-to-end pipeline of:
    1. Understanding and enhancing the user prompt with LLM
    2. Generating an image from text
    3. Converting the image to a 3D model
    4. Managing memory of created assets
    """
    
    def __init__(self, 
                stub: Stub, 
                memory_manager: MemoryManager,
                llm_client: OllamaLlama,
                text_to_image_app_id: str,
                image_to_3d_app_id: str,
                output_dir: str = "static/outputs"):
        """
        Initialize the creative pipeline.
        
        Args:
            stub: Stub instance for Openfabric API calls
            memory_manager: Memory manager instance
            llm_client: LLM client for prompt enhancement
            text_to_image_app_id: App ID for Text-to-Image service
            image_to_3d_app_id: App ID for Image-to-3D service
            output_dir: Directory for storing output files
        """
        self.stub = stub
        self.memory = memory_manager
        self.llm = llm_client
        self.text_to_image_app_id = text_to_image_app_id
        self.image_to_3d_app_id = image_to_3d_app_id
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "models"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "videos"), exist_ok=True)
    
    def process(self, user_prompt: str, user_id: str = "super-user") -> Dict[str, Any]:
        """
        Process a user prompt through the entire pipeline.
        
        Args:
            user_prompt: Original prompt from the user
            user_id: User identifier
            
        Returns:
            Dictionary containing results and paths to generated assets
        """
        try:
            result = {
                "stages_completed": [],
                "errors": [],
                "image_path": None,
                "model_path": None
            }   
            # Step 1: Enhance the prompt with LLM
            logging.info("Step 1: Enhancing prompt with LLM")
            # check local or docker
            if( self.is_running_in_docker()):
                enhanced_prompt = self.llm.enhance_prompt(user_prompt)
            else:
                enhanced_prompt = self.llm.enhance_prompt_local(user_prompt)
            
            logging.info("Step 2: Generating image from text")
            image_data = None
            try:
                image_data, image_path = self._generate_image(enhanced_prompt, user_id)
                result["image_path"] = image_path
                result["stages_completed"].append("image_generation")
            except Exception as e:
                logging.error(f"Error generating image: {e}")
                result["errors"].append(f"Image generation failed: {str(e)}")
                image_path = None
            
            # Stage 3: Convert image to 3D model (only if we have an image)
            if image_path:
                logging.info("Step 3: Converting image to 3D model")
                # In the process method, update how you handle the model_data return
                try:
                    video_path = None
                    model_data, model_path, video_path = self._generate_3d_model(image_path, user_id, image_data)
                    result["model_path"] = model_path
                    result["stages_completed"].append("model_generation")
                except Exception as e:
                    logging.error(f"Error generating 3D model: {e}")
                    result["errors"].append(f"3D model generation failed: {str(e)}")
                    
                    # Try fallback with correct return type handling
                    model_data = self._generate_3d_model2(image_data, user_id)
                    if model_data:
                        model_path = os.path.join(self.output_dir, "models", f"{uuid.uuid4().hex}.glb")
                        with open(model_path, 'wb') as f:
                            f.write(model_data)
                        result["model_path"] = model_path
                        result["stages_completed"].append("model_generation_fallback")
                    else:
                        model_path = None

            else:
                model_path = None
                result["errors"].append("Skipped 3D model generation due to missing image")
            
            # Stage 4: Save to memory 
            logging.info("Step 4: Saving creation to memory")
            tags = self._extract_tags(enhanced_prompt)
            if(video_path):
                creation_id = self.memory.save_creation(
                    user_prompt, 
                    enhanced_prompt, 
                    image_path, 
                    model_path,
                    video_path, 
                    tags,
                    user_id
                )
            else:
                creation_id = self.memory.save_creation(
                    user_prompt, 
                    enhanced_prompt, 
                    image_path, 
                    model_path,
                    tags,
                    user_id
                )
            
            # Save to short-term memory for session context
            self.memory.save_to_short_term("last_prompt", user_prompt)
            self.memory.save_to_short_term("last_enhanced_prompt", enhanced_prompt)
            self.memory.save_to_short_term("last_image_path", image_path)
            self.memory.save_to_short_term("last_model_path", model_path)
            
            result = {
                "creation_id": creation_id,
                "original_prompt": user_prompt,
                "enhanced_prompt": enhanced_prompt,
                "image_path": image_path,
                "model_path": model_path,
                "tags": tags
            }
            
            logging.info(f"Pipeline completed successfully: {creation_id}")
            return result
            
        except Exception as e:
            logging.error(f"Pipeline error: {e}")
            return {
                "error": str(e),
                "stage": "pipeline_process",
                "original_prompt": user_prompt
            }
    
    def _generate_image(self, prompt: str, user_id: str) -> Tuple[bytes, str]:
        """
        Generate an image from text using Openfabric Text-to-Image app.
        
        Args:
            prompt: Enhanced prompt for image generation
            user_id: User identifier
            
        Returns:
            Tuple of (image_data, image_path)
        """
        try:
            # Get input schema for the Text-to-Image app
            input_schema = self.stub.schema(self.text_to_image_app_id, 'input')
            logging.info(f"Text-to-Image input schema: {input_schema}")
            
            # Prepare the request based on the schema
            # Note: This would be adapted based on the actual schema of the app
            request = {
                "prompt": prompt,
                "negative_prompt": "blurry, distorted, low quality, draft",
                "width": 1024,
                "height": 1024,
                "guidance_scale": 7.5,
                "num_inference_steps": 50
            }
            
            # Call the Text-to-Image app
            response = self.stub.call(self.text_to_image_app_id, request, user_id)
            
            # Extract the image data
            # This would depend on the actual response structure
            image_data = response.get('result', None)
            if not image_data:
                raise ValueError("No image data in response")
                
            # Generate a unique filename
            filename = f"{uuid.uuid4().hex}.png"
            image_path = os.path.join(self.output_dir, "images", filename)
            
            # Save the image data to a file
            with open(image_path, 'wb') as f:
                f.write(image_data)
                
            logging.info(f"Image generated and saved to {image_path}")
            return image_data, image_path
            
        except Exception as e:
            logging.error(f"Error generating image: {e}")
            raise
    
    def _generate_3d_model(self, image_path: str, user_id: str, image_data) -> Tuple[bytes, str, Optional[str]]:
        try:
            # Base64 encode the image data
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            logging.info(f"Sending request to Image-to-3D service (App ID: {self.image_to_3d_app_id})")
            
            # Use the correct parameter name: 'input_image' instead of 'image'
            request = {
                "input_image": image_base64
            }
            
            # Call the Image-to-3D service
            response = self.stub.call(self.image_to_3d_app_id, request, user_id)
            
            if not response:
                raise ValueError("Empty response from Image-to-3D service")
                
            # Extract the model data from the correct field (based on output schema)
            model_data = response.get('generated_object')
            if not model_data:
                raise ValueError("No model data in response")
                    
            # Generate a unique filename and save
            id = uuid.uuid4().hex
            filename = f"{id}.glb"
            model_path = os.path.join(self.output_dir, "models", filename)

            with open(model_path, 'wb') as f:
                f.write(model_data)

            if(response['video_object']):
                video_data = response.get('video_object')
                video_path = os.path.join(self.output_dir, "videos", f"{id}.mp4")
                with open(video_path, 'wb') as f:
                    f.write(video_data)
                logging.info(f"Video generated and saved to {video_path}")
                return model_data, model_path, video_path
                
            logging.info(f"3D model generated and saved to {model_path}")
            return model_data, model_path, None
        
        except Exception as e:
            logging.error(f"Error generating 3D model: {e}")
            raise

    def _extract_tags(self, prompt: str) -> list:
        """
        Extract relevant tags from the prompt for memory indexing.
        
        Args:
            prompt: Enhanced prompt text
            
        Returns:
            List of tags extracted from the prompt
        """
        # Basic implementation - extract key nouns and adjectives
        # In a real implementation, this would use NLP or the LLM
        words = prompt.lower().replace(',', ' ').split()
        tags = []
        
        # Filter out common words and keep potential tags
        stopwords = {"a", "the", "and", "of", "for", "with", "in", "on", "at"}
        for word in words:
            if len(word) > 3 and word not in stopwords:
                tags.append(word)
                
        # Limit number of tags
        return list(set(tags))[:10]

    def _generate_3d_model2(self, image_data: bytes, user_id: str = 'super-user') -> Optional[bytes]:
        try:
            logging.info("Attempting fallback 3D model generation")
            
            # Base64 encode the image
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            # Use the correct parameter name: 'input_image'
            request_data = {"input_image": encoded_image}
            
            # Call the service
            response = self.stub.call(self.image_to_3d_app_id, request_data, user_id)
            
            if not response:
                logging.error("Empty response from fallback service")
                return None
                
            # Extract model data from the correct field
            model_data = response.get('generated_object')
            
            return model_data
            
        except Exception as e:
            logging.error(f"Fallback 3D model generation failed: {str(e)}")
            return None

    @staticmethod
    def is_running_in_docker():
        path_cgroup = '/proc/1/cgroup'
        if os.path.exists('/.dockerenv'):
            return True
        if os.path.isfile(path_cgroup):
            with open(path_cgroup, 'r') as f:
                return 'docker' in f.read() or 'containerd' in f.read()
        return False        
