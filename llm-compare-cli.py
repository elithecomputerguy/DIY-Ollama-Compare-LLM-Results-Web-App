import ollama
import os
import time 

#Turn File into a variable value
current_directory = os.path.dirname(os.path.abspath(__file__))
file_name = 'info.txt'
file_path = os.path.join(current_directory, file_name)
with open(file_path, 'r') as file:
    data = file.read()

#Function to make AI Request
def ask(query, llm, data):
    time_start = time.time()
    query = f'Answer this user query: {query} \
            based on the information in this data: {data} \
            -- be as succinct as possible \
            -- just answer the specific question with no other information'
    response = ollama.chat(model=llm, messages=[
    {
        'role': 'user',
        'content': query,
    },
    ])
    response = response['message']['content']
    time_elapse = time.time() - time_start

    return response,time_elapse

os.system('clear')
model = ['llama2:7b', 'llama2:13b','phi','mistral']
while True:
    query = input('how can i help you?  ')
    os.system('clear')
    print(f'Question: {query}')
    for llm in model:
        answer = ask(query, llm, data)
        print(f'Model: {llm}')
        print(f'Response: {answer[0]}')
        print(f'Time: {answer[1]}\n')
