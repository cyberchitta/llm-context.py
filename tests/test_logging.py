import logging

from llm_context.exec_env import MessageCollector


def test_message_collector():
    messages = []
    collector = MessageCollector(messages)
    logger = logging.getLogger("test")
    logger.addHandler(collector)
    logger.setLevel(logging.INFO)

    test_msg = "Test message"
    logger.info(test_msg)

    assert messages == [test_msg]
