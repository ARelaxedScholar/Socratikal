import asyncio
import warnings
from pocketflow import Node, AsyncBatchNode, AsyncFlow
from google import genai
import json

from dotenv import load_dotenv
import os

import re

def extract_json_from_block(text: str) -> str:
    # The regex pattern
    pattern = r"```(?:json)?\s*(.*)```"

    # re.DOTALL allows '.' to match newline characters
    match = re.search(pattern, text.strip(), re.DOTALL)

    if match:
        # group(1) returns the content of the first capturing group (.*)
        return match.group(1).strip()
    else:
        # If no code block is found, return the original text
        return text

load_dotenv()
api_key = os.getenv("API_KEY")
# Defining a global pipe
client = genai.Client(api_key=api_key)

class Socratikal(Node):
    def prep(self, shared):
        if not shared["completed_loop"]:
            shared["completed_loop"] = True 
            user_input = input("User: ")
            if "history" not in shared:
                shared["history"] = [{"role": "admin", "message": shared["Socratikal"]}]
            shared.get("history").append({
                "role": "user",
                "message" : user_input,
                })

            # Pass the data to the exec node
            return shared['history']
        else:
            shared["completed_loop"] = False
            return shared["final_question"]

    def exec(self, prep_res):
        if isinstance(prep_res, list):
            response = client.models.generate_content(
                model='gemini-2.5-flash', contents=str(prep_res)
            )
            try:
                subjects = json.loads(extract_json_from_block(response.text))
                return subjects
            except:
                raise ValueError(f"Socratikal returned string that didn't follow the format: {response.text}")
        elif isinstance(prep_res, str):
            print("Socratikal: " + prep_res)
            return prep_res
        else:
            # Shouldn't happen
            pass

        
    def post(self, shared, prep_res, exec_res):
        if isinstance(exec_res, str):
            # We are ready to return
            shared.get("history").append({"role": "llm",
                                      "message": exec_res,})
            return "self" 
        if isinstance(exec_res, list):
            # It's the first pass through this
            shared["subjects"] = exec_res
            return None # We go to next node
        
class GeneratingQuestions(AsyncBatchNode):
    async def prep_async(self, shared):
        return [(shared["history"], subject) for subject in shared.get("subjects", [])]

    async def exec_async(self, subject_tuple):
        response = client.models.generate_content(
                model='gemini-2.5-flash', contents=str(f"Given this full history: {subject_tuple[0]} and the following subject: {subject_tuple[1]}, write the most thought-provoking question you can think of. Note that it should be a conversational question, so not an essay prompt. It should be light enough that it could be said in speech, but insightful.")
        )
        return response.text

    async def post_async(self, shared, prep_res, exec_res):
        shared["questions"] = exec_res
        return None # We go to the next node
    
class Ranker(Node):
    def prep(self, shared):
        return (shared["history"], shared["questions"])
    def exec(self, prep_res):
        system_prompt = """Given this full history: {} and this list of questions {}, you will select the most thought-provoking, learning-accelerating, conversation-forwarding question. You WILL output the choice as a JSON dictionary with the following format:           
        {{
            'question' : <The selected question>,
            'reasoning' : <Why is this the question you selected>
        }}                
        Failure to follow this format will represent a failure in your mission.""".format(prep_res[0], prep_res[1])

        response = client.models.generate_content(
                model='gemini-2.5-flash', contents=str(system_prompt))
        try:
            basic_json = extract_json_from_block(response.text) # Because the LLM likely wrapped the JSON
            return json.loads(basic_json)["question"]
        except:
            warnings.warn(f"Ranker failed to respect the expected format: {response.text}")
            return prep_res[1][0] # return the first question
    def post(self, shared, prep_res, exec_res):
        shared["final_question"] = exec_res




node1 = Socratikal()
node2 = GeneratingQuestions()
node3 = Ranker()

node1 - "self" >> node1
node1 >> node2 >> node3 >> node1


flow = AsyncFlow(start=node1)

if __name__ == "__main__":
    shared = {}
    shared["completed_loop"] = False
    shared["Socratikal"] = """Based on the current history and the subject decided by the user,
                              you will identify thought-inducing subjects within the domain selected by the user
                              to force them to think socratically, and turn them into an expect.

                              You shall generate your list of subjects, 5 to 10 as a Json list as follows:
                              ['subect 1', 'subject 2', 'subject 3', 'subject 4', 'subject 5', 'subject 6', 'subject 7']
                              Your subjects be clear prompts and thinking direction for the user to explore."""
    
    asyncio.run(flow.run_async(shared))

