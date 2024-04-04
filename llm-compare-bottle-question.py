#Allows you to ask a question 
from bottle import route, post, run, request
import sqlite3
import os
import ollama
import time

#Class For Interacting with Database
#path() is used for using database in same folder as script
class database:
    def path():
        current_directory = os.path.dirname(os.path.abspath(__file__))
        db_name = 'question.db'
        file_path = os.path.join(current_directory, db_name)

        return file_path

    def db_create():
        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        create_table = '''
                        create table if not exists result(
                            id integer primary key,
                            model text,
                            query text,
                            response text,
                            time text
                        )
                        '''

        cursor.execute(create_table)
        conn.commit()
        conn.close()

    def db_select():
        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        sql = 'select * from result order by id desc'
        cursor.execute(sql)
        record = cursor.fetchall()
        conn.commit()
        conn.close()

        return record

    def db_insert(model, query, response, time):

        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        sql = 'insert into result(model, query, response, time) values(?,?,?,?)'
        cursor.execute(sql,(model, query, response, time))
        conn.commit()
        conn.close()

#LLM Function
def ask(query, llm):
    time_start = time.time()
    query = f'Answer this user query: {query} \
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

#Index Page. Query form sends values back to this page
@route('/')
@post('/')
def index():
    query = request.forms.get('query')

    model = ['llama2:7b', 'llama2:13b','phi','mistral']

    if query != None:
        for llm in model:
            response = ask(query,llm) #response[0] = response, response[1] = time_elapse
            database.db_insert(llm, query,response[0], response[1])
            print(response)

    record_set = database.db_select()

    form =  f'''
                <form action="./" method="post">
                Question: <textarea cols="50" rows="1" name="query"></textarea>
                <br>
                <input type="submit">
                </form>
            '''
    
    previous=''
    set_new=''
    set_old=''
    for record in record_set:
        set_new=record[2]
        if set_new != set_old:
            previous = f'{previous}</div><br><div style="border:solid 3px black;">\
                        <span style="font-size:20;font-weight:bold;">{set_new}</span>'
            set_old = set_new
        previous =f'''
                        {previous} 
                        <div style="border:solid 1px black">
                            <strong>Model:</strong> {record[1]} <br>
                            <strong>Response:</strong><br> <pre>{record[3]}</pre>
                            <strong>Time:</strong> {record[4]}
                        </div>
                    '''
    
    page = f'''
                {form}
                {previous}
            '''

    return page

database.db_create()

run(host='0.0.0.0', port=80, debug=True)
