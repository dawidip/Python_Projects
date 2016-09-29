import numpy as np
import pulseaudio as pa
import time
import sys
import zlib
import threading


framerate = 44000
frame = 440
timeInSec = 6

codec = ['11110' , '01001', '10100', '10101', '01010', '01011', '01110', '01111','10010', '10011', '10110', '10111', '11010', '11011', '11100', '11101']
decodec = ['0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0001', '0100', '0101', '0000', '0000', '0110', '0111', '0000', '0000', '1000', '1001', '0010', '0011', '1010', '1011', '0000', '0000', '1100', '1101', '1110', '1111', '0000']
preambul = '1010101010101010101010101010101010101010101010101010101010101011'

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

def generateCRC32(message):
	return '0'*(32 - len(bin(np.abs(zlib.crc32(message)))[2:])) + bin(np.abs(zlib.crc32(message)))[2:];

def stringToBin(message):
    return ''.join('{:08b}'.format(ord(c)) for c in message)
def binToString(message):
    return ''.join(chr(int(message[i:i+8], 2)) for i in xrange(0, len(message), 8))

def receiveMessage(mes):
    i = 0
    while(i + len("101010101010101010101010101010101010101011") != len(mes)):
        if(mes[i: i+len("101010101010101010101010101010101010101011")] == "101010101010101010101010101010101010101011"):
            break
        i+=1

    mes = mes[i + len("101010101010101010101010101010101010101011"): len(mes) - 8]
    mes = fiveB4B(mes)

    nadawcaAdress = int(mes[0:48],2)
    dokogoAdress = int(mes[48:96],2)
    
    if(generateCRC32(mes[:len(mes) - 32]) == mes[len(mes) - 32:]):
        print "CRC STATUS=OK"
    else:
        return "#"

    print "Nadawano     z   : " + str(nadawcaAdress)
    print "Przeznaczone dla : " + str(dokogoAdress)

    return binToString(mes[96:len(mes) - 32])

def getHzFrequency(arr, i):

    array_temp = arr[i: i + frame]
    array_temp = np.abs(np.fft.fft(array_temp))
    freqs = np.fft.fftfreq(len(array_temp))
    idx = np.argmax(array_temp)
    hertzFrequency = abs(framerate * freqs[idx])
    return hertzFrequency




with pa.simple.open(direction = pa.STREAM_RECORD, format = pa.SAMPLE_S16LE, rate = framerate, channels = 1) as recorder:
    arr = recorder.read(4400000)
    arr = np.fromstring(arr, np.int16)
	
    toFinish = '11111111'
    actFinish = '00000000'
    mes = '0'
    x = -1;    
    ind = -1;
    
    for i in xrange (0, len(arr) - frame, frame):
        
        hertz = getHzFrequency(arr, i)
        if(610 >= hertz and hertz >= 390):            
            for j in range (i - frame, i + frame):  
                one = 0
                zero = 0
                for z in xrange (j, len(arr) - frame, frame):
                    hertz = getHzFrequency(arr, z)
                    if(hertz == 600):
                        one += 1
                    elif (hertz == 400):
                        zero += 1
                    else:
                        break
                    if(abs(zero - one) > 1):
                        break
                    if(zero == 29):
                        ind = j
                        break
                if(ind != -1):
                    break
        if(ind != -1):
            break
    
    finind = ind + frame + 1
    finalmes = ""        
    while ind < finind:
        mes = "7"    
        for i in xrange (ind, len(arr) - frame, frame):
            
            hertz = getHzFrequency(arr, i)
            if(580 <= hertz and hertz <= 620):
                x = 1
            elif(380 <= hertz and hertz <= 420):
                x = 0        
            else: 
                x = 3
                break        

            mes += str(x)
            actFinish = actFinish[1:8] + str(x)
            if( actFinish == toFinish and 200 < len(mes) and getHzFrequency(arr, i + frame)!=600 and getHzFrequency(arr, i+frame) != 400):
                #print i
                #print len(arr)                
                break
                    
        ind += 5
        if (len(mes) < 200):  
            continue
        finalmes = receiveMessage(mes)
        if(finalmes != "#"):       
            break
    
    print ""
    print ""
    if(finalmes == "#"):       
        finalmes = "CRC ERROR, SOMETHING WENT WRONG :(" 
    print finalmes
    print ""
    print ""
    print "KONIEC WIADMOSCI"
    print "Milego dnia :)"
