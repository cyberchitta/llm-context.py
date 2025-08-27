class LLMContextError(Exception):
    def __init__(self, message: str, error_type: str):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


class RuleResolutionError(LLMContextError):
    def __init__(self, message: str):
        super().__init__(message, "RULE_RESOLUTION_ERROR")
