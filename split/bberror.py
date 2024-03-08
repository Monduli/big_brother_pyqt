import sys
from traceback import format_exception


class BBError(Exception):
    def __init__(self, original_exception, big_brother):
        self.original_exception = original_exception
        self.big_brother = big_brother

    def __str__(self):
        error_message = ""

        try:
            error_message += f"\n*** Big Brother Simulation Error ***\n\n"
            error_message += f"Error occurred in: {sys._getframe(1).f_code.co_name}\n"
        except Exception as e:
            error_message += f"\nError occurred while getting the error location: {str(e)}\n"

        try:
            error_message += f"Current Houseguests: {', '.join([hg.name for hg in self.big_brother.houseguests])}\n\n"
        except Exception as e:
            error_message += f"\nError occurred while getting the current houseguests: {str(e)}\n"

        try:
            error_message += f"Error: {type(self.original_exception).__name__}\n\n"
        except Exception as e:
            error_message += f"\nError occurred while getting the original exception type: {str(e)}\n"

        try:
            error_message += f"Original Exception Traceback:\n{''.join(format_exception(type(self.original_exception), self.original_exception, self.original_exception.__traceback__))}\n\n"
        except Exception as e:
            error_message += f"\nError occurred while getting the original exception traceback: {str(e)}\n"

        try:
            error_message += f"Current Game State:\n"
            error_message += f"- Head of Household: {self.big_brother.HOH.name if self.big_brother.HOH else 'None'}\n"
        except Exception as e:
            error_message += f"\nError occurred while getting the Head of Household: {str(e)}\n"

        try:
            error_message += f"- Nominees: {', '.join([n.name for n in self.big_brother.nominees]) if self.big_brother.nominees else 'None'}\n"
        except Exception as e:
            error_message += f"\nError occurred while getting the Nominees: {str(e)}\n"

        try:
            error_message += f"- Veto Winner: {self.big_brother.veto_winner.name if self.big_brother.veto_winner else 'None'}\n"
        except Exception as e:
            error_message += f"\nError occurred while getting the Veto Winner: {str(e)}\n"

        try:
            error_message += f"- Evicted: {self.big_brother.evicted.name if self.big_brother.evicted else 'None'}\n"
        except Exception as e:
            error_message += f"\nError occurred while getting the Evicted houseguest: {str(e)}\n"

        return error_message.strip()