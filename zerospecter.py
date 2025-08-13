print("""
       █████████████████
     ██▒▒             ██▒▒
    ██▒▒    ██████     ██▒▒
   ██▒▒   ██   █  ██    ██▒▒
   ██▒▒   ██  █   ██    ██▒▒
    ██▒▒    ██████     ██▒▒
     ██▒▒             ██▒▒
       █████████████████
+=======================================+
|            ZER0SPECTER                |
|      Penetration & Exploit            |
+=======================================+

""")

import random
import string
import pyzipper
from itertools import product
from multiprocessing import Pool, cpu_count

def zipcrack():
    esc1 = str((input('include letters?[y][n] ')))
    esc2 = str(input('include numbers? [y][n] '))
    esc3 = str(input('include special characters?[y][n] '))
    cs = int(input('estimated password length?: '))
    arq = str(input('zip path: '))

    senha = ''
    if esc1 == 'y':
        senha += string.ascii_letters
    if esc2 == 'y':
        senha += string.digits
    if esc3 == 'y':
        senha += string.punctuation
    if not senha:
        print('nothing selected, ending...')
        exit()

    def ext(sen):
        try:
            with pyzipper.AESZipFile(arq, 'r') as zp:
                zp.extractall(pwd=sen.encode())
            return (sen, True)
        except:
            return (sen, False)

    def res():
        for sla in product(senha, repeat=cs):
            yield ''.join(sla)

    if __name__ == "__main__":
        with Pool(cpu_count()) as pool:
            for comb, sus in pool.imap_unordered(ext, res(), chunksize=500):
                print(f'Testing: {comb}')
                if sus:
                    print(f'broken with: {comb}')
                    pool.terminate()
                    break
def pass_gen():
    cs = int(input('add the number of character for the password: '))
    q1 = str(input('include special character? [y][n]'))
    q2 = str(input('include numbers?[y][n]'))

    senhap = []
    cha1 = string.ascii_lowercase + string.ascii_uppercase + string.punctuation
    cha2 = string.ascii_lowercase + string.ascii_uppercase

    if q1 and q2 == 'y':
        for _ in range(cs):
            ran = random.randint(1,2)
            if ran == 1:
                senha = random.choice(cha1)
            else:
                senha = str(random.randint(0,9))
            senhap.append(senha)

    if q1 == 'n' and q2 == 'y':
        for _ in range(cs):
            ran = random.randint(1,2)
            if ran == 1:
                senha = random.choice(cha2)
            else:
                senha = str(random.randint(0,9))
            senhap.append(senha)

    if q1 =='y' and q2 == 'n':
        for _ in range(cs):
            ran = random.randint(1,2)
            senha = random.choice(cha1)
            senhap.append(senha)

    if q1 and q2 == 'n':
        for _ in range(cs):
            ran = random.randint(1,2)
            if ran == 1:
                senha = random.choice(cha2)
            else:
                senha = str(random.randint(0,9))
            senhap.append(senha)

    print(''.join(senhap))

def win():
    val = 0
    rec = input("insert your needed: ")
    if rec == "zipbreaker":
        print("""
              #######################
              #     Z1PBR34K3R       #
              #######################
              """)
        zipcrack()
        return True
    elif rec == "passgen":
        print("""
            #######################
            #    P4SSG3N3R4T0R    #
            #######################
            """)
        pass_gen()
        return True
    elif rec == "oigatum":
        
        return True
    else:
        return False

control = 0

while control == 0:
    if win() == False:
        print ("syntax_err0r...")
    elif win() == True:
        control = 1