import os
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def launch_streamlit():
    try:
        logger.info("Starting Streamlit app...")
        # Use the python interpreter that's running this script to launch streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "gui.py", "--server.port=8501", "--server.address=0.0.0.0"]
        subprocess.run(cmd)
    except Exception as e:
        logger.error(f"Failed to start Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    launch_streamlit()