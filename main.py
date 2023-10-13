import logging
from datetime import datetime
import os
import openai
import subprocess
import argparse

# Set up the logger
logging.basicConfig(filename='history.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Your original Python script
def run_script():
    try:
        # Load your API key from an environment variable or secret management service
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Define the system message
        system_msg = 'You are a helpful assistant who understands data science.'

        # Define the user message
        user_msg = 'Define neuron'
        
        model = "gpt-3.5-turbo-0613"  # or "gpt-4"

        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": system_msg},
                      {"role": "user", "content": user_msg}],
            max_tokens=30
        )


        output_finish_reason = response["choices"][0]["finish_reason"]
        output_content = response["choices"][0]["message"]["content"]

        logging.info(f"Date and Time: {datetime.now()} | Model: {model} | User Message: {user_msg} | Output Finish Reason: {output_finish_reason} | Output Content: {output_content}")

        # Execute gnatprove

        # Supply ada file arg to the python script via argparse
        parser = argparse.ArgumentParser(description="Run gnatprove on an Ada source file.")
        parser.add_argument("ada_source_file", help="Path to the Ada source file to be proved")
        args = parser.parse_args()

        # Command to run gnatprove on the provided Ada source file
        gnatprove_command = f"gnatprove -Pproject_file.gpr {args.ada_source_file}"

        try:
            # Run the gnatprove command as a subprocess
            result = subprocess.run(gnatprove_command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Check if the subprocess completed successfully
            if result.returncode == 0:
                print("gnatprove executed successfully. Output:")
                print(result.stdout)
            else:
                print(f"gnatprove encountered an error. Exit code: {result.returncode}")
                print("Error output:")
                print(result.stderr)

        except subprocess.CalledProcessError as e:
            print(f"Error running gnatprove: {e}")
            logging.error(f"Error running gnatprove: {e}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.error(f"An unexpected error occurred: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.error(f"An unexpected error occurred: {e}")

# Run the script
if __name__ == '__main__':
    run_script()
