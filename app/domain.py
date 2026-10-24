"""Regras de negócio puras para gestão de senhas de atendimento."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from threading import Lock

NAME_MAX_LENGTH = 80

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

def _call_order(ticket: Ticket) -> tuple[int, int]:
    # Preferencial antes da normal; FIFO (id crescente) dentro da mesma categoria.
    return (0 if ticket.priority == Priority.preferencial else 1, ticket.id)

class QueueService:
    def __init__(self):
        self._tickets: dict[int, Ticket] = {}
        self._next_id = 1
        # Endpoints síncronos do FastAPI rodam em threads; o lock torna cada
        # operação atômica (evita chamar a mesma senha duas vezes ou repetir ids).
        self._lock = Lock()

    def create(self, name: str, priority: Priority = Priority.normal) -> Ticket:
        name = name.strip()
        if not name or len(name) > NAME_MAX_LENGTH:
            raise ValueError(f'Nome deve conter entre 1 e {NAME_MAX_LENGTH} caracteres.')
        with self._lock:
            ticket = Ticket(self._next_id, name, priority, Status.esperando, datetime.now(timezone.utc))
            self._tickets[ticket.id] = ticket
            self._next_id += 1
        return ticket

    def list(self, status: Status | None = None) -> list[Ticket]:
        with self._lock:
            return [t for t in self._tickets.values() if status is None or t.status == status]

    def waiting_queue(self) -> list[Ticket]:
        """Senhas em espera na ordem exata em que call_next as chamará."""
        return sorted(self.list(Status.esperando), key=_call_order)

    def get(self, ticket_id: int) -> Ticket:
        with self._lock:
            if ticket_id not in self._tickets:
                raise KeyError('Senha não encontrada.')
            return self._tickets[ticket_id]

    def call_next(self) -> Ticket:
        with self._lock:
            waiting = [t for t in self._tickets.values() if t.status == Status.esperando]
            if not waiting:
                raise ValueError('Não há senhas aguardando.')
            chosen = min(waiting, key=_call_order)
            chosen.status = Status.chamado
            return chosen

    def finish(self, ticket_id: int) -> Ticket:
        with self._lock:
            ticket = self._tickets.get(ticket_id)
            if ticket is None:
                raise KeyError('Senha não encontrada.')
            if ticket.status != Status.chamado:
                raise ValueError('Apenas senhas chamadas podem ser concluídas.')
            ticket.status = Status.concluido
            return ticket
