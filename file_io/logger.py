from datetime import datetime


class Logger(object):
    @staticmethod
    def get_timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_message_with_prefix(prefix: str, message: str) -> str:
        return Logger.get_timestamp() + " " + prefix + ": " + message

    @staticmethod
    def get_debug_log(message: str) -> str:
        if __debug__:
            return Logger.get_message_with_prefix("[DEBUG]", message)
        else:
            return ''

    @staticmethod
    def get_warning_log(message: str) -> str:
        return Logger.get_message_with_prefix("[WARNING]", message)

    @staticmethod
    def get_error_log(message: str) -> str:
        return Logger.get_message_with_prefix("[ERROR]", message)

    @staticmethod
    def get_log(message: str) -> str:
        return Logger.get_timestamp() + " " + message
