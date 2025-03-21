import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import FunctionTool, ToolSet
from user_functions import user_functions

# Clear the console
os.system('cls' if os.name=='nt' else 'clear')

# Load environment variables from .env file
load_dotenv()
PROJECT_CONNECTION_STRING= os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT")

# Create expense claim data
data = "Transportation: $2,500, Meals: $560.35, Accommodation: $1234.00, Misc: $125.00"


# Connect to the Azure AI Foundry project
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(exclude_environment_credential=True,
                                      exclude_managed_identity_credential=True),
    conn_str=PROJECT_CONNECTION_STRING
)

# Define an agent that uses a custom function

