# encoding: utf-8
#####################################################
######  Introduction à la cryptographie  	###
#####   Codes de Huffman             		###
####################################################

import heapq
import sys
import pickle

###  distribution de proba sur les letrres

caracteres = [
    ' ', 'a', 'b', 'c', 'd', 'e', 'f',
    'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z'
]

proba = [
    0.1835, 0.0640, 0.0064, 0.0259, 0.0260, 0.1486, 0.0078,
    0.0083, 0.0061, 0.0591, 0.0023, 0.0001, 0.0465, 0.0245,
    0.0623, 0.0459, 0.0256, 0.0081, 0.0555, 0.0697, 0.0572,
    0.0506, 0.0100, 0.0000, 0.0031, 0.0021, 0.0008
]


def frequences():
    table = {}
    n = len(caracteres)
    for i in range(n):
        table[caracteres[i]] = proba[i]
    return table


F = frequences()

###  la classe Arbre

class Arbre:
    def __init__(self, lettre, gauche=None, droit=None):
        self.gauche = gauche
        self.droit = droit
        self.lettre = lettre

    def estFeuille(self):
        return self.gauche == None and self.droit == None

    def estVide(self):
        return self == None

    def __str__(self):
        return '<' + str(self.lettre) + '.' + str(self.gauche) + '.' + str(self.droit) + '>'


###  Ex.1  construction de l'arbre d'Huffamn utilisant la structure de "tas binaire"
def arbre_huffman(frequences):
    tas = [(0, 'NYT', Arbre("NYT"))]  # init et implémentation du Not Yet Transfered
    for elem in frequences:
        tas.append((frequences[elem], elem, Arbre(elem)))
    heapq.heapify(tas)
    while len(tas) != 1:
        num1 = heapq.heappop(tas)
        num2 = heapq.heappop(tas)
        arbretemp = Arbre(None, gauche=num1, droit=num2)
        heapq.heappush(tas, (num1[0] + num2[0], None, arbretemp))
    return heapq.heappop(tas)[2]


ArbreGeneral = arbre_huffman(F)


###  Ex.2  construction du code d'Huffamn

def parcours(arbre, prefixe, code):

    def arbreRecursif(arbre: Arbre, path, code) -> None:

        if arbre.estFeuille():
            code[arbre.lettre] = prefixe.join(path)
            return

        if arbre.gauche:
            arbreRecursif(arbre.gauche[2], path + "0", code)

        if arbre.droit:
            arbreRecursif(arbre.droit[2], path + "1", code)

    arbreRecursif(arbre, "", code)
    return code


def code_huffman(arbre):
    # on remplit le dictionnaire du code d'Huffman en parcourant l'arbre
    code = {}
    parcours(arbre, '', code)
    return code


dico = code_huffman(ArbreGeneral)


###  Ex.3  encodage d'un texte contenu dans un fichier

def encodage(dico, fichier):
    try:
        file = open(fichier, "r", encoding="utf-8")
        filestr = file.read()
        file.close()
    except FileNotFoundError:
        print("File not found")
        exit()
    dicofile = open('dico', "wb")
    pickle.dump(dico, dicofile)
    encodedfile = ""
    for elem in filestr:

        try:
            encodedfile += dico[elem]
        except KeyError:
            charbyte = bin(int.from_bytes(elem.encode('utf-8'), "big")).split('b')[1]
            compteur = 0
            if len(charbyte) < 9:
                encodedfile += dico["NYT"] + ((7 - len(charbyte)) * "0") + charbyte
            else:
                encodedfile += dico["NYT"] + ((31 - len(charbyte)) * "0") + charbyte

    i = 0
    encodebytes = bytearray()
    while i < len(encodedfile):
        encodebytes.append(int(encodedfile[i:i + 8], 2))
        i += 8

    return encodebytes

if len(sys.argv) == 2:
	filename = sys.argv[1]
else:
	print("Argument Error - (python3 main.py filename)")
	exit()
encode = encodage(dico, filename)

filenamewrite = filename.split(".")[0] + "Encoded.bin"
with open(filenamewrite, "w+b") as filewrite:
    filewrite.write(encode)


##  Ex.4  décodage d'un fichier compresse

def decodage(arbre, fichierCompresse):

    # ouverture du fichier
    try:
        file = open(fichierCompresse, "rb")
        binfile = file.read()
        file.close()
    except FileNotFoundError:
        print("File not found")
        exit()
    dicofile = open('dico', "rb")
    dico = pickle.load(dicofile)
    if len(binfile) == 0:
        raise ValueError("EmptyFileError")


    string = str()
    dico_reverse = {}
    mode_ascii = False

    binary_data = str()
    for elem in binfile:
        charbyte = bin(int(elem)).split('b')[1]
        binary_data += ((8 - len(charbyte)) * "0") + charbyte
    for elem in dico:
        dico_reverse[dico[elem]] = elem
    bin_array = str()
    for bina in binary_data:
        bin_array = bin_array + str(bina)
        try:
            if not mode_ascii:
                #Le mode ascii permet de passer en mode de décodage de NYT
                caractere = dico_reverse[str(bin_array)]
                if caractere == 'NYT':
                    caractere = False
                    mode_ascii = True
                    bin_array = str()
            elif len(bin_array) == 7:
                try:
                    binary_int = int(bin_array, 2);
                    byte_number = binary_int.bit_length() + 7 // 8
                    # Getting an array of bytes
                    binary_array = binary_int.to_bytes(byte_number, "big")
                    # Converting the array into ASCII text
                    ascii_text = binary_array.decode('utf-8')
                    # Getting the ASCII value
                    caractere = ascii_text[len(ascii_text) - 1]
                    mode_ascii = False
                except Exception:
                    pass
            if mode_ascii and len(bin_array) == 31:
                #decodage d'un NYT 32 bits
                binary_int = int(bin_array, 2);
                byte_number = binary_int.bit_length() + 31 // 32
                # Getting an array of bytes
                binary_array = binary_int.to_bytes(byte_number, "big")
                # Converting the array into ASCII text
                ascii_text = binary_array.decode('utf-8')
                caractere = ascii_text[len(ascii_text) - 1]
                mode_ascii = False

        except KeyError:
            caractere = False

        if caractere:
            string = string + caractere
            bin_array = str()
    print("Message décodé: \n\n")
    print(string)


decode = decodage(ArbreGeneral, filenamewrite)
