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
    
    # Transformacija
    self.tr = ''
    
    # Indikator inverzne transformacije
    self.inv = 0
    
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
    # Postavljanje glavnog menija i vezivanje
    # komandi za odgovarajuće funkcionalnosti
    self.meni = Menu(self)
    self.umeni = Menu(self.meni)
    self.umeni.add_command(label = 'Zaključi unos', command = self.promena_unosa)
    self.umeni.add_command(label = 'Ispravi figuru', command = self.ispravi)
    self.umeni.add_command(label = 'Očisti platno', command = self.novo_platno)
    self.meni.add_cascade(label = 'Opcije', menu = self.umeni)
    self.meni.add_command(label = 'Info (F1)', command = self.info)
    self.meni.add_command(label = 'Kraj (Esc)', command = self.kraj)
    self.config(menu = self.meni)
    
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
  
  # Funkcija za dohvatanje vrednosti promenljive
  def uzmi_prom(self, prom):
    try:
      if prom == 'x':
        return float(eval(self.x_koord.get()))
      elif prom == 'y':
        return float(eval(self.y_koord.get()))
      else:
        return float(eval(self.ugao.get()))
    except:
      showerror('Greška', 'Loši parametri tranformacije!')
      return float('nan')
  
  # Funkcija za transformisanje kreiranog poligona
  def transformisi(self, *args):
      
      print ("Transformišem - {}!". format(self.tr))
      
      if self.ttačke == []:
          showerror('Greška', 'Unesite tačke na platno!')
          return
      
      if self.tr == '':
          showerror('Greška', 'Izaberite transformaciju!')
          return
      
      if (self.tr == 'rotacija' and self.nacin_rotacije == '' and self.ugao.get() == ''):
          showerror('Greška', 'Izaberite ugao i način rotacije!')
          return
      elif (self.tr == 'rotacija' and self.nacin_rotacije == ''):
          showerror('Greška', 'Izaberite način rotacije!')
          return
      
      # Preslikavanje stringa u odgovarajucu matricu transformacije
      # u zavisnosti od unetih parametara
      if (self.tr == 'rotacija' and self.nacin_rotacije == 'oko koordinatnog pocetka') or self.tr == 'refleksija':
        # Greska ako nije unet ugao
        if self.ugao.get() == '':
            showerror('Greška', 'Unesite parametre tranformacije!')
            return
        if self.inv == 0:
            u = self.uzmi_prom('u')
        else:
            u = -self.uzmi_prom('u')
        
        if isnan(u): return
        
        self.odabrana_transformacija = (self.funkcije[self.tr])(u)

      elif self.tr == 'rotacija':
          centar_mase = lambda t: (sum(map(ig(0), t))/len(t),
                                   sum(map(ig(1), t))/len(t))
          
          # Ukoliko je odabrana inverzna transformacija
          if self.inv == 0:
            u = self.uzmi_prom('u')
          else:
            u = -self.uzmi_prom('u')
          
          if isnan(u): return
          
          if self.nacin_rotacije == 'oko centra mase':
            t1, t2 = centar_mase(self.ttačke)
          elif self.nacin_rotacije == 'oko tacke':
            if self.x_koord.get() == '' or self.x_koord.get() == '':
            # Greska ako nisu uneti x i y
                showerror('Greška', 'Unesite parametre tranformacije!')
                return
            # Ukoliko je odabrana inverzna transformacija
            if self.inv == 0:
                t1 = self.uzmi_prom('x')
                if isnan(t1): return
                t2 = self.uzmi_prom('y')
            else:
                t1 = -self.uzmi_prom('x')
                if isnan(t1): return
                t2 = -self.uzmi_prom('y')
          
          if isnan(t2): return
          
          self.odabrana_transformacija = (self.funkcije[self.tr])(u, t1, t2)
    
      else:
        if self.x_koord.get() == '' or self.x_koord.get() == '':
            # Greska ako nisu uneti x i y
            showerror('Greška', 'Unesite parametre tranformacije!')
            return
        # Ukoliko je odabrana inverzna transformacija
        if self.inv == 0:
            t1 = self.uzmi_prom('x')
            if isnan(t1): return
            t2 = self.uzmi_prom('y')
        elif self.tr == 'skaliranje':
            t1 = 1/self.uzmi_prom('x')
            if isnan(t1): return
            t2 = 1/self.uzmi_prom('y')
        else:
            t1 = -self.uzmi_prom('x')
            if isnan(t1): return
            t2 = -self.uzmi_prom('y')
        
        if isnan(t2): return
        
        self.odabrana_transformacija = (self.funkcije[self.tr])(t1,t2)
      
      # Nove transformisane tacke sa vrednostima koordinatnom sistemu sa slike
      nttacke = list(map(partial(mul, self.odabrana_transformacija), self.ttačke))
      
      # Provera da nisu tacke otisle van koordinatnog sistema sa slike tj. platna
      if any(map(lambda t: t[0] < -29 or t[1] < -19 or
                       t[0] > 29 or t[1] > 19, nttacke)):
        showerror('Greška', 'Neuspela transformacija!')
        return
      else:
        # U slucaju da je korektno, iscrtava se transformisan poligon
        # ttacke -> lista tacaka u koordinatnom sistemu sa slike
        # tacke -> lista tacaka u koordinatnom sistemu platna
        self.ttačke = nttacke
        self.tačke = list(map(partial(mul, self.kup), self.ttačke))
        self.nacrtaj_figuru()
      
  # Transformacijski okvir
  def tranformacije(self):
    # Mapa za preslikavanje stringa u odgavarajucu matricu transformacije
    self.funkcije = {'translacija': Trans, 'skaliranje': Skal, 
                     'smicanje': Smic, 'rotacija': Rot,
                     'refleksija': Refl}
      
    def unos_transformacije(*args):
        print("Uneli ste novu transformaciju!")
        # Citanje vrednosti odabrane transformacije iz padajuce liste
        self.tr = var.get()
        print("Odabrali ste: {}".format(str(self.tr)))
        if self.tr != 'rotacija':
            self.nacin_rotacije = ''
            self.radio1.deselect()
            self.radio2.deselect()
            self.radio3.deselect()
            
            self.radio1.configure(state = 'disabled')
            self.radio2.configure(state = 'disabled')
            self.radio3.configure(state = 'disabled')
        else:
            self.radio1.configure(state = 'normal')
            self.radio2.configure(state = 'normal')
            self.radio3.configure(state = 'normal')
            
        
        # Dozvola i zabrana pristupa poljima za unos parametara 
        # u zavisnosti od odabrane transformacije
        if self.tr == 'translacija' or self.tr == 'smicanje' or self.tr == 'skaliranje':
            self.x_koord.configure(state = 'normal')
            self.y_koord.configure(state = 'normal')
            # Brisanje unete vrednosti parametra
            self.ugao.delete(0, 'end')
            self.ugao.configure(state = 'disabled')
        else:
            self.zabrana_pristupa()
        
    # Pravljenje okvira za odabir transformacije
    self.okvir_t = LabelFrame(self, text = 'Izaberite transformaciju', 
                              padx = 5, pady = 5)
    self.okvir_t.place(x = 20, y = 337,
                       height = 95, width = 170)

    # U zavisnosti od vrednosti var koje procitamo iz padajuceg menija,
    # pozivamo odgovarajucu funkciju transformacije
    var = StringVar(self)
    var.set('                 ')
    # Funkcija za pracenje promenljive
    var.trace('w', unos_transformacije)
    
    # Padajuca lista geometrijskih transformacija
    self.option = OptionMenu(self.okvir_t, var, 
                             'translacija', 
                             'skaliranje', 
                             'smicanje', 
                             'rotacija', 
                             'refleksija').pack()
    
    # Postavljanje dugmeta za pokretanje transformacije
    dugme_t = Button(self.okvir_t, text = 'Transformiši', 
                     command = self.transformisi).pack()
    
    # Naslovi parametara koje korisnik unosi
    x_koord_labela = Label(self, text = 'x:') 
    y_koord_labela = Label(self, text = 'y:') 
    ugao_labela = Label(self, text = '\u03B8:') 
    
    # Promena pozicije elemenata
    x_koord_labela.place(x = 200, y = 348)
    y_koord_labela.place(x = 200, y = 375)
    ugao_labela.place(x = 200, y = 403)
    
    # Polja za unos vrednosti transformacija
    self.x_koord = Entry(self, state = 'disabled')
    self.y_koord = Entry(self, state = 'disabled')
    self.ugao = Entry(self, state = 'disabled')
    
    # Promena pozicije elemenata
    self.x_koord.place(x = 215, y = 348)
    self.y_koord.place(x = 215, y = 375)
    self.ugao.place(x = 215, y = 403)
    
    # Konfiguracija elemenata, postavljanje sirine polja za unos parametara
    self.x_koord.config(width = 5)
    self.y_koord.config(width = 5)
    self.ugao.config(width = 5)
       
    self.odabir_rotacije()
    self.inverz()
    
  def inverz(self):
      
    def odaberi_inverz(*args):
        self.inv = int(var.get())
        if self.inv == 1:
            print('Odabrali ste inverznu transformaciju.')
        
    var = IntVar()
    var.trace('w', odaberi_inverz)
    
    self.inverz = Checkbutton(self, text = 'Inverz',
                              variable = var, command = None)
    self.inverz.place(x = 300, y = 410)    
        
  def zabrana_pristupa(self):
        self.x_koord.delete(0, 'end')
        self.x_koord.configure(state = 'disabled')
        self.y_koord.delete(0, 'end')
        self.y_koord.configure(state = 'disabled')
        self.ugao.configure(state = 'normal')
        
  # Odabir nacina rotacije
  def odabir_rotacije(self):
        
    def unos_rotacije(*args):
        self.nacin_rotacije = var.get()
        
    def rot_promena(*args):
        if self.nacin_rotacije != 'oko tacke':
            self.zabrana_pristupa()
        else:
            self.x_koord.configure(state = 'normal')
            self.y_koord.configure(state = 'normal')
            self.ugao.configure(state = 'normal')
        
    var = StringVar()
    self.nacin_rotacije = ''
    var.trace('w', unos_rotacije)
    
    odabir_rotacije = Label(self, 
        text = '''Način rotacije''',
        justify = 'center',
        padx = 10)
    odabir_rotacije.place(x = 290, y = 326)
    self.radio1 = Radiobutton(self, 
              text="oko koord. početka",
              padx = 3, 
              variable=var, 
              value= 'oko koordinatnog pocetka',
              command = rot_promena)
    self.radio1.grid(row=0, column = 0)
    self.radio1.place(x = 270, y = 345)
    
    self.radio2 = Radiobutton(self, 
              text="oko centra mase",
              padx = 3, 
              variable=var, 
              value= 'oko centra mase',
              command = rot_promena)
    self.radio2.grid(row=1, column = 0)
    self.radio2.place(x = 270, y = 365)
    
    self.radio3 = Radiobutton(self, 
              text="oko tačke",
              padx = 3, 
              variable=var, 
              value= 'oko tacke',
              command = rot_promena)
    self.radio3.grid(row=1, column = 0)
    self.radio3.place(x = 270, y = 385)
    
    self.radio1.configure(state = 'disabled')
    self.radio2.configure(state = 'disabled')
    self.radio3.configure(state = 'disabled')
            
  # Okvir za magični svet transformacija
  def init_unos(self):
    # Pravljenje okvira za dugmad
    self.okvir_d = LabelFrame(self, text = 'Unosite tačke klikovima'
                               ' po platnu', padx = 10, pady = 10)
    self.okvir_d.place(x = 10, y = 315,
                       height = 128, width = 430)
    
    self.tranformacije()
    
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
  
  # Promena teksta u zavisnosti od toga
  # da li je unos tačaka u toku ili ne
  def promena_unosa(self):
    if self.unos:
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
  
  # Zamena liste tačaka konveksnim omotom
  def ispravi(self):
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
             ' tranformacije: translaciju, rotaciju, refleksiju,'
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
