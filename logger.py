from datetime import datetime


class Logger(object):
    def __init__(self):
        print("Logger has started...")

    @staticmethod
    def get_timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_message_with_prefix(self, prefix: str, message: str) -> str:
        return self.get_timestamp() + " " + prefix + ": " + message

    def get_debug_log(self, message: str) -> str:
        return self.get_message_with_prefix("[DEBUG]", message)

    def get_warning_log(self, message: str) -> str:
        return self.get_message_with_prefix("[WARNING]", message)

    def get_error_log(self, message: str) -> str:
        return self.get_message_with_prefix("[ERROR]", message)

    def get_log(self, message: str) -> str:
        return self.get_timestamp() + " " + message
