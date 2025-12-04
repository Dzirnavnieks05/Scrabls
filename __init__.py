import tkinter as tk
import numpy as np
from itertools import permutations
import requests

LĪDZSKAŅI = 'BCČDFGĢHJKĶLĻMNŅPRSŠTVZŽ'
PATSKAŅI = 'AĀEĒIĪOUŪ'

class Spēle:
    def __init__(self):
        '''Sagatavo laukumu un 2 spēlētājus spēlētājus.'''
        self.logs = tk.Tk()
        self.logs.title('Scrabble')
        self.lauciņš_izm = 45
        self.audekls = tk.Canvas(
            self.logs, 
            width=self.lauciņš_izm*15, height=self.lauciņš_izm*15, 
            bg='green'
        )
        #Ar pozitīvām vērtībām apzīmēsim burta reizinātājus, ar negatīvām - vārda.
        self.bonusi = np.zeros((15, 15), dtype=int)
        self.laukums = np.full((15, 15), -1, dtype=int)

        #Trīskārša vārda vērtība:
        for x in (0, 7, 14):
            for y in (0, 7, 14):
                if x==y==7:
                    continue
                self.audekls.create_rectangle(
                    x*self.lauciņš_izm, y*self.lauciņš_izm,
                    (x+1)*self.lauciņš_izm, (y+1)*self.lauciņš_izm,
                    fill='red'
                )
                self.bonusi[x, y] = -3
        #Divkārša vārda vērtība:
        for i in range(1, 5):
            self.audekls.create_rectangle(
                i*self.lauciņš_izm, i*self.lauciņš_izm,
                (i+1)*self.lauciņš_izm, (i+1)*self.lauciņš_izm,
                fill='pink'
            )
            self.bonusi[i, i] = -2

            self.audekls.create_rectangle(
                (14-i)*self.lauciņš_izm, i*self.lauciņš_izm,
                (15-i)*self.lauciņš_izm, (i+1)*self.lauciņš_izm,
                fill='pink'
            )
            self.bonusi[14-i, i] = -2

            self.audekls.create_rectangle(
                (14-i)*self.lauciņš_izm, (14-i)*self.lauciņš_izm,
                (15-i)*self.lauciņš_izm, (15-i)*self.lauciņš_izm,
                fill='pink'
            )
            self.bonusi[14-i, 14-i] = -2

            self.audekls.create_rectangle(
                i*self.lauciņš_izm, (14-i)*self.lauciņš_izm,
                (i+1)*self.lauciņš_izm, (15-i)*self.lauciņš_izm,
                fill='pink'
            )
            self.bonusi[i, 14-i] = -2
        self.audekls.create_rectangle(
            7*self.lauciņš_izm, 7*self.lauciņš_izm,
            8*self.lauciņš_izm, 8*self.lauciņš_izm,
            fill='pink'
        )
        self.bonusi[7, 7] = -2
        #Trīskārša burta vērtība:
        for x in range(1,15, 4):
            for y in range(1,15, 4):
                if not (x==y==1 or x==y==13 or (x==1 and y==13) or (x==13 and y==1)):
                    self.audekls.create_rectangle(
                        x*self.lauciņš_izm, y*self.lauciņš_izm,
                        (x+1)*self.lauciņš_izm, (y+1)*self.lauciņš_izm,
                        fill='blue'
                    )
                    self.bonusi[x, y] = 3
        #Divkārša burta vērtība:
        for x, y in ((3, 0), (11, 0), (6, 2), (8, 2), (7, 3)):
            self.audekls.create_rectangle(
                x*self.lauciņš_izm, y*self.lauciņš_izm,
                (x+1)*self.lauciņš_izm, (y+1)*self.lauciņš_izm,
                fill='lightblue'
            )
            self.bonusi[x, y] = 2

            self.audekls.create_rectangle(
                y*self.lauciņš_izm, x*self.lauciņš_izm,
                (y+1)*self.lauciņš_izm, (x+1)*self.lauciņš_izm,
                fill='lightblue'
            )
            self.bonusi[y, x] = 2

            self.audekls.create_rectangle(
                x*self.lauciņš_izm, (14-y)*self.lauciņš_izm,
                (x+1)*self.lauciņš_izm, (15-y)*self.lauciņš_izm,
                fill='lightblue'
            )
            self.bonusi[x, 14-y] = 2

            self.audekls.create_rectangle(
                (14-y)*self.lauciņš_izm, x*self.lauciņš_izm,
                (15-y)*self.lauciņš_izm, (x+1)*self.lauciņš_izm,
                fill='lightblue'
            )
            self.bonusi[14-y, x] = 2

        self.audekls.create_rectangle(
            6*self.lauciņš_izm, 6*self.lauciņš_izm,
            7*self.lauciņš_izm, 7*self.lauciņš_izm,
            fill='lightblue'
        )
        self.bonusi[6, 6] = 2

        self.audekls.create_rectangle(
            6*self.lauciņš_izm, 8*self.lauciņš_izm,
            7*self.lauciņš_izm, 9*self.lauciņš_izm,
            fill='lightblue'
        )
        self.bonusi[6, 8] = 2
        self.audekls.create_rectangle(
            8*self.lauciņš_izm, 6*self.lauciņš_izm,
            9*self.lauciņš_izm, 7*self.lauciņš_izm,
            fill='lightblue'
        )
        self.bonusi[8, 6] = 2

        self.audekls.create_rectangle(
            8*self.lauciņš_izm, 8*self.lauciņš_izm,
            9*self.lauciņš_izm, 9*self.lauciņš_izm,
            fill='lightblue'
        )
        self.bonusi[8, 8] = 2

        #Līnijas:
        for i in range(16):
            self.audekls.create_line(
                i*self.lauciņš_izm, 0,
                i*self.lauciņš_izm, 15*self.lauciņš_izm,
                fill='beige',
                width=3
            )
            self.audekls.create_line(
                0, i*self.lauciņš_izm,
                15*self.lauciņš_izm, i*self.lauciņš_izm,
                fill='beige',
                width=3
            )
        self.audekls.pack()

        # print(self.bonusi)
        #Vai spēle ir sākusies
        self.vai_sākts = False
    def mainloop(self):
        return self.logs.mainloop()
    def pārbaudīt_vārdu(self, roka, x=None,y=None,virziens='x'):
        '''Pārbauda, kādus vārdus var veidot no pieejamajiem burtiem.'''
        
        roka_burti = ''.join(burti_sim[j] for j in roka)
        if x==None and y==None:
            #Pārbauda, vai šāda roka jau ir bijusi
            with open('dati', 'r') as f:
                for i in f:
                    if i[1:8] == roka_burti and i[9]=='0':
                        iesp_komb = []
                        for i in f:
                            if not '#' in i:
                                iesp_komb.append(i[:-1])
                        return iesp_komb
            with open('dati', 'a', encoding='utf-8') as f:
                f.write(f'#{roka_burti} 0\n')

            #Veic pārlasi un meklē pieejamos vārdus:
            for s in range(2, 7+1):
                m = sorted(tuple(set(permutations(roka, s))))
                if False:#s==7:
                    ind = m.index(tuple(burti_sim.index(i) for  i in 'TRAKRJO'))
                else:
                    ind = 0
                for v in m[ind:]:
                    v = ''.join(burti_sim[i] for i in v)
                    if any(i in v for i in ('JKR', 'JRT')):
                        continue
                    #Pēc "J", "R" vārda sākumā nemēdz sekot līdzskaņi:
                    if v[0] in ('J', 'R'):
                        if not  v[1] in PATSKAŅI:
                            continue
                    #Pēc "T" vārda sākumā parasti seko patskanis vai "JLRSV":
                    if v[0]=='T' and v[1] in 'JLRSV':
                        continue
                    #Pēc "TR" vārda sākumā nemēdz sekot līdzskaņi
                    if v[0:2]=='TR' and v[2] in LĪDZSKAŅI:
                        continue
                    #"J" nemēdz būt starp līdzskaņiem:
                    if 'J' in v:
                        if any(v[i]=='J' and v[i-1] in LĪDZSKAŅI and v[i+1] in LĪDZSKAŅI for i in range(2, len(v)-1)):
                            continue
                    if v[1:3] == 'RR' and v[0] in LĪDZSKAŅI:
                        continue
                    
                    #Nemēdz būt 5 secīgi līdzskaņi:
                    

                    vaicājums = requests.get(f'http://api.tezaurs.lv:8182/analyze/{v}', timeout=1000)
                    vaicājums = vaicājums.json()
                    # print(vaicājums)
                    vai_der = False
                    iesp_komb = [] #Iespējamās kombinācijas, kuras var veidot no vārdiem.
                    # _sar = []
                    for i in vaicājums:
                        if not (
                            i['Vārdšķira']=='Saīsinājums' or \
                            i['Vārdšķira']=='Reziduālis' or \
                            ('Lietojums' in i and i['Lietojums']=='Sarunvaloda') or\
                            ('Lietvārda tips' in i and i['Lietvārda tips']=='Īpašvārds')
                        ):
                            # print(i)
                            # print(i['Vārdšķira'])
                            # _sar.append(i)
                            vai_der = True

                    if vai_der:
                        with open('dati', 'a') as f:
                            f.write(v+'\n')
                        print(v)
                        iesp_komb.append(v)
                        # for i in _sar:
                        #     print(i)
                        #     print(i['Vārdšķira'])
                    else:
                        print('Ne', v)
                for v in iesp_komb:
                    print(v)
        else:
            #Veic pārlasi un meklē pieejamos vārdus:
            for s in range(2, 7+1):
                m = sorted(tuple(set(permutations(roka, s))))
                if False:#s==7:
                    ind = m.index(tuple(burti_sim.index(i) for  i in 'TRAKRJO'))
                else:
                    ind = 0
                for v in m[ind:]:
                    v = ''.join(burti_sim[i] for i in v)
                    if any(i in v for i in ('JKR', 'JRT')):
                        continue
                    #Pēc "J", "R" vārda sākumā nemēdz sekot līdzskaņi:
                    if v[0] in ('J', 'R'):
                        if not  v[1] in PATSKAŅI:
                            continue
                    #Pēc "T" vārda sākumā parasti seko patskanis vai "JLRSV":
                    if v[0]=='T' and v[1] in 'JLRSV':
                        continue
                    #Pēc "TR" vārda sākumā nemēdz sekot līdzskaņi
                    if v[0:2]=='TR' and v[2] in LĪDZSKAŅI:
                        continue
                    #"J" nemēdz būt starp līdzskaņiem:
                    if 'J' in v:
                        if any(v[i]=='J' and v[i-1] in LĪDZSKAŅI and v[i+1] in LĪDZSKAŅI for i in range(2, len(v)-1)):
                            continue
                    if v[1:3] == 'RR' and v[0] in LĪDZSKAŅI:
                        continue
                    
                    #Nemēdz būt 5 secīgi līdzskaņi:
                    

                    vaicājums = requests.get(f'http://api.tezaurs.lv:8182/analyze/{v}', timeout=1000)
                    vaicājums = vaicājums.json()
                    # print(vaicājums)
                    vai_der = False
                    iesp_komb = [] #Iespējamās kombinācijas, kuras var veidot no vārdiem.
                    # _sar = []
                    for i in vaicājums:
                        if not (
                            i['Vārdšķira']=='Saīsinājums' or \
                            i['Vārdšķira']=='Reziduālis' or \
                            ('Lietojums' in i and i['Lietojums']=='Sarunvaloda') or\
                            ('Lietvārda tips' in i and i['Lietvārda tips']=='Īpašvārds')
                        ):
                            # print(i)
                            # print(i['Vārdšķira'])
                            # _sar.append(i)
                            vai_der = True

                    if vai_der:
                        with open('dati', 'a') as f:
                            f.write(v+'\n')
                        print(v)
                        iesp_komb.append(v)
                        # for i in _sar:
                        #     print(i)
                        #     print(i['Vārdšķira'])
                    else:
                        print('Ne', v)
                for v in iesp_komb:
                    print(v)

        
        return iesp_komb
    def pārbaudīt_punktus(self, vārds, x, y, virziens='x'):
        '''Aprēķina punktu skaitu par vārdu. Pašlaik tiek ņemts vērā tikai izspēlētais vārds.'''
        rezultāts = 0
        v_reiz = 1
        bonusi = [] #Izlietotie bonusi.
        if virziens=='x':
            for i in range(len(vārds)):
                if self.bonusi[x+i, y]==0:
                    rezultāts += burti[vārds[i]][1]
                elif self.bonusi[x+i, y]<=0:
                    rezultāts += burti[vārds[i]][1]
                    v_reiz *= abs(self.bonusi[x+i, y])
                else:
                    rezultāts += burti[vārds[i]][1]*self.bonusi[x+i, y]
        elif virziens=='y':
            pass
        else:
            print('Nepareizs virziens')
            raise

        return int(rezultāts*v_reiz)
    def gājiens(self, roka: tuple):
        if not self.vai_sākts:
            self.vai_sākts = True
            izvēles = self.pārbaudīt_vārdu(roka)
            izvēles_p = []
            print(izvēles)
            for v in izvēles:
                #Vienkāršības un simetrijas labat 1. gājiens vienmēr būs horizontāls:
                for x in range(8-len(v), 7+1):
                    izvēles_p.append((v, self.pārbaudīt_punktus(v, x, 7, ), x, 7, 'x'))
        izvēles_p.sort(key=lambda x: x[1], reverse=True)
        for v in izvēles_p:
            print(v)
        
        vārds_izsp = izvēles_p[0]
        if vārds_izsp[-1]=='x':
            for i in range(len(vārds_izsp[0])):
                x_i = vārds_izsp[2]+i
                self.audekls.create_rectangle(
                        x_i*self.lauciņš_izm,     vārds_izsp[3]*self.lauciņš_izm,
                    (x_i+1)*self.lauciņš_izm, (vārds_izsp[3]+1)*self.lauciņš_izm,
                    fill='beige',
                )
                self.audekls.create_text(
                    (x_i+0.5)*self.lauciņš_izm, (vārds_izsp[3]+0.5)*self.lauciņš_izm,
                    text=vārds_izsp[0][i],
                    # fill='beige',
                )

                ind = burti_sim.index(vārds_izsp[0][i])
                roka.pop(roka.index(ind))

                self.bonusi[x_i, vārds_izsp[3]] = 0
        self.logs.update()


