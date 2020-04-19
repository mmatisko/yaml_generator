from datetime import datetime
import io
import sys


class Logger(object):
    @staticmethod
    def __get_timestamp() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def __get_message_with_prefix(prefix: str, message: str) -> str:
        return Logger.__get_timestamp() + ' ' + prefix + ': ' + message + '\n'

    @staticmethod
    def get_log(message: str) -> str:
        return Logger.__get_timestamp() + ' ' + message

    @staticmethod
    def write_log(message: str, stream: io.FileIO = sys.stdout):
        stream.write(Logger.__get_message_with_prefix("", message))

    @staticmethod
    def write_debug_log(message: str, stream: io.FileIO = sys.stdout):
        return stream.write(Logger.__get_message_with_prefix('[DEBUG]', message) if __debug__ else '')

    @staticmethod
    def write_warning_log(message: str, stream: io.FileIO = sys.stdout):
        return stream.write(Logger.__get_message_with_prefix("[WARNING]", message))

    @staticmethod
    def write_error_log(message: str, stream: io.FileIO = sys.stdout):
        return stream.write(Logger.__get_message_with_prefix("[ERROR]", message))
