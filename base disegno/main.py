from tkinter import *
import numpy as np
from PIL import Image, ImageDraw, ImageTk
import time
from tkinter import filedialog
## Elenco colori
colori = {
    "bianco_rgb" : (255,255,255),
    "nero_rgb" : (0,0,0),
    "bianco_hex" : "#fff",
    "nero_hex" : "#000",
    "verde_rgb" : (0, 255, 0),
    "verde_hex" : "#00FF00"
}

class main_window:
    def __init__(self, root):
        self.root = root
        ## Configurazioni basi della schermata
        self.windows_default()
        ## Configuro il binding
        self.binding()
        ## Varie disegni default
        self.default_draw()


    def windows_default(self):
        ## Dimensioni
        self.altezza = 600
        self.larghezza = 800
        ## Creazione del canvas
        self.canvas = Canvas(self.root, width=self.larghezza, height=self.altezza, background="black", bd = 0, highlightthickness=0)
        ## Creazione del file dove annotiamo tutte le modifiche al canvas (per le collisioni)
        self.image1 = Image.new("RGB", (self.larghezza, self.altezza), colori["nero_rgb"])
        self.draw = ImageDraw.Draw(self.image1)
        self.canvas.grid(row=0, column=0)

    def binding(self):
        ## Opzione selezionata
        self.opzione_disegno = 'c'
        ## Binding mouse
        self.canvas.bind("<Button-1>", self.sinistro)
        self.canvas.bind("<Button-2>", self.destro)
        ## Movimento
        self.root.bind("<Motion>", self.motion)
        ## Binding tastiera
        self.root.bind_all('<Key>', self.key)
        ## Configurazione raggio del cerchio
        ### Sensibilità raggio
        self.sens = 2
        ## Raggio iniziale
        self.r = self.sens * 10
        ## Automatizzazione
        self.aut = False
        ## Detect collisioni
        self.detect_coll = False
        ## Configurazioni per il rettangolo
        self.resetta_rettangolo()

    def key(self, key):
        ## Se la key è + allora aumenta il raggio del cerchio
        if key.char == '+':
            if self.r <= 100 - self.sens:
                self.r += self.sens
        ## Se la key è - allora diminuisci il raggio del cerchio
        elif key.char == '-':
            if self.r >= self.sens:
                self.r -= self.sens
        ## Attivo la modalità automatica
        elif key.char == 'a':
            self.aut = not self.aut
        ## Attivo modalità detect collisioni
        elif key.char == 'd':
            self.detect_coll = not self.detect_coll
            ## Crea lista mappa
            self.mappa = np.array(self.image1, dtype=int)
        ## Raggruppo la tastiera qua dentro
        else:
            '''
                Opzioni valide:
                r = Crea rettangolo
                q = Crea quadrato dato 1 punto
                p = Crea poligono
                l = Crea linea
                c = Crea cerchio
            '''
            self.opzione_disegno = key.char
            ## Resetto vari punti precedenti
            self.resetta_rettangolo()

        self.info_opz()
    ## Ogni volta che si muove il mouse
    def motion(self, event):
        ## Controlla se la modalità automatica è attiva
        if self.aut:
            ## Se si allora controlla
            self.standard_1_punt0(event.x, event.y, self.opzione_disegno)
        ## Controlla se la modalità collisioni è attiva
        if self.detect_coll:
            try:
                ## Se si stampa che colore è sul momento
                print(self.mappa[event.y, event.x])
            except IndexError as e:
                print("Fuori dall'immagine")

    ## Detect tasto sinistro
    def sinistro(self, event):
        ## Prendo coordinate
        x = event.x
        y = event.y
        ## Se non è ai confini
        if x >= self.larghezza - 100 or y >= self.altezza -40:
            ## Se è salva o carica
            if y >= self.altezza - 80:
                ## Se è salva
                if x <= 80:
                    self.salva()
                ## Se è carica
                if x >= self.larghezza - 80:
                    self.carica()
        else:
            ## Se è cerchio
            if self.opzione_disegno == 'c':
                self.standard_1_punt0(x, y, 'c')
            ## Se è rettangolo
            elif self.opzione_disegno == 'r':
                self.rettangolo(x, y)
            ## Se è quadrato
            elif self.opzione_disegno == 'q':
                self.standard_1_punt0(x, y, 'q')
            ## Se è poligono
            elif self.opzione_disegno == 'p':
                self.poligono(x,y)
            ## Se è la linea
            elif self.opzione_disegno == 'l':
                self.linea((x,y))

    def linea(self, val):
        self.n_punti += 1
        ## Se non è stato preso un valore precedente
        if self.x0 == -1:
            self.x0 = val
        ## Senò disegna
        else:
            self.canvas.create_line([self.x0, val], fill = colori["verde_hex"])
            self.draw.line([self.x0, val], fill = colori["verde_rgb"])
            ## Resetta
            self.resetta_rettangolo()
        ## aggiorna
        self.info_opz()


    ## Main per il disegno di un poligono
    def poligono(self, x, y):
        ## Aumento conteggio dei punti presi
        self.n_punti += 1
        ## Controllo i vari punti precedenti
        if self.x0 == -1:
            self.x0 = (x, y)
        elif self.y0 == -1:
            self.y0 = (x,y)
        elif self.x1 == -1:
            self.x1 = (x,y)
        ## Se tutti sono già stati scritti
        else:
            ## Disegna
            self.disegna_poligono((x,y))
            ## Resetta
            self.resetta_rettangolo()
        ## Aggiorna
        self.info_opz()

    def disegna_poligono(self, y1):
        self.canvas.create_polygon([self.x0, self.y0, self.x1, y1], fill = colori["bianco_hex"], outline = colori["bianco_hex"])
        self.draw.polygon([self.x0, self.y0, self.x1, y1], colori["bianco_rgb"], colori["bianco_rgb"])

    def destro(self, event):
        pass
    ## Resetta valori per rettangolo e poligono
    def resetta_rettangolo(self):
        self.n_punti = 0
        self.x0 = self.y0 = self.x1 = -1

    ## Responsabile disegno rettangolo
    def rettangolo(self, x, y):
        self.n_punti += 1
        ## Se prima non è mai stato disegnato
        if self.x0 == -1:
            self.x0 = x
            self.y0 = y
        ## Se prima aveva già preso dei punti
        else:
            ## Disegno
            self.canvas.create_rectangle(self.x0, self.y0, x, y, fill = colori["bianco_hex"], outline = colori["bianco_hex"])
            self.draw.rectangle([self.x0, self.y0, x, y], colori["bianco_rgb"], colori["bianco_rgb"])
            ## Resetta
            self.resetta_rettangolo()
        ## Aggiorna
        self.info_opz()

    def standard_1_punt0(self,x,y,tipo):
        ## Prendi i confini del cerchio
        x0 = x - self.r / 2
        y0 = y - self.r / 2
        x1 = x + self.r / 2
        y1 = y + self.r / 2
        ## Se è cerchio
        if tipo == 'c':
            self.cerchio(x0, y0, x1, y1)
        ## Se è quadrato
        elif tipo == 'q':
            self.quadrato(x0, y0, x1, y1)

    ## Disegno del cerchio
    def cerchio(self, x0, y0, x1, y1):
        ## Disegna
        self.canvas.create_oval(x0, y0, x1, y1, fill=colori["bianco_hex"], outline=colori["bianco_hex"])
        self.draw.ellipse([x0, y0, x1, y1], colori["bianco_rgb"], colori["bianco_rgb"])

    ## Disegno del quadrato
    def quadrato(self, x0, y0, x1, y1):
        self.canvas.create_rectangle(x0, y0, x1, y1, fill = colori["bianco_hex"], outline = colori["bianco_hex"])
        self.draw.rectangle([x0, y0, x1, y1], fill = colori["bianco_rgb"], outline=colori["bianco_hex"])

    ## Disegni default
    def default_draw(self):
        self.info_opz()
        self.salva_btn()
        self.carica_btn()

    ## Bottone per il salvataggio
    def salva_btn(self):
        self.canvas.create_rectangle(0, self.altezza - 40, 75, self.altezza, fill = colori["bianco_hex"])
        self.canvas.create_text(35, self.altezza - 20, text = "Salva")

    ## Bottone per il caricamento
    def carica_btn(self):
        self.canvas.create_rectangle(self.larghezza - 75, self.altezza - 40, self.larghezza, self.altezza, fill = colori["bianco_hex"])
        self.canvas.create_text(self.larghezza - 40, self.altezza - 20, text = "Carica")

    ## Lista in alto e sinistra
    def info_opz(self):
        ## Disegno area
        self.canvas.create_rectangle(self.larghezza - 100, 100, self.larghezza + 10, 0, fill = colori["bianco_hex"])
        ## Titolo
        self.canvas.create_text(self.larghezza - 50, 15, text = "Opzioni:")
        ## Raggio
        self.canvas.create_text(self.larghezza - 50, 30, text = "Raggio: {}".format(self.r))
        ## Selezione corrente
        self.canvas.create_text(self.larghezza - 50, 45, text = "Selezione: {}".format(self.opzione_disegno))
        ## Modalità automatica
        self.canvas.create_text(self.larghezza - 50, 60, text = "Auto: {}".format(self.aut))
        ## Modalità collisioni
        self.canvas.create_text(self.larghezza - 50, 75, text="Coll: {}".format(self.detect_coll))
        ## Numero punti
        self.canvas.create_text(self.larghezza - 50, 90, text="Punti: {}".format(self.n_punti))

    def salva(self):
        self.image1.save("preview{}.png".format(str(time.time()).replace('.','')))

    def carica(self):
        ## Prendo il nome del file
        name = self.openfilename()
        ## Apro l'immagine
        self.image1 = Image.open(name)
        ## Faccio il riferimento a chi dovrò scrivere
        self.draw = ImageDraw.Draw(self.image1)
        ## La rendo compatibile siccome è un png
        img_out = ImageTk.PhotoImage(self.image1)
        ## Aggiungo al canvas
        self.canvas.create_image(0, 0, anchor=NW, image=img_out)
        ## Salvataggio dell'immagine
        self.canvas.image = img_out
        ## Disegno elemetni standard
        self.default_draw()

    def openfilename(self):
        # open file dialog box to select image
        # The dialogue box has a title "Open"
        filename = filedialog.askopenfilename(title='"pen')
        return filename


root = Tk()
gui = main_window(root)
gui.canvas.mainloop()
