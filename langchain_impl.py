from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
import re




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





    