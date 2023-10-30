from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.prompts import StringPromptTemplate

import logging
from datetime import datetime



# Model Params
llm_model = "gpt-3.5-turbo-0613" or "gpt-4"
llm_temperature = 0
llm = ChatOpenAI(model_name=llm_model, temperature=llm_temperature)



# Logging Setup
# Set up the logger
logging.basicConfig(filename='history.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')





# Prompt Template
PROMPT = """\
Given the following ADA/SPARK2014 file, generate a {feature} and return the full code.

Source Code:
{source_code}


"""




def sanitize_output(text: str):
    _, after = text.split("```ada")
    return after.split("```")[0]




# Predict
with get_openai_callback() as cb:
    print(sanitize_output(llm.predict("Write the files for an implementation of a binary search in ada/spark2014. Make sure to include all spark annotations such as loop invariants and pre and post conditions. There is no need to explain the implementation, simply return the code")))
    print(cb)
    
    


    
# Log
# logging.info(f"Date and Time: {datetime.now()} | Model: {llm_model} | Temperature: {llm_temperature} | User Message: {user_msg} | Output Finish Reason: {output_finish_reason} | Output Content: {output_content}")