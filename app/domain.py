"""Regras de negócio puras para gestão de senhas de atendimento."""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

class Priority(str, Enum):
    normal = 'normal'
    preferencial = 'preferencial'

class Status(str, Enum):
    esperando = 'esperando'
    chamado = 'chamado'
    concluido = 'concluido'

@dataclass
class Ticket:
    id: int
    name: str
    priority: Priority
    status: Status
    created_at: datetime

class QueueService:
    def __init__(self):
        self._tickets: dict[int, Ticket] = {}
        self._next_id = 1

    def create(self, name: str, priority: Priority = Priority.normal) -> Ticket:
        name = name.strip()
        if not name or len(name) > 80:
            raise ValueError('Nome deve conter entre 1 e 80 caracteres.')
        ticket = Ticket(self._next_id, name, priority, Status.esperando, datetime.now(timezone.utc))
        self._tickets[ticket.id] = ticket
        self._next_id += 1
        return ticket

    def list(self, status: Status | None = None) -> list[Ticket]:
        return [t for t in self._tickets.values() if status is None or t.status == status]

    def get(self, ticket_id: int) -> Ticket:
        if ticket_id not in self._tickets:
            raise KeyError('Senha não encontrada.')
        return self._tickets[ticket_id]

    def call_next(self) -> Ticket:
        waiting = self.list(Status.esperando)
        if not waiting:
            raise ValueError('Não há senhas aguardando.')
        # Preferencial antes da normal; FIFO dentro da mesma categoria.
        chosen = min(waiting, key=lambda t: (0 if t.priority == Priority.preferencial else 1, t.id))
        chosen.status = Status.chamado
        return chosen

    def finish(self, ticket_id: int) -> Ticket:
        ticket = self.get(ticket_id)
        if ticket.status != Status.chamado:
            raise ValueError('Apenas senhas chamadas podem ser concluídas.')
        ticket.status = Status.concluido
        return ticket
