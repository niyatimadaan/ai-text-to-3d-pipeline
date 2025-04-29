import requests
import logging

class OllamaLlama:
# URL of the Ollama API
    def enhance_prompt(self, user_prompt: str) -> None:
        url = "http://host.docker.internal:11434/api/generate"

        # Define the payload
        payload = {
            "model": "llama2",
            "prompt": f"""
                    You are an artistic prompt enhancer. Your job is to take simple user requests and transform them 
                    into detailed, vivid descriptions for image and 3D generation. Include artistic style, lighting, 
                    mood, colors, perspective, and detailed elements. Make it specific and visual but keep the core 
                    idea intact. Format your response as a rich text description without any explanations or additional 
                    content in maximum 200 words.

                    Transform this prompt for image generation: 
                    User Request: {user_prompt}

                    Include every detail of user request in the response. 
                """,
            "stream": False 
        }

        # Send a POST request to the Ollama API
        response = requests.post(url, json=payload)

        # Check response
        if response.status_code == 200:
            data = response.json()
            print("Model Response:\n", data["response"])
            logging.info(f"Model Response:\n {data['response']}")
            return data["response"]
        else:
            print("Error:", response.status_code, response.text)
            logging.error(f"Error: {response.status_code} {response.text}")
            # Fallback to algorithmic enhancement if LLM fails
            return self._create_enhanced_prompt_fallback(user_prompt)

    def enhance_prompt_local(self, user_prompt: str) -> None:
        # url = "http://host.docker.internal:11434/api/generate"
        url = "http://localhost:11434/api/generate"

        # Define the payload
        payload = {
            "model": "llama2",
            "prompt": f"""
                    You are an artistic prompt enhancer. Your job is to take simple user requests and transform them 
                    into detailed, vivid descriptions for image and 3D generation. Include artistic style, lighting, 
                    mood, colors, perspective, and detailed elements. Make it specific and visual but keep the core 
                    idea intact. Format your response as a rich text description without any explanations or additional 
                    content in maximum 200 words. 

                    Transform this prompt for image generation: 
                    User Request: {user_prompt}

                    Include every detail of user request in the response. 
                """,
            "stream": False 
        }

        # Send a POST request to the Ollama API
        response = requests.post(url, json=payload)

        # Check response
        if response.status_code == 200:
            data = response.json()
            print("Model Response:\n", data["response"])
            logging.info(f"Model Response:\n {data['response']}")
            return data["response"]
        else:
            print("Error:", response.status_code, response.text)
            logging.error(f"Error: {response.status_code} {response.text}")
            # Fallback to algorithmic enhancement if LLM fails
            return self._create_enhanced_prompt_fallback(user_prompt)

    def _create_enhanced_prompt_fallback(self, basic_prompt: str) -> str:
        """
        Creates an enhanced prompt when LLM fails.
        
        Args:
            basic_prompt: Simple user prompt
            
        Returns:
            Enhanced version with artistic details
        """
        art_styles = ["cinematic", "fantasy art", "photorealistic", "digital painting"]
        lighting = ["dramatic lighting", "golden hour sunlight", "soft ambient light", "moody shadows"]
        details = ["intricate details", "high resolution", "textured surfaces", "vibrant colors"]
        
        import random
        style = random.choice(art_styles)
        light = random.choice(lighting)
        detail = random.choice(details)
        
        enhanced = f"{basic_prompt}, {style}, {light}, {detail}, masterfully crafted, 8k resolution"
        logging.info(f"Using fallback enhancement: {enhanced}")
        return enhanced