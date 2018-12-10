import socket
import select
import time
import sys


def usage():
    print("syntax : http_proxy <port>")
    print("sample : http_proxy 8080")

def main():
    # syntax error
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    host = "localhost"
    port = sys.argv[1]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, int(port)))
    server_socket.listen(10)
    # we don't need input
    connection_list = [server_socket]

    while connection_list:
        try:
            # rlist => read_socket: wait until ready for reading
            # wlist => write_socket: wait until ready for writing
            # xlist => error_socket: wait for an exceptional condition
            # unlock blocking state per 10seconds
            read_socket, write_socket, error_socket = select.select(connection_list, [], [], 10)

            for ob in read_socket:
                # new request
                if ob == server_socket:
                    (client_socket, address) = server_socket.accept()
                    connection_list.append(client_socket)
                    print("New client %s is connected." % address[0])

                # any data from client
                else:
                    data = ob.recv(4096).decode()
                    if data:
                        print("I got the message from client %s." % address[0])
                        # get request and try to send it to server
			# find Host field                        
			indx = data.index("Host")
                        where = data[indx+6:]
                        url = where.split("\r\n")[0]
                        
			try:
                            web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            web_socket.connect((url, 80))
                            web_socket.send(data.encode())
                        except:
                            ob.send("you cannot connect web server")
                            break

                        while True:
                            response = web_socket.recv(65536)
                            if response:
                                ob.send(response)
                            else:
                                web_socket.close()
                                break

        
                    # if client broke the connection
                    else:
                        connection_list.remove(ob)
                        print("A connection with client %s is disconnected." % address[0])
                        ob.close()

        except KeyboardInterrupt:
            server_socket.close()
            sys.exit(1)

if __name__ == "__main__":
    main()

