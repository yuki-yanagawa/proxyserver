import socket
import signal

def main():
    signal.signal(signal.SIGINT,signal.SIG_DFL)
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(("localhost",8888))
    data = sock.recv(4096)
    print(data)


if __name__ == "__main__":
    main()