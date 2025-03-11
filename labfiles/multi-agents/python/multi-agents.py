import os
import asyncio
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.models import CodeInterpreterTool
from azure.ai.projects.models import FunctionTool, ToolSet
from user_functions import user_functions
from typing import Any
from pathlib import Path
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.agents.azure_ai import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy
from semantic_kernel.agents.strategies import SequentialSelectionStrategy, DefaultTerminationStrategy
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents import ChatHistoryTruncationReducer



async def process_expenses():

    # Load environment variables from .env file
    load_dotenv()
    ai_agent_settings = AzureAIAgentSettings.create()

    # Create expense claim data
    data = "Transportation: $2,500, Meals: $560.35, Accommodation: $1234.00, Misc: $125.00"

    # Connect to the Azure AI Foundry project
    async with (
        DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True) as creds,
        AzureAIAgent.create_client(
            credential=creds,
            conn_str=ai_agent_settings.project_connection_string.get_secret_value(),
        ) as project_client,
    ):

        # Define an agent that uses the code interpreter to create charts
        code_interpreter = CodeInterpreterTool()
        chart_agent_def = await project_client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name="chart-agent",
            instructions="You are helpful agent that creates charts based on provided data.",
            tools=code_interpreter.definitions,
            tool_resources=code_interpreter.resources,
        )

        chart_agent = AzureAIAgent(
            client=project_client,
            definition=chart_agent_def
        )

        # Define an agent that uses a custom function to send email
        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)

        email_agent_def = await project_client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name="email-agent",
            instructions="You are an AI assistant that creates and sends email messages.",
            toolset=toolset
        )

        email_agent = AzureAIAgent(
            client=project_client,
            definition=email_agent_def
        )

        # Create a group chat with the two agents
        history_reducer = ChatHistoryTruncationReducer(target_count=5)
        chat = AgentGroupChat(
            agents=[email_agent, chart_agent],
            selection_strategy=SequentialSelectionStrategy(history_reducer=history_reducer),
            termination_strategy=DefaultTerminationStrategy(maximum_iterations=2, history_reducer=history_reducer),
            
            #termination_strategy=ApprovalTerminationStrategy(agents=[chart_agent], maximum_iterations=10)
            #termination_strategy=TerminationStrategy(maximum_iterations=10)
        )

        try:
            # Add the user input as a chat message
            prompt_message = "Send an email containing an itemized list of the expense claim items in the following data as well as the total to expenses@contoso.com with the subject 'Expense Claim' - " + data + ". Then create a pie chart of the expense categories and save it as a png file."
            await chat.add_chat_message(
                ChatMessageContent(role=AuthorRole.USER, content=prompt_message)
            )
            print(f"# User: '{prompt_message}'")

            async for content in chat.invoke():
                print(f"# {content.role} - {content.name or '*'}: '{content.content}'")

            print(f"# IS COMPLETE: {chat.is_complete}")

            print("*" * 60)
            print("Chat History (In Descending Order):\n")
            async for message in chat.get_chat_messages(agent=save_agent):
                print(f"# {message.role} - {message.name or '*'}: '{message.content}'")
        except Exception as e:
            print(f"Error during chat invocation: {e}")
        finally:
            await chat.reset()
            await project_client.agents.delete_agent(email_agent.id)
            await project_client.agents.delete_agent(chart_agent.id)

async def main():
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Run the async agent code
    await process_expenses()

class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate."""

    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return "chart" in history[-1].content.lower()

if __name__ == "__main__":
    asyncio.run(main())
