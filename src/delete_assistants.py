from openai import OpenAI
import os


client = OpenAI()

# Function to list all assistants


def list_assistants():
    
    list_of_assistants = client.beta.assistants.list(
        order="desc",
    )
    
    return list_of_assistants.data


def delete_assistant(assistant_id):
    response = client.beta.assistants.delete(assistant_id)
    print(response)

# Main execution
if __name__ == "__main__":
    assistants = list_assistants()

    for assistant in assistants:
        print(f"Assistant id: {assistant.id}")
        delete_assistant(assistant.id)
