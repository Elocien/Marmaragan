from time import sleep
from openai import OpenAI
from typing import Any, List


class thread_creator:
    """
    A class to create and manage the creation of assistants with OpenAI's API. 
    
    See https://platform.openai.com/docs/assistants/overview for an overview of the functionality of assistants. 
    """

    def __init__(self):
        """
        Initializes a new thread and an assistant for code correction.
        """
        self.client = OpenAI()
        self.thread = self.client.beta.threads.create()
        self.thread_id = self.thread.id
        self.assistant = self.client.beta.assistants.create(
            instructions="You are a programmer. Fix the sent python code so that it runs correctly. Return only the code.",
            name="Python Fixer",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4-0613"
        )

    def create_message(self, message: str) -> None:
        """
        Creates a message in the thread.

        Args:
            message (str): The message content to be sent.
        """
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=message
        )

    def retrieve_messages(self) -> List[Any]:
        """
        Initiates a run of the assistant within the thread and retrieves messages after a delay.

        Returns:
            List[Any]: A list of messages from the thread.
        """
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant.id
        )

        sleep(5)

        run_id = run.id
        self.client.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=run_id
        )

        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread_id
        )

        return messages.data


# Example usage
test = thread_creator()
test.create_message("print('hello world')")
instance = test.retrieve_messages()
