from threading import Thread
import functools


class TimeoutException(BaseException):
    def __init__(self, msg=None):
        #: The message from the remark tag or element
        self.msg = msg

    def __str__(self):
        if self.msg is None:
            return "No error message provided"
        if not isinstance(self.msg, str):
            return str(self.msg)
        return self.msg


def timeout(seconds_before_timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [TimeoutException('timeout [%s seconds] exceeded!' % seconds_before_timeout)]

            def new_func():
                try:
                    res[0] = func(*args, **kwargs)
                except TimeoutException as e:
                    res[0] = e
            t = Thread(target=new_func)
            t.daemon = True
            try:
                t.start()
                t.join(seconds_before_timeout)
            except TimeoutException as e:
                print('error starting thread')
                raise e
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco