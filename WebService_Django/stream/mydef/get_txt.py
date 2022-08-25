import pickle
import os

def write_txt(label):
    filePath = './detected.txt'



    with open(filePath, mode='a', encoding='utf-8') as f:
        f.write(str(label) + '\n')
        f.close()



def read_txt(path = './detected.txt'):
    lists = []
    with open(path, mode='rt', encoding='utf-8') as r:
        for line in r:
            line = line.rstrip('\n')
            line = int(line)
            lists.append(line)

    with open(path,'w') as f:
        pass

    return lists
