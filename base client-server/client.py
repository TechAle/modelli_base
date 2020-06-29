import socket
import threading
from PIL import Image
from io import BytesIO

class client:
    def __init__(self, port,ip):
        ## Variabili costanti
        self.PORT = port
        self.IP = ip
        self.ADDR = (self.IP, self.PORT)
        self.LEN_MSG = 64
        self.FORMAT = "utf-8"
        ## Tutti i vari messaggi speciali
        self.special_msg = \
        {
            ## Messaggio di disconnessione
            "exit" : "!DISCONNECT",
            ## Messaggio che dice che la connessione è ancora attiva
            "alive" : "!ALIVE",
            ## Ricevo gli account disponibili
            "getAcc" : "!GETACCOUNT"
        }
        ## Settaggio client
        print("[CLIENT] starting")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ## Connetto il client
        print("[CLIENT] searching for a server")
        self.client.connect(self.ADDR)
        print("[CLIENT] server found {}".format(self.ADDR))
        ## Avvio il task per ricevere
        self.reciveTask = threading.Thread(target = self.recive)
        self.reciveTask.start()


    ## Riceve in input un messaggio e lo invia al server
    def send(self, msg):
        print("[CLIENT] sending " + msg)
        message = msg.encode(self.FORMAT)
        send_len = str(len(message)).encode(self.FORMAT)
        ## Per raggiungere i 64
        send_len += b' ' * (self.LEN_MSG - len(send_len))
        self.client.send(send_len)
        self.client.send(message)

    ## Riceve un messaggio dal server
    def recive(self):
        connected = True
        while connected:
            try:
                ## The format is this: I/T + Len
                msg_len = self.client.recv(self.LEN_MSG).decode(self.FORMAT)
                if msg_len and msg_len.strip().__len__() != 0:
                    ## If contains text
                    if msg_len[0] == 'T':
                        msg = self.client.recv(int(msg_len[1:])).decode(self.FORMAT)
                        print("[SERVER][RECEIVED] text " + msg)
                        self.case(msg)
                    ## If contains image
                    elif msg_len[0] == 'I':
                        print("[SERVER][RECEIVING] reciving img with len " + msg_len)
                        ## Recive msg
                        msg = b""
                        recive = "a"
                        ## Ogni immagine finisce con IEND
                        while not str(recive).__contains__("IEND"):
                            recive = self.client.recv(int(msg_len[1:]))
                            if recive:
                                msg += recive
                        ## Trasformazioni per poi vederla
                        stream = BytesIO(msg)
                        image = Image.open(stream).convert("RGBA")
                        stream.close()
                        image.show()
                        print("[SERVER][RECEIVED] img")

            ## Nel caso il server abbia perso la connessione
            except ConnectionResetError or BrokenPipeError:
                print("[SERVER] connection lost")
                ## Elimino il thread per ricevere
                del self.reciveTask
                break
    ## Analizza i vari casi
    def case(self, msg):
        ## Se è una richiesta se è vivo, allora dì che sei vivo
        if msg == self.special_msg["alive"]:
            self.send(self.special_msg["alive"])
## Avvia il client
if __name__ == "__main__":
    main_clt = client(9090, "192.168.1.119")
