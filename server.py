import socket
import threading
import logging

HOST = "0.0.0.0"
PORT =int(input("Enter server port : "))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def handle_client(client_socket, address):
    logging.info(
        f"[*] Client IP : {address[0]} PORT :{address[1]}"
    )

    with client_socket:
        client_socket.settimeout(30)

        try:
            while True:
                data = client_socket.recv(4096)

                if not data:
                    break

                message = data.decode("utf-8", errors="replace")

                logging.info(
                    f"Received from {address}: {message}"
                )

                client_socket.sendall(b"ACK\r\n")

        except socket.timeout:
            logging.info(
                f"Client timeout: {address}"
            )

        except ConnectionResetError:
            logging.info(
                f"Client disconnected unexpectedly: {address}"
            )

        except Exception as e:
            logging.error(
                f"Client error {address}: {e}"
            )

    logging.info(
        f"Client disconnected: {address}"
    )


def main():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))
    server.listen(10)

    logging.info(
        f"Listening on {HOST}:{PORT}"
    )

    try:
        while True:

            client_socket, address = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )

            thread.start()

    except KeyboardInterrupt:
        logging.info("Server shutting down")

    finally:
        server.close()


if __name__ == "__main__":
    main()