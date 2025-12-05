from itertools import permutations, combinations
import tkinter as tk

import numpy as np
import pandas as pd
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
        self.df =  pd.read_csv('vārdi', index_col=0)
        self.df.dropna(inplace=True)
        #Ar pozitīvām vērtībām apzīmēsim burta reizinātājus, ar negatīvām - vārda.
        self.bonusi = np.zeros((15, 15), dtype=int)
        #Izspēlēto lauciņu indeksi
        self.laukums = np.full((15, 15), -1, dtype=int)
        #Sākuma lauciņi (kurus ir vērts apskatīt, izspēlējot).
        # -1 - lauciņš nav piemērots izspēlēšanai;
        # 0 - lauciņu aizņem burts;
        # 1 - lauciņš atrodas blakus burtam
        self.pieejami = np.full((15, 15), -1, dtype=int)

        self.vārdi_izspēlēti = []

        self.num_gājiena = 0

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

        #Vai spēle ir sākusies
        self.vai_sākts = False
    def mainloop(self):
        return self.logs.mainloop()
    def pārbaudīt_vārdu(self, roka, x=None,y=None,virziens='x'):
        '''Pārbauda, kādus vārdus var veidot no pieejamajiem burtiem.'''
        
        df = self.df
        ##Pirmais vārds
        if not self.vai_sākts:
            df_i = df[df['Items'].str.len()<=7] #Vārds sastāvēs no 2-7 burtiem;
            v = ''.join(burti_sim[i] for i in roka)
            burti_der = 0 #Burtu skaits, kas ietilpst
            for i in set(v):
                #1) Pārbauda, vai pietiek burtu;
                #2) Pasaka, ka tiek izmantots burtu skaits no vārda.
                burti_der += (df_i['Items'].str.count(i) <= v.count(i)) * df_i['Items'].str.count(i)
            df_i = df_i[burti_der>=df_i['Items'].str.len()]

            return df_i['Items']
        else:
            pot_v = []
            if virziens=='x':                
                ##Vai ievietojot burtu izvēlētajā vietā var veidoties derīgi vārdi vertikālā virzienā:
                for b in roka:
                    v = [int(self.laukums[x,i]) if i!=y else b for i in range(15)]
                    for sāk in range(y-1, -1, -1):
                        if v[sāk]==-1:
                            sāk += 1
                            break
                    else:
                        sāk = 0 #Vārds sākas pie malas
                    for bei in range(y+1, 15, 1):
                        if v[bei]==-1:
                            break
                    else:
                        bei = 15 #Vārds beidzas pie malas
                    v = ''.join(burti_sim[i] for i in v[sāk+1:bei])
                    if v in df:
                        print('Der X?', sāk, bei, v)
                        ...

                ##Vai vārdu var turpināt?
                for sāk in range(x-1, -1, -1):
                    if self.laukums[sāk,y]==-1:
                        sāk += 1
                        break
                else:
                    sāk = 0 #Vārds sākas pie malas
                for bei in range(x+1, 15, 1):
                    if self.laukums[bei,y]==-1:
                        break
                else:
                    bei = 15 #Vārds beidzas pie malas
                sāk0 = None
                v = ''
                for ind, i in enumerate(self.laukums[sāk+1:bei, y], sāk+1):
                    if i!=-1:
                        v += burti_sim[i]
                        if sāk0==None:
                            sāk0=ind

                if len(v)>0:#Ja ==1, tiek apskatīts iepriekšējā punktā.
                    df_i = df[df['Items'].str.contains(v)]#Vārdi, kuri var veidoties no pieejamajiem:
                    

                    df_i.loc[:, 'Items']=df_i['Items'].str.replace(
                        v, '_', 1
                    )
                    df_i = df_i[(2<=df_i['Items'].str.len())*(df_i['Items'].str.len()<=8)]#Viens simbols aiziet "_", lai zinām, kuru daļu aizstāt.

                    burti_der = 0 #Burtu skaits, kas ietilpst
                    v_roka = [burti_sim[i] for i in roka]
                    for i in set(v_roka):
                        #1) Pārbauda, vai pietiek burtu;
                        #2) Pasaka, ka tiek izmantots burtu skaits no vārda.
                        if i!='_':
                            burti_der += (df_i['Items'].str.count(i) <= v_roka.count(i)) * df_i['Items'].str.count(i)
                    df_i = df_i[burti_der>=df_i['Items'].str.len()-1]
                    

                    #Atrodam perpendikulāros vārdus:
                    vārdi_perp = []
                    for v_i in df_i['Items']:
                        #Vārda sākuma koordinātas: (x_i, y)                        
                        x_i = sāk0-v_i.index('_') 
                        v_i = v_i.replace('_', v)

                        #Ja iziet no laukuma robežām, izlaižam:
                        if x_i+len(v_i)>=15:
                            continue

                        for b_i in range(len(v_i)):
                            if self.laukums[x_i+b_i, y] !=-1:#Ja burts jau ir aizņemts, jauns vārds netiek veidots:
                                continue

                            v_p = v_i[b_i]
                            for j in range(y-1, -1, -1):#Pievieno izspēlētos burtus no sākuma:
                                if self.laukums[x_i+b_i,j]==-1:
                                    break
                                v_p = burti_sim[self.laukums[x_i+b_i, j]] + v_p
                            for j in range(y+1, 15, 1):#Pievieno izspēlētos burtus no sākuma:
                                if self.laukums[x_i+b_i, j]==-1:
                                    break
                                v_p += burti_sim[self.laukums[x_i+b_i, j]]
                            if len(v_p)>1:
                                vārdi_perp.append((v_p, (x_i+b_i, y)))

                        pot_v.append((v_i, (x_i, y), 'x', vārdi_perp))

            if virziens=='y':                
                ##Vai ievietojot burtu izvēlētajā vietā var veidoties derīgi vārdi horizontālā virzienā:
                for b in roka:
                    v = [int(self.laukums[i,y]) if i!=x else b for i in range(15)]
                    for sāk in range(x-1, -1, -1):
                        if v[sāk]==-1:
                            sāk += 1
                            break
                    else:
                        sāk = 0 #Vārds sākas pie malas
                    for bei in range(x+1, 15, 1):
                        if v[bei]==-1:
                            break
                    else:
                        bei = 15 #Vārds beidzas pie malas

                    v = ''.join(burti_sim[i] for i in v[sāk+1:bei])
                    if v in df:
                        print('Der Y?', sāk, bei, v)
                        ...

                ##Vai vārdu var turpināt?
                for sāk in range(y-1, -1, -1):
                    if self.laukums[x,sāk]==-1:
                        sāk += 1
                        break
                else:
                    sāk = 0 #Vārds sākas pie malas
                for bei in range(y+1, 15, 1):
                    if self.laukums[x,bei]==-1:
                        break
                else:
                    bei = 15 #Vārds beidzas pie malas
                sāk0 = None
                v = ''
                for ind, i in enumerate(self.laukums[x, sāk+1:bei], sāk+1):
                    if i!=-1:
                        v += burti_sim[i]
                        if sāk0==None:
                            sāk0=ind
                
                if len(v)>0:#Ja ==1, tiek apskatīts iepriekšējā punktā.
                    df_i = df[df['Items'].str.contains(v)]#Vārdi, kuri var veidoties no pieejamajiem:
                    
                    df_i.loc[:, 'Items']=df_i['Items'].str.replace(
                        v, '_', 1
                    )
                    df_i = df_i[(2<=df_i['Items'].str.len())*(df_i['Items'].str.len()<=8)]#Viens simbols aiziet "_", lai zinām, kuru daļu aizstāt.

                    burti_der = 0 #Burtu skaits, kas ietilpst
                    v_roka = [burti_sim[i] for i in roka]
                    for i in set(v_roka):
                        #1) Pārbauda, vai pietiek burtu;
                        #2) Pasaka, ka tiek izmantots burtu skaits no vārda.
                        if i!='_':
                            burti_der += (df_i['Items'].str.count(i) <= v_roka.count(i)) * df_i['Items'].str.count(i)
                    df_i = df_i[burti_der>=df_i['Items'].str.len()-1]

                    #Atrodam perpendikulāros vārdus:
                    vārdi_perp = []
                    for v_i in df_i['Items']:
                        #Vārda sākuma koordinātas: (x, y_i)
                        y_i = sāk0-v_i.index('_') 
                        v_i = v_i.replace('_', v)

                        #Ja iziet no laukuma robežām, izlaižam:
                        if y_i+len(v_i)>=15:
                            continue

                        for b_i in range(len(v_i)):
                            if self.laukums[x,y_i+b_i] !=-1:#Ja burts jau ir aizņemts, jauns vārds netiek veidots:
                                continue

                            v_p = v_i[b_i]
                            for j in range(x-1, -1, -1):#Pievieno izspēlētos burtus no sākuma:
                                if self.laukums[j,y_i+b_i]==-1:
                                    break
                                v_p = burti_sim[self.laukums[j,y_i+b_i]] + v_p
                            for j in range(x+1, 15, 1):#Pievieno izspēlētos burtus no sākuma:
                                if self.laukums[j,y_i+b_i]==-1:
                                    break
                                v_p += burti_sim[self.laukums[j,y_i+b_i]]
                            if len(v_p)>1:
                                vārdi_perp.append((v_p, (x, y_i+b_i)))

                        pot_v.append((v_i, (x, y_i), 'y', vārdi_perp))
            return pot_v

    def pārbaudīt_punktus(self, vārds, x, y, virziens='x'):
        '''Aprēķina punktu skaitu par vārdu. Pašlaik tiek ņemts vērā tikai izspēlētais vārds.'''
        rezultāts = 0
        v_reiz = 1
        bonusi = [] #Izlietotie bonusi.
        burti_izsp = 0
        if virziens=='x':
            for i in range(len(vārds)):
                #Burti nesakrīt
                #Ja lauciņš ir -1: automātiski brīvs
                #Citādi: ja nesakrīt
                if (self.laukums[x+i, y]!=-1) and (burti_sim[self.laukums[x+i, y]]!=vārds[i]):
                    rezultāts = 0
                    break
                #Pārbaudām, vai vertikāli veidojas vārds:
                v = vārds[i]
                for j in range(y-1, -1, -1):#Pievieno izspēlētos burtus no sākuma:
                    if self.laukums[x+i,j]==-1:
                        break
                    v = burti_sim[self.laukums[x+i,j]] + v
                for j in range(y+1, 15, 1):#Pievieno izspēlētos burtus no sākuma:
                    if self.laukums[x+i,j]==-1:
                        break
                    v += burti_sim[self.laukums[x+i,j]]
                if len(v)>1:
                    if not v in self.df.values:
                        rezultāts = 0
                        break

                #Atrodam bonusu
                if self.bonusi[x+i, y]==0:
                    rezultāts += burti[vārds[i]][1]
                elif self.bonusi[x+i, y]<=0:
                    rezultāts += burti[vārds[i]][1]
                    v_reiz *= abs(self.bonusi[x+i, y])
                else:
                    rezultāts += burti[vārds[i]][1]*self.bonusi[x+i, y]

                #Vai burts nāk no rokas:
                if self.laukums[x+i, y] == -1:
                    burti_izsp += 1

                if burti_izsp==0:#Nekas netiek izspēlēts
                    rezultāts = 0
                elif burti_izsp==7:#Bingo
                    rezultāts += 50
        elif virziens=='y':
            for i in range(len(vārds)):
                #Burti nesakrīt
                if (self.laukums[x, y+i]!=-1) and (burti_sim[self.laukums[x, y+i]]!=vārds[i]):
                    rezultāts = 0
                    break
                #Pārbaudām, vai horizontāli veidojas vārds:
                v = vārds[i]
                for j in range(x-1, -1, -1):#Pievieno izspēlētos burtus no sākuma:
                    if self.laukums[j, y+i]==-1:
                        break
                    v = burti_sim[self.laukums[j, y+i]] + v
                for j in range(x+1, 15, 1):#Pievieno izspēlētos burtus no sākuma:
                    if self.laukums[j, y+i]==-1:
                        break
                    v += burti_sim[self.laukums[j, y+i]]
                if len(v)>1:
                    if not v in self.df.values:
                        rezultāts = 0
                        break

                #Atrodam bonusu
                if self.bonusi[x, y+i]==0:
                    rezultāts += burti[vārds[i]][1]
                elif self.bonusi[x, y+i]<=0:
                    rezultāts += burti[vārds[i]][1]
                    v_reiz *= abs(self.bonusi[x, y+i])
                else:
                    rezultāts += burti[vārds[i]][1]*self.bonusi[x, y+1]

                #Vai burts nāk no rokas:
                if self.laukums[x, y+i] == -1:
                    burti_izsp += 1

                if burti_izsp==0:#Nekas netiek izspēlēts
                    rezultāts = 0
                elif burti_izsp==7:#Bingo
                    rezultāts += 50
        else:
            print('Nepareizs virziens')
            raise

        return int(rezultāts*v_reiz)
    def sar_vārds(self, saraksts):
        # print(saraksts)
        return ''.join(burti_sim[i] for i in saraksts)
    def gājiens(self, roka: tuple):
        gājieni = [
            # ('TRAKO', 22, 7, 7, 'x'),
            # ('IZVĀKS', 24, (10), 3, 'y'),
            # ('LĪVJOS', 34, (11), 3, 'y'),
            # ('AIZVĀKSIET', 32, (10), 2, 'y'),
            # ('NEAIZVĀKSIET', 19, (10), 0, 'y'),
            # ('IZTEČU', 17, np.int64(7), 5, 'y'),
            # ('ŠONAKT', 23, np.int64(9), 4, 'y'),
            # ('VĒRTĀK', 18, np.int64(8), 5, 'y'),
            # ('SVĒRTĀKĀ', 16, np.int64(8), 4, 'y'),
            # ('NEATSVĒRTĀKĀ', 20, np.int64(8), 0, 'y'),

        ]
        if self.num_gājiena>=len(gājieni):
            if not self.vai_sākts:
                
                izvēles = self.pārbaudīt_vārdu(roka)
                
                vārdi_neder = []
                # for v in izvēles:
                #     #Pārbaudām, vai vārds ir derīgs:
                #     if not self.vai_legāls(v):
                #         vārdi_neder.append(v)
                    


                izvēles_p = []    
                if vārdi_neder:
                    df = pd.read_csv('vārdi', index_col=0)
                    for v in izvēles:
                        if v in vārdi_neder:
                            df = df[df['Items']!=v]
                        else:
                            for x in range(8-len(v), 7+1):
                                izvēles_p.append((v, self.pārbaudīt_punktus(v, x, 7, ), x, 7, 'x', []))
                    df.to_csv('vārdi')
                else:
                    for v in izvēles:
                        for x in range(8-len(v), 7+1):
                            izvēles_p.append((v, self.pārbaudīt_punktus(v, x, 7, ), x, 7, 'x', []))
                self.vai_sākts = True
            
            else:
                izvēles = []
                print('Atrod iespējamos vārdus')
                for x, y in zip(*np.where(self.pieejami==1)):
                    izvēles += self.pārbaudīt_vārdu(roka, x, y, 'x')
                    izvēles += self.pārbaudīt_vārdu(roka, x, y, 'y')
                vārdi_neder = []
                # for v_pilns in izvēles:
                #     if not self.vai_legāls(v_pilns[0]):
                #         vārdi_neder.append(v_pilns[0])

                #     # print(v_pilns[-1])
                #     for v in v_pilns[-1]:
                #         if not self.vai_legāls(v[0]):
                #             vārdi_neder.append(v[0])



                # print('Atjauno datubāzi')
                izvēles_p = []    
                if vārdi_neder:
                    df = pd.read_csv('vārdi', index_col=0)
                    df = df[~ df.isin(vārdi_neder)]
                    df.dropna(inplace=True)
                    df.to_csv('vārdi')
                    print('Datubāze atjaunota')
                    df_i = pd.DataFrame(izvēles)
                    # print(df_i)


                    izvēles
                    for v in izvēles:
                        izvēles_p.append((v[0], self.pārbaudīt_punktus(v[0], *v[1], v[2]), *v[1], v[2], v[3]))
                else:
                    for v in izvēles:
                        izvēles_p.append((v[0], self.pārbaudīt_punktus(v[0], *v[1], v[2]), *v[1], v[2], v[3]))
                    

                # # print(izvēles)
                # izvēles_p = []
                # print(izvēles)
                # for v in izvēles:
                #     #Vienkāršības un simetrijas labat 1. gājiens vienmēr būs horizontāls:
                #     for x in range(8-len(v), 7+1):
                #         izvēles_p.append((v, self.pārbaudīt_punktus(v, x, 7, ), x, 7, 'x'))
            # return
        else:
            self.vai_sākts = True
            izvēles_p = [gājieni[self.num_gājiena]]
        

        
        izvēles_p.sort(key=lambda x: x[1], reverse=True)

        # vārds_izsp = izvēles_p[0]
        for v_i in izvēles_p:
            #Vārds nevar dod 0 punktu:
            if v_i[1]==0:
                continue
            #Pārbauda, vai var spēlēt vārdu
            if self.vai_legāls(v_i[0]):
                #Pārbaudam, vai perpendikulāri vārdi ir derīgi:
                # print('Varbūt legāls:', v_i[0])
                for v in v_i[-1]:
                    if not self.vai_legāls(v[0]):
                        # print('Nav legāls, jo:', v[0])
                        break
                else:
                    vārds_izsp = v_i
                    break
        else:
            print('Izlaists gājiens')
            return
        print('Labākais vārds:', vārds_izsp)
        #Aprēķinām punktus un uzzīmējam vārdu:
        if vārds_izsp[-2]=='x':
            self.vārdi_izspēlēti.append(vārds_izsp[0])
            for i in range(len(vārds_izsp[0])):
                x_i = vārds_izsp[2]+i
                if burti_sim.index(vārds_izsp[0][i]) == self.laukums[x_i, vārds_izsp[3]]:
                    continue

                #Uzzīmē lauciņu:
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

                #No rokas izņemam izspēlētos kauliņus:
                ind = burti_sim.index(vārds_izsp[0][i])
                roka.pop(roka.index(ind))

                #Dzēšam izspēlētos bonusus:
                self.bonusi[x_i, vārds_izsp[3]] = 0

                #Pievienojam izspēlēto laukumu:
                self.laukums[x_i, vārds_izsp[3]] = ind

                #Pievienojam izspēlēto laukumu:
                self.pieejami[x_i, vārds_izsp[3]] = 0
                if x_i-1>=0:
                    self.pieejami[x_i-1, vārds_izsp[3]] = abs(self.pieejami[x_i-1, vārds_izsp[3]])
                if x_i+1<15:
                    self.pieejami[x_i+1, vārds_izsp[3]] = abs(self.pieejami[x_i+1, vārds_izsp[3]])
                if vārds_izsp[3]-1>0:
                    self.pieejami[x_i, vārds_izsp[3]-1] = abs(self.pieejami[x_i, vārds_izsp[3]-1])
                if vārds_izsp[3]+1<15:
                    self.pieejami[x_i, vārds_izsp[3]+1] = abs(self.pieejami[x_i, vārds_izsp[3]+1])
        if vārds_izsp[-2]=='y':
            self.vārdi_izspēlēti.append(vārds_izsp[0])
            for i in range(len(vārds_izsp[0])):
                y_i = vārds_izsp[3]+i
                if burti_sim.index(vārds_izsp[0][i]) == self.laukums[vārds_izsp[2], y_i]:
                    continue
                
                #Uzzīmē lauciņu:
                self.audekls.create_rectangle(
                        vārds_izsp[2]*self.lauciņš_izm,     y_i*self.lauciņš_izm,
                        (vārds_izsp[2]+1)*self.lauciņš_izm, (y_i+1)*self.lauciņš_izm,
                    fill='beige',
                )
                self.audekls.create_text(
                    (vārds_izsp[2]+0.5)*self.lauciņš_izm, (y_i+0.5)*self.lauciņš_izm,
                    text=vārds_izsp[0][i],
                    # fill='beige',
                )

                #No rokas izņemam izspēlētos kauliņus:
                ind = burti_sim.index(vārds_izsp[0][i])
                roka.pop(roka.index(ind))

                #Dzēšam izspēlētos bonusus:
                self.bonusi[vārds_izsp[2], y_i] = 0

                #Pievienojam izspēlēto laukumu:
                self.laukums[vārds_izsp[2], y_i] = ind

                #Pievienojam izspēlēto laukumu:
                self.pieejami[vārds_izsp[2], y_i] = 0
                if y_i-1>=0:
                    self.pieejami[vārds_izsp[2], y_i-1] = abs(self.pieejami[vārds_izsp[2], y_i-1])
                if y_i+1<15:
                    self.pieejami[vārds_izsp[2], y_i+1] = abs(self.pieejami[vārds_izsp[2], y_i+1])
                if vārds_izsp[2]-1>0:
                    self.pieejami[vārds_izsp[2]-1, y_i] = abs(self.pieejami[vārds_izsp[2]-1, y_i])
                if vārds_izsp[2]+1<15:
                    self.pieejami[vārds_izsp[2]+1, y_i] = abs(self.pieejami[vārds_izsp[2]+1, y_i])

        self.num_gājiena += 1    
        self.logs.update()
        return vārds_izsp[1]
    def vai_legāls(self, vārds):
        '''Pārbauda, vai vārdu var izspēlēt.'''
        vaicājums = requests.get(f'http://api.tezaurs.lv:8182/analyze/{vārds}', timeout=1000)
        vaicājums = vaicājums.json()
        for i in vaicājums:
            #Ja vārds ir derīgs, nav nepieciešams pārbaudīt tā nozīmes:
            if not (
                i['Vārdšķira']=='Saīsinājums' or \
                i['Vārdšķira']=='Reziduālis' or \
                ('Lietojums' in i and i['Lietojums']=='Sarunvaloda') or\
                ('Lietvārda tips' in i and i['Lietvārda tips']=='Īpašvārds')
            ):
                return True
        return False


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