np.random.seed(0)
burti = {
    'A' : (11, 1),
    'Ā' : (4, 2), 
    'B' : (1, 5), 
    'C' : (1, 5),
    'Č' : (1, 10), 
    'D' : (3, 3), 
    'E' : (6, 1), 
    'Ē' : (2, 4), 
    'F' : (1, 10),
    'G' : (1, 5), 
    'Ģ' : (1, 10),
    'H' : (1, 10), 
    'I' : (9, 1), 
    'Ī' : (2, 4), 
    'J' : (2, 4), 
    'K' : (4, 2), 
    'Ķ' : (1, 10),
    'L' : (3, 2), 
    'Ļ' : (1, 8),
    'M' : (4, 2), 
    'N' : (4, 2), 
    'Ņ' : (1, 6),
    'O' : (3, 3),
    'P' : (3, 2),
    'R' : (5, 1),
    'S' : (8, 1),
    'Š' : (1, 6),
    'T' : (6, 1),
    'U' : (5, 1),
    'Ū' : (1, 6),
    'V' : (3, 3),
    'Z' : (2, 3),
    'Ž' : (1, 8),
    '*' : (2, 0),
}

burti_sim = list(burti.keys())
burti_maisā_sk = [burti[i][0] for i in burti]
burti_vērtības = [burti[i][1] for i in burti]




