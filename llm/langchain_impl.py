from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.prompts import load_prompt
import re



def get_prompt(file_name):
    # Load Prompt
    prompt = load_prompt(file_name)
    
    return prompt.format()



def sanitize_output(text: str):
    _, after = text.split("```ada")
    return after.split("```")[0]




def generate_llm_response(llm_model, llm_temperature, prompt):
    """
    This class initialises the language model, passes the prompt to the llm and returns its response
    """


    llm = ChatOpenAI(model_name=llm_model, temperature=llm_temperature)
    
    # Predict
    with get_openai_callback() as cb:
        response = llm.predict(prompt)
        # response = sanitize_output(llm.predict(prompt))
        tokens = re.findall(r"Tokens Used: (\d+)", str(cb))[0] if re.findall(r"Tokens Used: (\d+)", str(cb)) else "Error"
        
        
        
        return (response, tokens)





    