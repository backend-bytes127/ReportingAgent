import json
import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from .tools.ticket import create_ticket_tool, check_ticket_status_tool, check_attachment_tool
from .handler.chat_model_start_handler import ChatModelStartHandler
from typing import List, Dict
import uuid
import yaml

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_FILE_PATH = os.path.join(BASE_DIR, 'prompt.yaml')

TICKETS_FILE = 'tickets.json'

def load_system_message():
    print(os.listdir())
    with open(PROMPT_FILE_PATH, 'r') as file:
        prompt_data = yaml.safe_load(file)
        prompt_data = prompt_data['system_prompt']
    return prompt_data


system_message = load_system_message()

app = FastAPI()

# LangChain integration setup
class UserInput(BaseModel):
    input: str

class AgentResponse(BaseModel):
    response: str

handler = ChatModelStartHandler()
chat = ChatOpenAI(callbacks=[handler])

prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content=(system_message)),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
tools = [
    create_ticket_tool,
    check_ticket_status_tool,
    check_attachment_tool
]

agent = OpenAIFunctionsAgent(
    llm=chat,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory
)

@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(user_input: UserInput):
    response = agent_executor(user_input.input)
    response_text = response.get("output", "")
    return AgentResponse(response=response_text)

# Ticket endpoints
class TicketRequest(BaseModel):
    issue: str
    reporter_name: str
    email: str
    priority: str
    attachments: str
    department: str
    noticed_at: str


def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_tickets(tickets):
    with open(TICKETS_FILE, 'w') as file:
        json.dump(tickets, file, indent=4)

@app.post("/create-ticket")
async def create_ticket(ticket: TicketRequest):
    tickets = load_tickets()
    ticket_id = str(uuid.uuid4())
    ticket_data = ticket.dict()
    ticket_data.update({"ticket_id": ticket_id, "status": "open"})
    tickets.append(ticket_data)
    save_tickets(tickets)
    return {"message": "Ticket created successfully", "ticket_id": ticket_id}

@app.get("/tickets")
async def get_tickets():
    tickets = load_tickets()
    return tickets

@app.get("/ticket-status/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    tickets = load_tickets()
    for ticket in tickets:
        if ticket["ticket_id"] == ticket_id:
            return {"ticket_id": ticket_id, "status": ticket["status"]}
    raise HTTPException(status_code=404, detail="Ticket not found")
