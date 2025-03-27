import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.identity import DefaultAzureCredential
from typing import Any
from pathlib import Path

def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    PROJECT_CONNECTION_STRING= os.getenv("PROJECT_CONNECTION")
    MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT")

    # Load data to be analyzed
    script_dir = Path(__file__).parent  # Get the directory of the script
    file_path = script_dir / 'data.txt'

    with file_path.open('r') as file:
        data = file.read()
        print(data)

    # Connect to the Azure AI Foundry project
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(exclude_environment_credential=True,
                                        exclude_managed_identity_credential=True),
        conn_str=PROJECT_CONNECTION_STRING
    )

    # Define an agent that uses the CodeInterpreter tool
    


if __name__ == '__main__': 
    main()