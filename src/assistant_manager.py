from time import sleep
from openai import OpenAI
from typing import Any, List


class openai_assistant:
    """
    A class to create and manage the creation of assistants, threads and messages with OpenAI's API. 
    
    See https://platform.openai.com/docs/assistants/overview for an overview of the functionality of assistants. 
    
    Unfortunalty there is no way to set temperature yet, see https://community.openai.com/t/how-to-set-temperature-and-other-hyperparameters-of-model-in-open-ai-assistant-api/486368
    """

    def __init__(self, instructions: str, gpt_model: str):
        """
        Initializes a new thread and an assistant for code correction.
        
        Args:
            instructions (str): Instructions detailing the purpose of the Assistant. E.g. "You are a programmer. Fix the sent python code so that it runs correctly"
            gpt_model (str): The GPT model to use. Choice of "gpt-3.5-turbo-1106", "gpt-4-0125-preview" or "gpt-4-0613"
        """
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.create(
            instructions=instructions,
            name="Spark Annotation Assistant",
            tools=[{"type": "code_interpreter"}],
            model=gpt_model
        )
        
        print(f"Created Assistant with id: {self.assistant.id}\n")

    def create_message(self, message: str) -> str:
        """
        Creates a message in the thread.

        Args:
            message (str): The message content to be sent.
        """
        thread = self.client.beta.threads.create()
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message
        )
        
        return thread.id
        

    def retrieve_messages(self, thread_id: str) -> List[Any]:
        """
        Initiates a run of the assistant within the thread and retrieves messages after a delay.

        Returns:
            List[Any]: A list of messages from the thread.
        """
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id
        )

        
        status = ""

        # Polling of the api to check if the run is completed
        while status != "completed":
            status = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            ).status
            
            sleep(1)

        # Retrieve the messages from the thread
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id
        )

        return messages.data
    

    def delete_assistant(self) -> None:
        """
        Deletes the Assistant
        """
        # Initialize the OpenAI client
        client = OpenAI()

        # Delete the assistant
        response = client.beta.assistants.delete(self.assistant.id)
        print(f"Assistant deleted:\n{response}")


