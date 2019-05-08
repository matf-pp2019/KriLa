#!/usr/bin/env python3

# Uključivanje sistemskog modula, kao i
# modula za rad sa datotečnim sistemom
from sys import exit as greška
from os.path import join as put

# Uključivanje grafičkog modula
from tkinter import Tk, Menu, LabelFrame, Canvas, Button, \
                    PhotoImage, Label, Entry, IntVar, StringVar, \
                    Checkbutton, OptionMenu, Radiobutton

# Uključivanje pomoćnog modula za
# kutijice sa iskačućim porukama
from tkinter.messagebox import showinfo, showerror, askyesno

# Uključivanje modula za nalazak konveksnog omotača
from omot import konveksni_omot

# Uključivanje funkcionalnog modula
from functools import partial

# Uključivanje modula sa operatorima
from operator import mul, itemgetter as ig

# Uključivanje matematičkog modula
from math import isnan

# Uključivanje geometrijskog modula
from geom import *

# Nosilac programa je klasa GeoDemonstrator, koja
# nasleđuje grafičku klasu Tk iz modula tkinter
class GeoDemonstrator(Tk):
  # Konstruktor aplikacije
  def __init__(self):
    # Log poruka o pokretanju aplikacije
    print('Dobro došli u aplikaciju GeoDemonstrator!')
    
    # Pozivanje konstruktora roditeljske klase
    super().__init__()
    
    # Postavljanje naziva aplikacije
    self.title('GeoDemonstrator')
    
    # Inicijalizacija liste tačaka
    self.tačke = []
    self.ttačke = []
    
    # Trenutna transformacija
    self.tr = ''
    
    # Indikator inverzne transformacije
    self.inv = False
    
    # Inicijalizacija liste identifikatora
    # na platnu trenutno iscrtanih tačaka
    self.id_tač = []
    
    # Inicijalizacija figure
    self.figura = None
    
    # Inicijalizacija transformacija iz platna
    # u iscrtani koordinatni sistem i obrnuto
    self.puk = Skal(1/7, -1/7) * Trans(-204, -132)
    self.kup = Trans(204, 132) * Skal(7, -7)
    
    # Inicijalizacija elemenata GKI
    self.init_gki()
  
  # Inicijalizacija elemenata GKI
  def init_gki(self):
    # Postavljanje veličine i pozicije prozora
    self.geometry('450x450+75+75')
    
    # Onemogućavanje promene veličine prozora,
    # pošto je Tk prilično plastičan, pa promene
    # ugrožavaju zamišljeni izgled aplikacije
    self.resizable(False, False)
    
    # Inicijalizacija glavnog menija
    self.init_meni()
    
    # Inicijalizacija platna
    self.init_platno()
    
    # Kontrola unosa tačaka
    self.init_unos()
      
  # Inicijalizacija glavnog menija
  def init_meni(self):
    # Pravljenje glavnog menija
    meni = Menu(self)
    
    # Postavljanje sporednog padajućeg menija
    self.umeni = Menu(meni)
    self.umeni.add_command(label = 'Zaključi unos',
                           command = self.promena_unosa)
    self.umeni.add_command(label = 'Ispravi figuru',
                           command = self.ispravi)
    self.umeni.add_command(label = 'Očisti platno',
                           command = self.novo_platno)
    
    # Postavljanje glavnog menija i vezivanje
    # komandi za odgovarajuće funkcionalnosti
    meni.add_cascade(label = 'Opcije', menu = self.umeni)
    meni.add_command(label = 'Info (F1)', command = self.info)
    meni.add_command(label = 'Kraj (Esc)', command = self.kraj)
    self.config(menu = meni)
    
    # Vezivanje tipki za akcije analogne
    # onima iz prethodno postavljenog menija
    self.bind('<F1>', self.info)
    self.bind('<Escape>', self.kraj)
    
    # Vezivanje protokola zatvaranja prozora
    # za istu akciju kao za Kraj i Escape
    self.protocol('WM_DELETE_WINDOW', self.kraj)
  
  # Inicijalizacija platna
  def init_platno(self):
    # Pravljenje okvira za platno
    okvir_p = LabelFrame(self, text = 'Zakoračite u svet geometrijskih'
                           ' transformacija', padx = 10, pady = 10)
    okvir_p.place(x = 10, y = 10,
                  height = 300, width = 430)
    
    # Postavljanje platna unutar okvira
    self.platno = Canvas(okvir_p, height = 261, width = 405)
    self.platno.place(x = 0, y = 0)
    
    # Postavljanje koordinatnog sistema na platno;
    # slika nije lokalna promenljiva, pošto bi je u
    # tom slučaju 'pojeo' sakupljač otpadaka
    self.slika = PhotoImage(file = put('..', 'slike', 'koord.gif'))
    self.platno.create_image(203, 131, image = self.slika)

    # Vezivanje čuvanja tačke za klik na platno
    self.unos = True
    self.platno.bind('<Button-1>', self.dodaj_tačku)
  
  # Funkcija za dohvatanje vrednosti promenljive; pokušava
  # se evaluacija vrednosti ili ispaljuje izuzetak
  def uzmi_prom(self, prom):
    try:
      if prom == 'x':
        return float(eval(self.x_koord.get()))
      elif prom == 'y':
        return float(eval(self.y_koord.get()))
      elif prom == 'u':
        return float(eval(self.ugao.get()))
      elif prom == 't1':
        return float(eval(self.t1_koord.get()))
      else:
        return float(eval(self.t2_koord.get()))
    except:
      showerror('Greška', 'Loši parametri transformacije!')
      return float('nan')
  
  # Funkcija za transformisanje kreiranog poligona
  def transformiši(self):
    # Nije moguće transformisati prazan skup tačaka
    if not self.ttačke:
      showerror('Greška', 'Unesite tačke na platno!')
      return
    
    # Neophodno je da transformacija bude odabrana
    if not self.tr:
      showerror('Greška', 'Izaberite transformaciju!')
      return
    
    # Neophodno je odabrati centar transformacije
    if self.tr != 'translacija' and \
       not self.centar_transformacije:
      showerror('Greška', 'Izaberite centar transformacije!')
      return
    
    # Rotacija i refleksija moraju da dobiju ugao
    if self.tr in ('rotacija', 'refleksija'):
      if not self.ugao.get():
        showerror('Greška', 'Unesite parametre transformacije!')
        return
      
      # Izračunavanje parametra rot/refl
      if self.inv:
        u = -self.uzmi_prom('u')
      else:
        u = self.uzmi_prom('u')
      
      # Propagacija greške u izračunavanju
      if isnan(u): return
      
      # Izračunavanje transformacije na osnovu centra
      if self.centar_transformacije == 'oko koordinatnog početka':
        transformacija = (self.funkcije[self.tr])(u)
      else:
        # Greška ako nisu uneti t1 i t2
        if not self.t1_koord.get() or not self.t2_koord.get():
          showerror('Greška', 'Unesite parametre transformacije!')
          return
        
        # Izračunavanje parametra transformacije
        # i eventualna propagacija greške u računu
        t1 = self.uzmi_prom('t1')
        if isnan(t1): return
        t2 = self.uzmi_prom('t2')
        if isnan(t2): return
        
        transformacija = (self.funkcije[self.tr])(u, t1, t2)
    else:
      # Greška ako nisu uneti x i y
      if not self.x_koord.get() or not self.y_koord.get():
        showerror('Greška', 'Unesite parametre transformacije!')
        return
      
      # Izračunavanje parametra transformacije
      if not self.inv:
        x = self.uzmi_prom('x')
        if isnan(x): return
        y = self.uzmi_prom('y')
      elif self.tr == 'skaliranje':
        x = self.uzmi_prom('x')
        if isnan(x): return
        y = self.uzmi_prom('y')
        
        # Obrada aritmetičke greške
        if x == 0 or y == 0:
          showerror('Greška', 'Deljenje nulom pri inverznom skaliranju!')
          return
        
        # Inverzno skaliranje
        x = 1/x
        y = 1/y
      else:
        x = -self.uzmi_prom('x')
        if isnan(x): return
        y = -self.uzmi_prom('y')
      
      # Propagacija greške u izračunavanju
      if isnan(y): return
      
      if self.tr == 'translacija' or \
         self.centar_transformacije == 'oko koordinatnog početka':
        transformacija = (self.funkcije[self.tr])(x, y)
      else:
        # Greška ako nisu uneti t1 i t2
        if not self.t1_koord.get() or not self.t2_koord.get():
          showerror('Greška', 'Unesite parametre transformacije!')
          return
        
        # Izračunavanje parametra transformacije
        # i eventualna propagacija greške u računu
        t1 = self.uzmi_prom('t1')
        if isnan(t1): return
        t2 = self.uzmi_prom('t2')
        if isnan(t2): return
        
        transformacija = (self.funkcije[self.tr])(x, y, t1, t2)
    
    # Nove transformisane tačke u
    # koordinatnom sistemu sa slike
    nttačke = list(map(partial(mul, transformacija), self.ttačke))
    
    # Provera da li su tačke otišle van koordinatnog
    # sistema sa slike tj. vidljivog dela platna
    if any(map(lambda t: t[0] < -29 or t[1] < -19 or
                     t[0] > 29 or t[1] > 19, nttačke)):
      showerror('Greška', 'Neuspela transformacija!')
      return
    else:
      # U slucaju da je korektno, iscrtava se transformisan poligon
      # ttačke -> lista tačaka u koordinatnom sistemu sa slike
      # tačke -> lista tačaka u koordinatnom sistemu platna
      print ('Izvršena transformacija: {}!'. format(self.tr))
      self.ttačke = nttačke
      self.tačke = list(map(partial(mul, self.kup), self.ttačke))
      self.nacrtaj_figuru()
      
  # Transformacijski okvir
  def transformacije(self):
    # Mapa za preslikavanje stringa u
    # odgavarajuću matricu transformacije
    self.funkcije = {'translacija': Trans,
                     'skaliranje': Skal, 
                     'smicanje': Smic,
                     'rotacija': Rot,
                     'refleksija': Refl}
    
    # Nepakovana lista argumenata *args je neophodna
    # kako bi se prosledili (i zanemarili) dodatni
    # podaci o promeni odabira, slično kao što npr.
    # kolbek fje u GLUT-u obavezno primaju koordinate
    # događaja, iako one često nisu nužan podatak
    def unos_transformacije(*args):
      # Čitanje vrednosti odabrane transformacije
      self.tr = var.get()
      print('Odabrana transformacija: {}'.format(self.tr))
      
      # Kontrola pristupa poljima za unos parametara 
      # u zavisnosti od odabrane transformacije
      self.kontrola_pristupa()
        
    # Pravljenje okvira za odabir transformacije
    okvir_t = LabelFrame(self, text = 'Izaberite transformaciju', 
                                      padx = 4, pady = 4)
    okvir_t.place(x = 18, y = 337,
                  height = 95, width = 158)

    # U zavisnosti od vrednosti var koju pročitamo iz
    # padajućeg menija, poziva se prava transformacija
    var = StringVar(self)
    var.set('                 ')
    
    # Funkcija za praćenje promenljive
    var.trace('w', unos_transformacije)
    
    # Padajuća lista geometrijskih transformacija
    option = OptionMenu(okvir_t, var, 'translacija', 'skaliranje', 
                        'smicanje', 'rotacija', 'refleksija').pack()
    
    # Postavljanje dugmeta za pokretanje transformacije
    dugme_t = Button(okvir_t, text = 'Transformiši', 
                     command = self.transformiši).pack()
    
    # Naslovi parametara koje korisnik unosi
    x_koord_labela = Label(self, text = 'x:')
    y_koord_labela = Label(self, text = 'y:')
    ugao_labela = Label(self, text = '\u03B8:')
    
    # Promena pozicije elemenata
    x_koord_labela.place(x = 185, y = 348)
    y_koord_labela.place(x = 185, y = 375)
    ugao_labela.place(x = 185, y = 403)
    
    # Polja za unos vrednosti transformacija
    self.x_koord = Entry(self, state = 'disabled')
    self.y_koord = Entry(self, state = 'disabled')
    self.ugao = Entry(self, state = 'disabled')
    
    # Promena pozicije elemenata
    self.x_koord.place(x = 200, y = 348)
    self.y_koord.place(x = 200, y = 375)
    self.ugao.place(x = 200, y = 403)
    
    # Konfiguracija elemenata, postavljanje
    # širine polja za unos parametara
    self.x_koord.config(width = 4)
    self.y_koord.config(width = 4)
    self.ugao.config(width = 4)
    
    # Konfiguracija ostalih parametara
    self.odabir_centra()
    self.inverz()
  
  # Funkcija za praćenje inverza
  def inverz(self):
    def odaberi_inverz(*args):
      self.inv = bool(var.get())
      if self.inv:
        print('Odabrana inverzna transformacija.')
    
    var = IntVar()
    var.trace('w', odaberi_inverz)
    
    self.inverz = Checkbutton(self, text = 'Invertuj promenu',
                              variable = var, command = None)
    self.inverz.place(x = 262, y = 410)
  
  # Kontrola pristupa poljima za unos
  def kontrola_pristupa(self):
    # Zanemarivanje kontrole ako još
    # nije birana transformacija
    if not self.tr:
      return
    
    # Svaka transformacija sem translacije
    # osvežava odabir centra transformacije
    if self.tr != 'translacija':
      self.t1_koord.config(state = 'normal')
      self.t2_koord.config(state = 'normal')
      
      self.radio1.config(state = 'normal')
      self.radio2.config(state = 'normal')
      self.radio3.config(state = 'normal')
    
    # Vektorske transformacije podrazumevaju
    # unos parametara x i y, ali ne i teta
    if self.tr in ('translacija',
                   'skaliranje',
                   'smicanje'):
      self.x_koord.config(state = 'normal')
      self.x_koord.delete(0, 'end')
      
      self.y_koord.config(state = 'normal')
      self.y_koord.delete(0, 'end')
      
      # Podrazumevane su jedinične transformacije
      if self.tr == 'skaliranje':
        self.x_koord.insert(0, '1')
        self.y_koord.insert(0, '1')
      else:
        self.x_koord.insert(0, '0')
        self.y_koord.insert(0, '0')
      
      self.ugao.delete(0, 'end')
      self.ugao.config(state = 'disabled')
      
      # Translacija nije oko tačke
      if self.tr == 'translacija':
        self.t1_koord.delete(0, 'end')
        self.t1_koord.config(state = 'disabled')
        
        self.t2_koord.delete(0, 'end')
        self.t2_koord.config(state = 'disabled')
        
        self.centar_transformacije = ''
        self.radio1.deselect()
        self.radio2.deselect()
        self.radio3.deselect()
        
        self.radio1.config(state = 'disabled')
        self.radio2.config(state = 'disabled')
        self.radio3.config(state = 'disabled')
    # Rotacija i refleksija zahtevaju ugao i tačku
    else:
      self.ugao.config(state = 'normal')
      self.ugao.delete(0, 'end')
      self.ugao.insert(0, '0')
      
      self.x_koord.delete(0, 'end')
      self.x_koord.config(state = 'disabled')
      
      self.y_koord.delete(0, 'end')
      self.y_koord.config(state = 'disabled')
    
    # Eventualno upisivanje nekih
    # vrednosti u slobodna polja
    self.baricentar()
  
  # Eventualno upisivanje nekih
  # vrednosti u slobodna polja
  def baricentar(self):
    # Zanemarivanje kontrole ako još
    # nije birana transformacija
    if not self.tr:
      return
    
    # Popunjavanje centra transformacije
    if self.centar_transformacije in ('oko koordinatnog početka',
                                          'oko centra mase'):
      baricentar = lambda t: (sum(map(ig(0), t))/len(t),
                              sum(map(ig(1), t))/len(t)) \
                                  if t else (0, 0)
      
      t1, t2 = baricentar(self.ttačke) if self.centar_transformacije \
                          == 'oko centra mase' else (0, 0)
      
      self.t1_koord.delete(0, 'end')
      self.t2_koord.delete(0, 'end')
      
      self.t1_koord.insert(0, '%.2f'%t1)
      self.t2_koord.insert(0, '%.2f'%t2)
    
      self.t1_koord.config(state = 'readonly')
      self.t2_koord.config(state = 'readonly')
  
  # Odabir načina rotacije
  def odabir_centra(self):
    def unos_centra(*args):
      self.centar_transformacije = var.get()
    
    # Praćenje stanja rotacije
    var = StringVar()
    self.centar_transformacije = ''
    var.trace('w', unos_centra)
    
    # Oznaka za odabir načina rotacije
    odabir_centra = Label(self,
        text = 'Centar transformacije:',
        justify = 'center',
        padx = 10)
    odabir_centra.place(x = 255, y = 330)
    
    # Dugme za rotaciju oko tačke (0, 0)
    self.radio1 = Radiobutton(self,
              text = 'centar platna',
              padx = 3,
              variable = var,
              value = 'oko koordinatnog početka',
              command = self.kontrola_pristupa)
    self.radio1.place(x = 242, y = 350)
    
    # Dugme za rotaciju oko baricentra
    self.radio2 = Radiobutton(self, 
              text = 'baricentar',
              padx = 3, 
              variable = var, 
              value = 'oko centra mase',
              command = self.kontrola_pristupa)
    self.radio2.place(x = 242, y = 370)
    
    # Dugme za rotaciju oko unete tačke
    self.radio3 = Radiobutton(self, 
              text = 'uneta tačka',
              padx = 3, 
              variable=var, 
              value= 'oko tačke',
              command = self.kontrola_pristupa)
    self.radio3.place(x = 242, y = 390)
    
    # Isprva su dugmad nepristupačna
    self.radio1.config(state = 'disabled')
    self.radio2.config(state = 'disabled')
    self.radio3.config(state = 'disabled')
    
    # Polja za unos centra transformacija
    # Naslovi parametara koje korisnik unosi
    t1_labela = Label(self, text = 't1:')
    t2_labela = Label(self, text = 't2:')
    
    # Promena pozicije elemenata
    t1_labela.place(x = 360, y = 358)
    t2_labela.place(x = 360, y = 385)
    
    # Polja za unos vrednosti transformacija
    self.t1_koord = Entry(self, state = 'disabled')
    self.t2_koord = Entry(self, state = 'disabled')
    
    # Konfiguracija elemenata, postavljanje
    # širine polja za unos parametara
    self.t1_koord.config(width = 4)
    self.t1_koord.place(x = 380, y = 358)
    self.t2_koord.config(width = 4)
    self.t2_koord.place(x = 380, y = 385)
            
  # Okvir za magični svet transformacija
  def init_unos(self):
    # Pravljenje okvira za dugmad
    self.okvir_d = LabelFrame(self, text = 'Unosite tačke klikovima'
                               ' po platnu', padx = 10, pady = 10)
    self.okvir_d.place(x = 10, y = 315,
                       height = 128, width = 430)
    
    # Inicijalizacija polja sa transformacijama
    self.transformacije()
    
  # Dodavanje pritisnute tačke
  def dodaj_tačku(self, dog):
    # Ukoliko je u toku unos tačaka
    if self.unos:
      # Dodavanje pritisnute tačke
      tačka = (dog.x, dog.y)
      self.tačke.append(tačka)
      
      # Čuvanje i u koordinatnom sistemu
      ttačka = self.puk * tačka
      self.ttačke.append(ttačka)
      
      # Log poruka o akciji
      print('Dodata tačka (%.2f, %.2f) na zahtev korisnika!' % ttačka)
      
      # Iscrtavanje figure
      self.nacrtaj_figuru()
      
      # Kontrola pristupa
      self.baricentar()
  
  # Promena teksta u zavisnosti od toga
  # da li je unos tačaka u toku ili ne
  def promena_unosa(self):
    if self.unos:
      # Ne zaključuje se prazan unos
      if not self.tačke:
        showerror('Greška', 'Unesite tačke na platno!')
        return
      
      self.okvir_d.config(text = 'Transformišite figuru pomoću dugmadi')
      self.umeni.entryconfig(1, label = 'Ponovi unos')
      
      # Promena stanja unosa i crtanje formiranog mnogougla
      self.unos = False
      self.nacrtaj_figuru()
      
      # Log poruka o akciji
      print('Zaključen unos tačaka na zahtev korisnika!')
    else:
      self.okvir_d.config(text = 'Unosite tačke klikovima po platnu')
      self.umeni.entryconfig(1, label = 'Zaključi unos')
      
      # Brisanje platna i reinicijalizacija liste tačaka
      self.novo_platno()
      
      # Promena stanja unosa
      self.unos = True
      
      # Log poruka o akciji
      print('Ponovljen unos tačaka na zahtev korisnika!')
  
  # Ispravljanje iscrtane figure
  def ispravi(self):
    # Ne ispravljaju se prazne figure
    if not self.tačke:
      showerror('Greška', 'Unesite tačke na platno!')
      return
    
    # Ne ispravlja se pre kraja unosa
    if self.unos:
      showerror('Greška', 'Prvo zaključite unos tačaka!')
      return
    
    # Zamena liste tačaka konveksnim omotom
    self.tačke = konveksni_omot(self.tačke)
    self.ttačke = list(map(partial(mul, self.puk), self.tačke))
    
    # Crtanje ispravljene figure
    self.nacrtaj_figuru()
    
    # Log poruka o akciji
    print('Ispravljena figura na zahtev korisnika!')
  
  # Reinicijalizacija platna
  def novo_platno(self):
    self.obriši_platno()
    self.tačke = []
    self.ttačke = []
    self.id_tač = []
  
  # Brisanje platna; ne može sa kratkim
  # self.platno.delete('all') jer se njime
  # briše i slika koordinatnog sistema
  def obriši_platno(self):
    # Brisanje prethodno nacrtane figure
    self.platno.delete(self.figura)
    
    # Brisanje prethodno nacrtanih tačaka
    list(map(self.platno.delete, self.id_tač))
  
  # Crtanje potrebne figure
  def nacrtaj_figuru(self):
    # Brisanje platna
    self.obriši_platno()
    
    # Iscrtavanje trenutnih tačaka i
    # čuvanje njihovih identifikatora
    self.id_tač = [self.platno.create_oval
              (t[0]-2, t[1]-2, t[0]+2, t[1]+2,
              outline = 'blue', fill = 'blue')
                    for t in self.tačke]
    
    # Ukoliko je unos u toku, crtanje nove linije
    if self.unos:
      self.figura = self.platno.create_line(self.tačke) \
                     if len(self.tačke) > 1 else None
    else:
      # Inače iscrtavanje mnogougla ukoliko su tačke učitane
      self.figura = self.platno.create_polygon(self.tačke, outline
         = 'black', fill = '') if len(self.tačke) > 1 else None
  
  # Prikazivanje glavnih informacija o aplikaciji
  def info(self, dog = None):
    # Log poruka o akciji
    print('Ispisane informacije o programu na zahtev korisnika!')
    
    # Prikazivanje glavnih informacija
    showinfo('Informacije',
             'GeoDemonstrator, seminarski iz Programskih paradigmi.\n\n'
             'Korisnik zadaje mnogougao u dvodimenzionom okruženju, nad'
             ' kojim zatim vrši proizvoljne afine geometrijske'
             ' transformacije: translaciju, rotaciju, refleksiju,'
             ' skaliranje, smicanje.\n\n'
             'Ideja je omogućiti jednostavno interaktivno prikazivanje i lakše'
             ' razumevanje materije koja se obrađuje na časovima Geometrije'
             ' za I smer, kao i Računarske grafike.\n\n'
             'Autori (tim KriLa):\n'
             'Kristina Pantelić, 91/2016,\n'
             'Lazar Vasović, 99/2016.\n\n'
             'Matematički fakultet, 2019')
  
  # Zatvaranje aplikacije na zahtev korisnika
  def kraj(self, dog = None):
    # Poruka korisniku o kraju programa
    if askyesno('Kraj programa',
       'Da li stvarno želite da napustite program?'):
      
      # Log poruka o zatvaranju aplikacije
      print('GeoDemonstrator zatvoren na zahtev korisnika!')
      
      # Upotreba self.quit() zamrzava prozor na Windows-u,
      # pošto prekida izvršavanje i pokretačkog programa
      self.destroy()

# Obaveštenje o grešci ukoliko je modul
# pokrenut kao samostalan program
if __name__ == '__main__':
  greška('GKI nije samostalan program! Pokrenite main!')
