import pytest
from app.domain import QueueService, Priority, Status

@pytest.fixture
def queue():
    return QueueService()

def test_empty_queue(queue):
    assert queue.list() == []

def test_create_normal(queue):
    ticket = queue.create('Ana')
    assert (ticket.id, ticket.name, ticket.priority, ticket.status) == (1, 'Ana', Priority.normal, Status.esperando)

def test_trim_name(queue):
    assert queue.create('  Ana  ').name == 'Ana'

@pytest.mark.parametrize('name', ['', '  ', 'x'*81])
def test_invalid_name(queue, name):
    with pytest.raises(ValueError):
        queue.create(name)

def test_increasing_ids(queue):
    assert [queue.create('Ana').id, queue.create('Bia').id] == [1, 2]

def test_missing_ticket(queue):
    with pytest.raises(KeyError):
        queue.get(999)

def test_fifo_same_priority(queue):
    one = queue.create('A')
    queue.create('B')
    assert queue.call_next().id == one.id

def test_priority_before_normal(queue):
    queue.create('Normal')
    preferred = queue.create('Preferencial', Priority.preferencial)
    assert queue.call_next().id == preferred.id

def test_preferred_fifo(queue):
    queue.create('Normal')
    first = queue.create('P1', Priority.preferencial)
    queue.create('P2', Priority.preferencial)
    assert queue.call_next().id == first.id

def test_call_empty_queue(queue):
    with pytest.raises(ValueError):
        queue.call_next()

def test_cannot_call_twice(queue):
    queue.create('A')
    queue.call_next()
    with pytest.raises(ValueError):
        queue.call_next()

def test_cannot_finish_waiting(queue):
    ticket = queue.create('A')
    with pytest.raises(ValueError):
        queue.finish(ticket.id)

def test_finish_called(queue):
    ticket = queue.create('A')
    queue.call_next()
    assert queue.finish(ticket.id).status == Status.concluido

def test_cannot_finish_twice(queue):
    ticket = queue.create('A')
    queue.call_next()
    queue.finish(ticket.id)
    with pytest.raises(ValueError):
        queue.finish(ticket.id)

def test_list_filter(queue):
    queue.create('A')
    queue.create('B')
    queue.call_next()
    assert len(queue.list(Status.esperando)) == 1
    assert len(queue.list(Status.chamado)) == 1
