
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph,START,END,add_messages
from langgraph.types import interrupt,Command
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Annotated,TypedDict,List
import sqlite3
import uuid

from models.llms import create_llm 

llm = create_llm(temperature=0.3)

# Define state
class state(TypedDict):
    linkedin_topic:str
    generated_post:Annotated[List[str],add_messages]
    human_feedback: Annotated[List[str], add_messages]


def model(state:state):
    linkedin_topic = state["linkedin_topic"]
    feedback = state['human_feedback'] if 'human_feedback' in state else ['No feedback yet']

  

    prompt= f'''
        Linkedin topic = {linkedin_topic}
        feedback = {feedback[-1] if feedback else "No feedback yet"}

        Generate a structured and well-written linkedin post based on the given topic.

        consider previous human feedback to refine the response.
        '''
    response = llm.invoke([
        SystemMessage(content="You are a helpful ai assiatant expertise in writing Linkedin content."),
        HumanMessage(content=prompt)
    ])

    generated_post = response.content

    print(f"Generated post: \n {generated_post}")

    return {"generated_post": [AIMessage(content=generated_post)],
            "human_feedback":feedback}

def human_node(state:state):
    
    generated_post = state['generated_post']

    # Interrupt to get user feedback
    user_feedback = interrupt(
        {
            "generated_post": generated_post,
            "message":"provide feedback or type done to finish"
        }
    )
 
    if user_feedback.lower() in ['done','d']:
        return Command(update={"human_feedback":state["human_feedback"]+["finalised"]},goto=END)
    
    return Command(update={"human_feedback":state["human_feedback"]+[user_feedback]},goto="model")


graph = StateGraph(state)
graph.add_node("model",model)
graph.add_node("human_node",human_node)

graph.add_edge(START,"model")
graph.add_edge("model","human_node")



# make db connection
sqlite_connection = sqlite3.connect("simple_chatbot.sqlite",check_same_thread=False)

memory = SqliteSaver(sqlite_connection)

app= graph.compile(checkpointer=memory)

if __name__ == "__main__":

    thread_config = {'configurable':{
        "thread_id":uuid.uuid4()}
        }

    linkedin_topic = input("Enter linkedin topic: ")

    initial_state ={
        "linkedin_topic":linkedin_topic,
        "generated_post":[],
        "human_feedback":[]
    }

    for chunk in app.stream(initial_state,thread_config):
        for node_id,value in chunk.items():
            if node_id == "__interrupt__":
                while True:
                    user_feedback = input("Enter feedback or type 'done' if finished. : ")
                    if user_feedback is not None:
                        app.invoke(Command(resume=user_feedback),config=thread_config)
                    
                    if user_feedback.lower() in ['done','d']:
                        break
