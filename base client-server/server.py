import socket
import threading
import time

class server:
   def __init__(self):
       ## Varia costanti
       self.PORT = 9090
       self.IP = socket.gethostbyname(socket.gethostname())
       self.ADDR = (self.IP, self.PORT)
       self.LEN_MSG = 64
       self.FORMAT = "utf-8"
       self.special_msg = \
           {
               "exit" : "!DISCONNECT",
               "alive" : "!ALIVE"
           }
       self.connections = []
       ## Avvio il controllo delle connessioni
       self.thread_conn = threading.Thread(target=self.connection_control)
       self.thread_conn.start()
       ## Settaggio del server
       print("[SERVER] starting")
       self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       ## Assegno al server ip e porta
       self.server.bind(self.ADDR)
       self.recive()


   def recive(self):
       ## Inizio accettare le connessioni
       self.server.listen()
       print("[SERVER] listening on " + str(self.IP) + " with port " + str(self.PORT))
       while True:
           ## Aspetto finchè non arrivano
           conn, addr = self.server.accept()
           Task = threading.Thread(target=self.client_had, args=(conn, addr)).start()
           ## Aggiungo tutte le informazioni in un dizionario
           self.connections.append({"conn": conn,"addr" : addr , "task" : Task, "last_check" : time.time(), "time" : 0})

       print("[SERVER] disconnect")



   def send(self, msg, conn, addr, type):
       ## Se è un immagine, passa il nome.
       if type == "T":
           message = msg.encode(self.FORMAT)
       elif type == "I":
           img = open(msg, 'rb')
           message = img.read()
           img.close()
       send_len = ( type + str(len(message))).encode(self.FORMAT)
       ## Per raggiugnere i 64
       send_len += b' ' * (self.LEN_MSG - len(message))
       print("[SERVER][SENDING] msg {} {}".format(addr, msg))
       try:
           conn.send(send_len)
           time.sleep(0.5)
           conn.send(message)
       except OSError:
           pass

   def client_had(self, conn, addr):
       print("[CLIENT] new {}".format(addr))
       connected = True
       while connected:
           try:
               msg_len = conn.recv(self.LEN_MSG).decode(self.FORMAT)
               ## Se è un effettivo messaggio
               if msg_len:
                   ## Aggiungo che è vivo
                   id = [i for i in self.connections if i["conn"] == conn][0]

                   index = self.connections.index(id)
                   self.connections[index]["time"] = 0
                   self.connections[index]["last_check"] = time.time()
                   ## Decodifico messaggio
                   msg = conn.recv(int(msg_len)).decode(self.FORMAT)
                   print(f"[CLIENT][RECIVE] {addr} {msg}")
                   if msg == self.special_msg["exit"]:
                       connected = False
           except:
               print("[CLIENT] connection lost {}".format(addr))
               break
       id = [i for i in self.connections if i["conn"] == conn][0]
       index = self.connections.index(id)
       self.connections.pop(index)
       print("[CLIENT] exit {}".format(addr))
       conn.close()


   def connection_control(self):
       rimuovi = []
       while True:
           for i in self.connections:
               time_now = time.time()
               ## Se non si hanno notizie da almeno 10 secondi
               if time_now - i["last_check"] > 10:
                   print("[CLIENT] invio alive {}".format(i["addr"]))
                   self.send(self.special_msg["alive"],i["conn"],i["addr"],"T")
                   i["time"] += 1
                   ## Se non risponde da 3 volte
                   if i["time"] == 4:
                       print("[CLIENT] non risponde da {} {}".format(i["time"],i["addr"]))
                       ## chiudo la connessione
                       i["conn"].close()
                       ## Rimuovo il task
                       del i["task"]
                       ## Rimuovo dalla lista
                       rimuovi.append(i["addr"])
           time.sleep(10)
           ## Se ci sono connessioni da rimuovere, rimuoviamole
           if rimuovi:
               cont = []
               for i, j in enumerate(rimuovi):
                   if self.connections[i]["addr"] == j:
                       cont.append(i)
               for i in reversed(cont):
                   self.connections.pop(i)
               rimuovi = []


if __name__ == "__main__":
   server_cnt = server()

