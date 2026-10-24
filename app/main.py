"""API REST AtendeJá. Armazenamento volátil, intencional para MVP acadêmico."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from .domain import QueueService, Priority, Status, Ticket

class TicketInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    priority: Priority = Priority.normal

class TicketOutput(BaseModel):
    id: int
    name: str
    priority: Priority
    status: Status
    created_at: str

def serialize(ticket: Ticket) -> TicketOutput:
    return TicketOutput(id=ticket.id, name=ticket.name, priority=ticket.priority,
                        status=ticket.status, created_at=ticket.created_at.isoformat())

def create_app() -> FastAPI:
    app = FastAPI(title='AtendeJá', description='API de senhas de atendimento', version='1.0.0')
    app.state.queue = QueueService()

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    @app.post('/tickets', response_model=TicketOutput, status_code=201)
    def create_ticket(payload: TicketInput, request: Request):
        try:
            return serialize(request.app.state.queue.create(payload.name, payload.priority))
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    @app.get('/tickets', response_model=list[TicketOutput])
    def get_tickets(request: Request, status: Status | None = None):
        return [serialize(t) for t in request.app.state.queue.list(status)]

    @app.get('/tickets/{ticket_id}', response_model=TicketOutput)
    def get_ticket(ticket_id: int, request: Request):
        try:
            return serialize(request.app.state.queue.get(ticket_id))
        except KeyError as error:
            raise HTTPException(404, str(error)) from error

    @app.post('/tickets/next', response_model=TicketOutput)
    def next_ticket(request: Request):
        try:
            return serialize(request.app.state.queue.call_next())
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    @app.post('/tickets/{ticket_id}/finish', response_model=TicketOutput)
    def finish_ticket(ticket_id: int, request: Request):
        try:
            return serialize(request.app.state.queue.finish(ticket_id))
        except KeyError as error:
            raise HTTPException(404, str(error)) from error
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    return app

app = create_app()
