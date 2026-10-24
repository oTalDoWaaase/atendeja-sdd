"""API REST AtendeJá. Armazenamento volátil, intencional para MVP acadêmico."""
from pathlib import Path
from typing import Annotated
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, StringConstraints
from . import __version__
from .domain import NAME_MAX_LENGTH, QueueService, Priority, Status, Ticket

STATIC_DIR = Path(__file__).parent / 'static'

# A interface só carrega recursos da própria origem; não se aplica ao /docs (Swagger usa CDN).
UI_SECURITY_HEADERS = {
    'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'",
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
}

class TicketInput(BaseModel):
    # Espaços nas bordas são removidos antes de validar o tamanho, como no domínio.
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=NAME_MAX_LENGTH)]
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
    app = FastAPI(title='AtendeJá', description='API de senhas de atendimento', version=__version__)
    app.state.queue = QueueService()
    app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

    @app.get('/', include_in_schema=False)
    def index():
        return FileResponse(STATIC_DIR / 'index.html', headers=UI_SECURITY_HEADERS)

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

    @app.get('/queue', response_model=list[TicketOutput])
    def get_queue(request: Request):
        """Senhas em espera na ordem em que serão chamadas por POST /tickets/next."""
        return [serialize(t) for t in request.app.state.queue.waiting_queue()]

    @app.get('/tickets/{ticket_id}', response_model=TicketOutput)
    def get_ticket(ticket_id: int, request: Request):
        try:
            return serialize(request.app.state.queue.get(ticket_id))
        except KeyError as error:
            raise HTTPException(404, error.args[0]) from error

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
            raise HTTPException(404, error.args[0]) from error
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    return app

app = create_app()
