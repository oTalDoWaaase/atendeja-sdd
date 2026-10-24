import sys
import threading
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

def test_name_at_max_length(queue):
    assert len(queue.create('x' * 80).name) == 80

def test_finish_missing_ticket(queue):
    with pytest.raises(KeyError):
        queue.finish(999)

def test_waiting_queue_order(queue):
    n1 = queue.create('N1')
    p1 = queue.create('P1', Priority.preferencial)
    n2 = queue.create('N2')
    p2 = queue.create('P2', Priority.preferencial)
    assert [t.id for t in queue.waiting_queue()] == [p1.id, p2.id, n1.id, n2.id]

def test_waiting_queue_matches_call_order(queue):
    for i, priority in enumerate([Priority.normal, Priority.preferencial] * 3):
        queue.create(f'C{i}', priority)
    expected = [t.id for t in queue.waiting_queue()]
    assert [queue.call_next().id for _ in expected] == expected
    assert queue.waiting_queue() == []

def test_strict_priority_keeps_normal_waiting(queue):
    # Caracteriza a regra vigente (ADR-003): preferenciais que chegam depois
    # continuam passando à frente da normal. Mudar isso exige decisão humana.
    normal = queue.create('Normal')
    for i in range(3):
        queue.create(f'P{i}', Priority.preferencial)
        assert queue.call_next().priority == Priority.preferencial
    assert queue.call_next().id == normal.id

def _run_concurrently(worker, threads=16):
    previous = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)  # força trocas de thread frequentes para expor corridas
    barrier = threading.Barrier(threads)
    def run():
        barrier.wait()
        worker()
    pool = [threading.Thread(target=run) for _ in range(threads)]
    try:
        for t in pool:
            t.start()
        for t in pool:
            t.join()
    finally:
        sys.setswitchinterval(previous)

def test_concurrent_call_next_never_repeats_ticket(queue):
    # Regressão: sem lock, a mesma senha era chamada por mais de uma thread.
    for i in range(320):
        queue.create(f'C{i}')
    called = []
    def worker():
        for _ in range(20):
            called.append(queue.call_next().id)
    _run_concurrently(worker)
    assert len(called) == 320
    assert len(set(called)) == 320
    assert queue.list(Status.esperando) == []

def test_concurrent_create_unique_ids(queue):
    def worker():
        for _ in range(50):
            queue.create('C')
    _run_concurrently(worker)
    ids = [t.id for t in queue.list()]
    assert sorted(ids) == list(range(1, 16 * 50 + 1))
