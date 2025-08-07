"""Utility functions and classes for Keck DRP primitives."""

class DummyAction:
    def __init__(self, args=None):
        self.args = args or {}
        self.action_type = "dummy"
        self.timestamp = None
        self.context = None
        self.logger = None

class DummyContext:
    def __init__(self, logger=None, config=None):
        import logging
        self.logger = logger or logging.getLogger("dummy_logger")
        self.config = config or {}
