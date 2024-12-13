import httpx
from pydantic import BaseModel

class CreateTicketRequest(BaseModel):
    issue: str
    reporter: str
    email: str
    priority: str
    department: str
    datetime: str

class Ticket(BaseModel):
    ticket_id: int
    status: str

class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client()

    def make_get(self, path: str, params: dict = None) -> dict:
        url = f"{self.base_url}/{path}"
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def make_post(self, path: str, data: dict) -> dict:
        url = f"{self.base_url}/{path}"
        response = self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def create_ticket(self, request: CreateTicketRequest) -> dict:
        return self.make_post("create-ticket", data=request.dict())

    def get_tickets(self) -> dict:
        return self.make_get("tickets")

    def get_ticket_status(self, ticket_id: int) -> Ticket:
        response = self.make_get(f"ticket-status/{ticket_id}")
        return Ticket(**response)
