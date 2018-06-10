import os
import threading

_counter_lock = threading.Lock()
_counter = 0
_prefix = None

__all__ = ["choose_boundary"]


def _get_next_counter():
    global _counter
    _counter_lock.acquire()
    _counter += 1
    result = _counter
    _counter_lock.release()
    return result


def choose_boundary():
    """Return a string usable as a multipart boundary.
    The string chosen is unique within a single program run, and
    incorporates the user id (if available), process id (if available),
    and current time.  So it's very unlikely the returned string appears
    in message text, but there's no guarantee.
    The boundary contains dots so you have to quote it in the header."""

    global _prefix
    import time
    if _prefix is None:
        import socket
        try:
            hostid = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            hostid = '127.0.0.1'
        try:
            uid = repr(os.getuid())
        except AttributeError:
            uid = '1'
        try:
            pid = repr(os.getpid())
        except AttributeError:
            pid = '1'
        _prefix = hostid + '.' + uid + '.' + pid
    return "%s.%.3f.%d" % (_prefix, time.time(), _get_next_counter())