def izvilkt_burtus(N=7):
    '''No maisa izvelk N burtus'''
    izvilkts = []
    for n in range(N):
        ind = np.random.randint(0, np.sum(burti_maisā_sk)-1)
        ind_burts = np.where(ind<np.cumsum(burti_maisā_sk))[-1][0]
        izvilkts.append(int(ind_burts))
        burti_maisā_sk[ind_burts] -= 1 #Izvelkam burtu
    return izvilkts
roka1 = izvilkt_burtus()
roka1.sort()
roka2 = izvilkt_burtus()
roka2.sort()

spēle = Spēle()

# spēle.pārbaudīt_vārdu(roka1)
punkti1 = 0
punkti2 = 0
izlaisti_pēc_kārtas = 0
while True:
    print('Roka1:', roka1, punkti1)

    p_i = spēle.gājiens(roka1)
    if p_i==None:
        izlaisti_pēc_kārtas += 1
    else:
        punkti1 += p_i
        izlaisti_pēc_kārtas = 0
    roka1 += izvilkt_burtus(7-len(roka1))
    roka1.sort()
    #1. spēlētājam beigušies kauliņi
    if not roka1:
        break

    print('Roka2:', roka2, punkti2)
    p_i = spēle.gājiens(roka2)
    if p_i==None:
        izlaisti_pēc_kārtas += 1
    else:
        punkti2 += p_i
        izlaisti_pēc_kārtas = 0
    roka2 += izvilkt_burtus(7-len(roka2))
    roka2.sort()
    #2. spēlētājam beigušies kauliņi
    if not roka2:
        break

    #Pēc turnīra noteikumiem, ja spēlētāji secīgi izlaiž 6 gājienus,
    #no punktiem tiek atņemta divkāršs punktu skaits, kas ir savā rokā.
    if izlaisti_pēc_kārtas==6:
        for i in roka1:
            punkti1 -= 2*burti[i][1]
        for i in roka2:
            punkti2 -= 2*burti[i][1]

#Ja spēlētājam beidzas kauliņi, tad spēle beidzas. Uzvarētājs
#savāc kauliņus no pretiniekiem un gūst punktus divkāršā vērtībā.
if roka1:
    for i in roka1:
        punkti2 += 2*burti[i][1]
else:
    for i in roka2:
        punkti1 += 2*burti[i][1]
print(punkti1, 'pret', punkti2)

# spēle.pārbaudīt_vārdu(roka2)
print(spēle.laukums.T)
print(spēle.pieejami.T)


print('Pārbaude strādā')
spēle.mainloop()