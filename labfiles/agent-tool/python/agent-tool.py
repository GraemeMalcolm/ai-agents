import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.identity import DefaultAzureCredential
from typing import Any
from pathlib import Path

DEBUG = False

# Load environment variables from .env file
load_dotenv()
PROJECT_CONNECTION_STRING= os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT")

# Create data to be charted
data = "Transportation: $2,500, Meals: $560.35, Accommodation: $1234.00, Misc: $125.00"


# Connect to the Azure AI Foundry project
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(exclude_environment_credential=True,
                                      exclude_managed_identity_credential=True),
    conn_str=PROJECT_CONNECTION_STRING
)

# Define an agent that uses a custom function
with project_client:

    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)

    agent = project_client.agents.create_agent(
        model=MODEL_DEPLOYMENT,
        name="email-agent",
        instructions="You are an AI assistant that creates and sends email messages.",
        toolset=toolset
    )
    print(f"Created agent, ID: {agent.id}")

    # Create and run a thread with a prompt message
    thread = project_client.agents.create_thread()
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Create an itemized list of the expense claim items in the following data and calculate the total:\n" + data + "\nThen send the list and total in an email to expenses@contoso.com with the subject 'Expense Claim'."
    )
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)

    # Check the run status for failures
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Get messages from the thread and print the last one from the agent
    messages = project_client.agents.list_messages(thread_id=thread.id)
    last_msg = messages.get_last_text_message_by_role("assistant")
    if last_msg:
        print(f"Last Message: {last_msg.text.value}")

    # Generate an image file for each image in the messages
    for image_content in messages.image_contents:
        file_name = f"{image_content.image_file.file_id}_image_file.png"
        project_client.agents.save_file(file_id=image_content.image_file.file_id, file_name=file_name)

    # Get the file path(s) from the messages
    for file_path_annotation in messages.file_path_annotations:
        project_client.agents.save_file(file_id=file_path_annotation.file_path.file_id, file_name=Path(file_path_annotation.text).name)
        print(f"Chart saved as {Path(file_path_annotation.text).name}")

    # Delete the agent when done
   project_client.agents.delete_agent(agent.id)