# print(burti_maisā_sk)
# print(np.cumsum(burti_maisā_sk))
# burti_maisā_kum = np.cumsum(burti_maisā_sk)

def izvilkt_burtus(N=7):
    '''No maisa izvelk N burtus'''
    izvilkts = []
    for n in range(N):
        ind = np.random.randint(0, np.sum(burti_maisā_sk)-1)
        ind_burts = np.where(ind<np.cumsum(burti_maisā_sk))[-1][0]
        izvilkts.append(int(ind_burts))
        burti_maisā_sk[ind_burts] -= 1 #Izvelkam burtu
        # print(ind, ind_burts, sum(burti_maisā_sk[:ind_burts]))
    return izvilkts
roka1 = izvilkt_burtus()
roka1.sort()
roka2 = izvilkt_burtus()
roka2.sort()
print(roka1)
print(roka2)
# print(burti_sim)
# print(burti_maisā_sk)

spēle = Spēle()

spēle.gājiens(roka1)
print(roka1)
roka1 += izvilkt_burtus(7-len(roka1))
roka1.sort()
print(roka1)

spēle.pārbaudīt_vārdu(roka2)
# print(spēle.bonusi.T)

# vaicājums = requests.get(f'https://tezaurs.lv/art', timeout=1000)
# vaicājums = vaicājums.text
# for i in vaicājums:
#     print(i)
# print(vaicājums.text)

print('Pārbaude strādā')
spēle.mainloop()