import multiprocessing
import os
import threading
import time

import pytest

from loguru import logger


@pytest.fixture
def fork_context():
    return multiprocessing.get_context("fork")


def child_process_log_and_complete():
    for i in range(10):
        logger.info("Child {}", i)
        logger.complete()


def test_complete_does_not_deadlock_with_sink_write_waiting_on_core_lock():
    # The sink needs the core lock (through "contextualize()") while "write()" is executed
    # with the handler lock acquired. If "complete()" held the core lock while waiting for
    # the handler lock, both threads would end up waiting for each other.
    write_started = threading.Event()
    finish_write = threading.Event()

    class Sink:
        def write(self, message):
            write_started.set()
            assert finish_write.wait(10)
            with logger.contextualize(key="value"):
                pass

    logger.add(Sink(), format="{message}", catch=False)

    writer_thread = threading.Thread(target=logger.info, args=("Message",), daemon=True)
    writer_thread.start()

    # Wait for the sink to hold the handler lock, then give "complete()" the opportunity
    # to start waiting for it before releasing the sink (which will then need the core
    # lock held by "complete()" if the locks are acquired in the wrong order).
    assert write_started.wait(10)

    completed = threading.Event()

    def complete():
        logger.complete()
        completed.set()

    completer_thread = threading.Thread(target=complete, daemon=True)
    completer_thread.start()

    time.sleep(0.5)
    finish_write.set()

    writer_thread.join(10)
    completer_thread.join(10)

    assert not writer_thread.is_alive()
    assert not completer_thread.is_alive()
    assert completed.is_set()


@pytest.mark.parametrize("enqueue", [False, True])
def test_complete_concurrent_with_contextualize(enqueue):
    written = []
    written_lock = threading.Lock()

    class Sink:
        def write(self, message):
            # Simulate a sink which needs the core lock while writing (e.g. because it
            # uses "contextualize()" or synchronizes with a thread that does).
            with logger.contextualize(sink=True):
                pass
            with written_lock:
                written.append(str(message))

    logger.add(Sink(), format="{message}:{extra[seed]}", enqueue=enqueue, catch=False)

    def log_messages(seed):
        for i in range(20):
            with logger.contextualize(seed=seed):
                logger.info("{}", i)

    threads = [
        threading.Thread(target=log_messages, args=(seed,), daemon=True) for seed in range(4)
    ]

    for thread in threads:
        thread.start()

    while any(thread.is_alive() for thread in threads):
        logger.complete()

    for thread in threads:
        thread.join(10)

    logger.complete()

    expected = {"%d:%d" % (i, seed) for seed in range(4) for i in range(20)}
    assert {message.strip() for message in written} == expected


@pytest.mark.skipif(os.name == "nt", reason="Windows does not support forking")
def test_complete_with_child_process_and_concurrent_sink_write(tmp_path, fork_context):
    output = tmp_path / "output.log"

    with output.open("w") as file:

        class Sink:
            def write(self, message):
                # The sink needs the core lock while writing, which must not prevent
                # "complete()" (called from both the parent and the child process) from
                # progressing, as the messages are written by the parent process.
                with logger.contextualize(sink=True):
                    pass
                file.write(str(message))
                file.flush()

        logger.add(Sink(), context=fork_context, format="{message}", enqueue=True, catch=False)

        process = fork_context.Process(target=child_process_log_and_complete)
        process.start()

        for i in range(10):
            logger.info("Main {}", i)
            logger.complete()

        process.join(30)
        assert process.exitcode == 0

        logger.complete()

    lines = output.read_text().splitlines()
    expected = ["Main %d" % i for i in range(10)] + ["Child %d" % i for i in range(10)]
    assert sorted(lines) == sorted(expected)
