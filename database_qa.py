import os
from langchain.prompts.prompt import PromptTemplate
from langchain.sql_database import SQLDatabase
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.chains import SQLDatabaseSequentialChain
import psycopg2

import traceback

db = SQLDatabase.from_uri(os.environ['URL_KEY'],
    sample_rows_in_table_info=2)

llm = OpenAI(temperature=0)

_DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Use the following format:

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:

{table_info}

If someone asks for the a table, the format is typically the following: student -> api_tasks_student.

When asked about particular objects, try to return their names rather than their ids.

when referring to instructors if instructor_id  = N/A, ignore these rows.
participation = taking
program != course
cohort_id = start_term_id
emails in the enrollment table match registered students in the student table.
information for students in active classes is all in current participation.
when asked about grades use both the current participation and participation tables.
a registered student is one who is in the persistence table, format : count(distinct(p.student_id)).
The current term is that found in the current participation table.
use aliases to avoid ambiguity.

Question: {input}"""
PROMPT = PromptTemplate(
    input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
)

#db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=False, return_intermediate_steps=True, prompt=PROMPT)
db_chain = SQLDatabaseSequentialChain(llm=llm, database=db, verbose=False, return_intermediate_steps=True, prompt=PROMPT)

insert_query = "INSERT INTO api_tasks_chat_query (question, query, answer) VALUES %s"

def database_qa(question):
    try:
        answer = db_chain(question)
        query = answer['intermediate_steps'][0]
        insertion = [( question, query, answer['result'] ),]
        conn = psycopg2.connect(os.environ['URL_KEY'])
        cur = conn.cursor()
        psycopg2.extras.execute_values(cur, insert_query, insertion)
        conn.commit()
        cur.close()
        conn.close()
        
        return answer
    except:
        traceback.print_exc()
        return { 'result' : 'Sorry, an error occurred. Please try again later.' }

    
    

