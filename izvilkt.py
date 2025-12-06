import pandas as pd
import requests

#Mājaslapa
# https://nosketch.korpuss.lv/#wordlist?corpname=LVK2022&tab=basic&find=lemma&wlattr=lemma_lc&itemsPerPage=100&showresults=1&cols=%5B%22frq%22%5D&diaattr=&showtimelineabs=0&timelinesthreshold=5
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
    # '*' : (2, 0),
}

def izvilkt(sākt_ar):
    df = pd.read_csv('wordlist_LVK2022_20251116172705.csv', skiprows=2)
    df.dropna(inplace=True)
    df = df[df['Item'].str.isalpha()]
    df = df['Item']

    #SPODRINĀT ir pēdējais, kurš tika iegūts.
    for num, v in enumerate(df[sākt_ar:], sākt_ar):
        print(num, v)
            # break
        while True:
            try:
                vaicājums = requests.get(f'http://api.tezaurs.lv:8182/inflect/json/{v}', timeout=1000)
            except:
                print('Nesanāk')
            else:
                break
        try:
            vaicājums = vaicājums.json()[0]
            with open('dati', 'a', encoding='utf-8') as f:
                for i in vaicājums:
                    # print(i)

                    v_i = str.upper(i['Vārds'])
                    if not (
                            i['Vārdšķira']=='Saīsinājums' #or \
                            # i['Vārdšķira']=='Reziduālis' or \
                            # ('Lietojums' in i and i['Lietojums']=='Sarunvaloda') or\
                            # ('Lietvārda tips' in i and i['Lietvārda tips']=='Īpašvārds') or
                            # len(v_i )>15
                            ):
                        f.write(v_i+'\n')
        except requests.exceptions.JSONDecodeError:
            with open('atmesti', 'a', encoding='utf-8') as f:
                f.write(v+'\n')
def attīrīt():
    # df = pd.read_csv('dati')
    # df.dropna(inplace=True)
    # print(df)
    # print('Sākotnēji:', len(df))
    # #Vārdi mēdz atkārtoties:
    # df.drop_duplicates(inplace=True)
    # print('Dublikāti:', len(df))
    # #Vārdu garumiem ir ierobežojumi:
    # garumi = df['Items'].str.len()
    # df = df[(2<=garumi)*(garumi<=15)]
    # print('Garums:', len(df))

    # #Burtu skaitam ir ierobežojumi:
    # for b in burti:
    #     df = df[df['Items'].str.count(b) <= burti[b][0]+2]#2 tukšie
    #     print(b, len(df))
    # df.to_csv('vārdi1')



    #Daži simboli nav leksikonā:
    df =  pd.read_csv('vārdi1', index_col=0)
    print(len(df))
    df[['Garums']] = 0
    for b in burti:
        print(b)
        df['Garums'] += df['Items'].str.count(b)

    df = df[df['Items'].str.len()==df['Garums']]
    print(len(df))
    print(df)


    df.to_csv('vārdi')
# print(df)
attīrīt()
#26464 - nespodrs
#26464 - 28368 - 
#25000 - 26773 - jeep
#24000 - 25677
#24500 - 26220
#24700 - 26438
#24750 - 26493
#24720 - 26459
# izvilkt(30289)
# #129802