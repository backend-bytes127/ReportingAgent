from langchain.tools import StructuredTool
from pydantic.v1 import BaseModel
import json
import uuid
from typing import Dict

TICKET_FILE = 'tickets.json'

class CreateTicketArgsSchema(BaseModel):
    issue: str
    reporter_name: str
    email: str
    priority: str
    attachments: str
    department: str
    noticed_at: str

class CheckTicketStatusArgsSchema(BaseModel):
    ticket_id: str


def create_ticket_issue(issue: str, reporter_name: str, email: str, priority: str, attachments: str, department: str, noticed_at: str) -> Dict:
    ticket_id = str(uuid.uuid4())  
    ticket_data = {
        "ticket_id": ticket_id,
        "issue": issue,
        "reporter_name": reporter_name,
        "email": email,
        "priority": priority,
        "attachments": attachments,
        "department": department,
        "noticed_at": noticed_at,
        "status": "Open"
    }
    
    try:
        with open(TICKET_FILE, 'r') as f:
            tickets = json.load(f)
    except FileNotFoundError:
        tickets = []
    
    tickets.append(ticket_data)
    
    with open(TICKET_FILE, 'w') as f:
        json.dump(tickets, f, indent=4)
    
    return {
        "message": f"Ticket {ticket_id} created successfully.",
        "ticket_id": ticket_id,
        "status": "Open"
    }


def check_ticket_status(ticket_id: str) -> Dict:
    try:
        with open(TICKET_FILE, 'r') as f:
            tickets = json.load(f)
        
        for ticket in tickets:
            if ticket["ticket_id"] == ticket_id:
                return {
                    "ticket_id": ticket_id,
                    "status": ticket["status"],
                    "issue": ticket["issue"]
                }
        
        return {"message": "Ticket ID not found."}
    
    except FileNotFoundError:
        return {"message": "No tickets found."}



create_ticket_tool = StructuredTool.from_function(
    name="create_ticket_issue",
    description="Create a ticket in the issue tracking system with the gathered information.",
    func=create_ticket_issue,
    args_schema=CreateTicketArgsSchema
)

check_ticket_status_tool = StructuredTool.from_function(
    name="check_ticket_status",
    description="Check the status of a ticket by its ID.",
    func=check_ticket_status,
    args_schema=CheckTicketStatusArgsSchema
)


def check_attachment_name(ticket_id:str): 
    try:
        with open(TICKET_FILE, 'r') as f:
            tickets = json.load(f)

        for ticket in tickets:
            if ticket["ticket_id"] == ticket_id:
                return {
                    "ticket_id": ticket_id,
                    "file_name": ticket["attachments"]
                }
        
        return {"message": "Ticket ID not found."}
    
    except FileNotFoundError:
        return {"message": "No tickets found."}

check_attachment_tool = StructuredTool.from_function(
    name="check_attachment_name",
    description="Get the filename of the attachment",
    func=check_attachment_name
)

