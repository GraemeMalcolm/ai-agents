import os
import asyncio

# Add references



async def main():
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Create expense claim data
    data = """{'expenses':[
                {'date':'07-Mar-2025','description':'taxi','amount':24.00},
                {'date':'07-Mar-2025','description':'dinner','amount':65.50},
                {'date':'07-Mar-2025','description':'hotel','amount':125.90}]
            }
            """

    # Run the async agent code
    await create_expense_claim(data)

async def create_expense_claim(expenses_data):

    # Get configuration settings


    # Connect to the Azure AI Foundry project

        
        # Define an agent that sends an expense claim email


        # Create an instance of the agent


        # Use the agent to generate an expense claim email



# Plugin for the email functionality
class EmailPlugin:
    """A Plugin to simulate email functionality."""

    @kernel_function(description="Sends and email.")
    def send_email(self, to, subject, body):
        print("\nTo:", to)
        print("Subject:", subject)
        print(body, "\n")


if __name__ == "__main__":
    asyncio.run(main())
