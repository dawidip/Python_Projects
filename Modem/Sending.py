import numpy as np
import pulseaudio as pa
import time
import sys
import zlib
import threading





sym_time = 0.01
framerate = 44000
amplitude = 4000
frequencyZero = 400
frequencyOne = 600
pointsZero = framerate/frequencyZero
pointsOne = framerate/frequencyOne
stepZero = np.pi*2/pointsZero
stepOne = np.pi*2/pointsOne
pointsFour = framerate/800
stepFour = np.pi*2/pointsFour
num_of_samples = int(sym_time * framerate)
codec = ['11110' , '01001', '10100', '10101', '01010', '01011', '01110', '01111','10010', '10011', '10110', '10111', '11010', '11011', '11100', '11101']
decodec = ['0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0001', '0100', '0101', '0000', '0000', '0110', '0111', '0000', '0000', '1000', '1001', '0010', '0011', '1010', '1011', '0000', '0000', '1100', '1101', '1110', '1111', '0000']
preambul = '1010101010101010101010101010101010101010101010101010101010101011'



toneZero = (amplitude * np.sin( np.r_[0:num_of_samples*stepZero:stepZero])).astype(np.int16).tostring()

toneOne = (amplitude * np.sin( np.r_[0:num_of_samples*stepOne:stepOne])).astype(np.int16).tostring()

toneFour = (amplitude * np.sin( np.r_[0:num_of_samples*stepFour:stepFour])).astype(np.int16).tostring()


def fourB5B(mes):
    i = 0
    endOfMessage = (len(mes) - len(mes)%4)
    res = ''
    while i + 4 <= endOfMessage:
        res += codec[int(mes[i:i+4], 2)]
        i += 4
    i = endOfMessage;
    if i <= len(mes):
        res += mes[i: len(mes)]
    return res

def fiveB4B(mes):
    i = 0
    endOfMessage = (len(mes) - len(mes)%5)
    res = ''
    while i + 5 <= endOfMessage:
        res += decodec[int(mes[i:i+5], 2)]
        i += 5
    i = endOfMessage
    if i <= len(mes):
        res += mes[i: len(mes)]
    return res


def generateAdress(adressMac):
	return '0'*(48 - len(bin(adressMac)[2:])) + bin(adressMac)[2:];

def generateLen(message):
	return '0'*(16 - len(message)) + message;

def generateCRC32(message):
	return '0'*(32 - len(bin(np.abs(zlib.crc32(message)))[2:])) + bin(np.abs(zlib.crc32(message)))[2:];

def sent(myAdress, receiverAdress, message):       
        mes = preambul + fourB5B(generateAdress(myAdress) + generateAdress(receiverAdress) + message + generateCRC32(generateAdress(myAdress) + generateAdress(receiverAdress) + message)) + "11111111"
        return mes;

def stringToBin(message):
    return ''.join('{:08b}'.format(ord(c)) for c in message)
def binToString(message):
    return ''.join(chr(int(message[i:i+8], 2)) for i in xrange(0, len(message), 8))

def generateTone(toneToPlay):
    with pa.simple.open(direction = pa.STREAM_PLAYBACK, format = pa.SAMPLE_S16LE, rate = framerate, channels = 1) as player:
        player.write(toneToPlay)



if __name__ == '__main__':
    
    message = "Litwo, Ojczyzno moja! ty jestes jak zdrowie; Ile cie trzeba cenic, ten tylko sie dowie, Kto cie stracil. Dzis pieknosc twa w calej ozdobie Widze i opisuje, bo tesknie po tobie. Panno swieta, co Jasnej bronisz Czestochowy I w Ostrej swiecisz Bramie! Ty, co grod zamkowy Nowogrodzki ochraniasz z jego wiernym ludem! Jak mnie dziecko do zdrowia powrocilas cudem"
    # w zmienna message wpisac wiadomosc do wyslania    
    
    myAdress = 1114964          #adres moj
    whereAdress = 1119999       #adres odbiorcy
    
    mes = sent(myAdress, whereAdress, stringToBin(message))
               

    print "Message to be sent:"
    print ""    
    print message
    print ""
    print ""

    ton = toneZero
    for i in range (0, len(mes)):
        if(mes[i] == "1"):
            ton += toneOne
        else:
            ton += toneZero
    for i in range (0,30):
        ton += toneFour

    print "Starting to play " + str(len(mes)) + " bytes... Enjoy!"

    generateTone(ton)	


#0000000000000000000000000001000100000011010101000000000000000000000000000001000100010110111111110000000001000011010000111011100110100110000111011101001
#0000000000000000000000000001000100000011010101000000000000000000000000000001000100010110111111110000000001000011010000111011100110100110000111011101001

