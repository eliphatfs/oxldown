from kubetk.helpers import rpc_server
import threading


class LogServer(object):
    
    def __init__(self) -> None:
        self.write_lock = threading.Lock()

    def add_log(self, s):
        with self.write_lock:
            fo.write(s)
            fo.write("\n")


if __name__ == '__main__':
    logserver = LogServer()
    with open("meta.jsonl", "a") as fo:
        with rpc_server.threaded(9000) as server:
            server.register_introspection_functions()
            server.register_multicall_functions()
            server.register_function(logserver.add_log)
            server.serve_forever(0.5)
