import os
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.agents.azure_ai import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents.strategies import SequentialSelectionStrategy, KernelFunctionTerminationStrategy, DefaultTerminationStrategy
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents import ChatHistoryTruncationReducer



async def process_expenses():

    # Load environment variables from .env file
    load_dotenv()
    ai_agent_settings = AzureAIAgentSettings.create()

    # Create expense claim data
    data = """{'expenses':[
                {'date':'01-Mar-2025','description':'flight','amount':675.99},
                {'date':'07-Mar-2025','description':'taxi','amount':24.00},
                {'date':'07-Mar-2025','description':'dinner','amount':65.50},
                {'date':'07-Mar-2025','description':'hotel','amount':125.90},
                {'date':'08-Mar-2025','description':'lunch','amount':14.70},
                {'date':'08-Mar-2025','description':'dinner','amount':45.50},
                {'date':'08-Mar-2025','description':'hotel','amount':125.90},
                {'date':'09-Mar-2025','description':'taxi','amount':25.90}]
            }
            """

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

        # Define an agent that categorizes data
        categorization_agent_def = await project_client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name="categorization_agent",
            instructions="You categorize data by formatting it as a table an adding a 'Category' column. Return only the table of categorized data."
        )

        categorization_agent = AzureAIAgent(
            client=project_client,
            definition=categorization_agent_def
        )

        # Define an agent that creates an expense claim
        expenses_agent_def = await project_client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name="expenses_agent",
            instructions="You compose an email to 'expenses@contoso.com' with the subject 'Expense Claim', listing individual expenses, a summary of categorized subtotals, and the grand total. Return the full email including the TO and SUBJECT fields"
        )

        expenses_agent = AzureAIAgent(
            client=project_client,
            definition=expenses_agent_def
        )

        # Create a group chat with the two agents
        history_reducer = ChatHistoryTruncationReducer(target_count=3)
        chat = AgentGroupChat(
            agents=[expenses_agent, categorization_agent],
            selection_strategy=SequentialSelectionStrategy(initial_agent=categorization_agent, history_reducer=history_reducer),
            termination_strategy=DefaultTerminationStrategy(maximum_iterations=2, history_reducer=history_reducer)
        )

        try:
            # Add the user input as a chat message
            prompt_message = "Categorise the following expenses by the categories 'Meals', 'Transportation', and 'Accommodation' - " + data + ". Then create an expenses claim email that includes table of categorized items and a total."
            await chat.add_chat_message(
                ChatMessageContent(role=AuthorRole.USER, content=prompt_message)
            )
            print(f"# AuthorRole.USER: \n{prompt_message}\n")

            async for content in chat.invoke():
                print(f"# {content.role} - {content.name or '*'}: \n{content.content}\n")

        except Exception as e:
            print(f"Error during chat invocation: {e}")
        finally:
            await chat.reset()
            await project_client.agents.delete_agent(expenses_agent.id)
            await project_client.agents.delete_agent(categorization_agent.id)

async def main():
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Run the async agent code
    await process_expenses()

if __name__ == "__main__":
    asyncio.run(main())
