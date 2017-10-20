'''
CS591 Final Project: Chord Recognition
Yida Xu, Wenjun Shen
'''

import array
import contextlib
import wave
import numpy as np
import matplotlib.pyplot as plt
from math import log

# file name

filename = 'FminorPart2.wav'

# notes and frequencies of the third octave

octaveN = ['C'    , 'C#'   , 'D'    , 'Eb'   , 'E'    , 'F'    , 'F#'   , 'G'    , 'Ab'   , 'A'  , 'Bb'   , 'B']
octaveF = [130.813, 138.591, 146.832, 155.563, 164.814, 174.614, 184.997, 195.998, 207.652, 220.0, 233.082, 246.942]

# Read a wave file and return the entire file as a standard array

def readWaveFile(infile,withParams=False,asNumpy=False):
    with contextlib.closing(wave.open(infile)) as f:
        params = f.getparams()
        frames = f.readframes(params[3])
        if(params[0] != 1):
            print("Warning in reading file: must be a mono file!")
        if(params[1] != 2):
            print("Warning in reading file: must be 16-bit sample type!")
        if(params[2] != 44100):
            print("Warning in reading file: must be 44100 sample rate!")
    if asNumpy:
        X = np.array(frames,dtype='int16')
    else:  
        X = array.array('h', frames)
    if withParams:
        return X,params
    else:
        return X
        
# return a list of triples of form  (f, A) for each frequency
# f detected by the transform
    
def spectrumFFT(X):
    S = []
    R = np.fft.rfft(X)
    WR = 44100/len(X)
    for i in range(len(R)):
        S.append( ( i*WR, 2.0 * np.absolute(R[i])/len(X) ) )
    return S
    
# return the closet note for the given frequency in term of (noteStr, noteFreq)

def findNote(F):
    refinedF = []
    
    for f in F:
        # find the key's index within an octave
        deviation = [abs(round(log(f / o, 2)) - log(f / o, 2)) for o in octaveF]
        i = deviation.index(min(deviation))
        
        # compute span relative to the 3rd octave
        span = round(log(f / octaveF[i], 2))
        
        # make sure this note is within the piano's range (A0 to C8)
        A0 = pow(2, 0-3) * octaveF[9]
        C8 = pow(2, 8-3) * octaveF[0]
        if A0 <= pow(2, span) * octaveF[i] <= C8:
            refinedF += [(octaveN[i] + str(3 + span), pow(2, span) * octaveF[i])]
    
    return refinedF

# filter the spectrum and get the frqeuencies loud enough to be heard

def spectrumFilter(S):
    F = []
    
    for (f, A) in S:
        if A > 350:
            F += [f]
    return F
    
# main function7

def main():
    X1 = readWaveFile(filename)
    X = []
    
    # mu-law
    for i in range(len(X1)):
        y = log(1 + (255 * abs(X1[i]) / 32767), 2) / log(256, 2)
        if y != 0:
            X += [X1[i] * y]
        else:
            X += [0]
            
    xaxis = []    # time
    yaxis = []    # frequencies
    yname = []    # yticks (note names)
    ws = pow(2, 16)
    slide = pow(2, 14)
    index = 0
    
    while index < len(X):
        # slice off a window piece
        window = X[index : index + ws]
        
        # perform FFT on the window and filter the spectrum
        spectrum = spectrumFFT(window)
        F = spectrumFilter(spectrum)
        
        # find the closet notes for each frequency in terms of (noteName, noteFreq)
        freq = findNote(F)
        
        # add useful frequencies to the axises along with time
        for f in freq:
            xaxis += [(index + (ws / 2)) / 44100]
            yaxis += [f[1]]
            yname += [f[0]]
            
        index += slide

    # plot the graph   
    plt.scatter(xaxis, yaxis)
    plt.gca().set_xlim(0, len(X) / 44100)
    plt.gca().set_ylim(min(yaxis) / 2, max(yaxis) + 20)
    plt.yticks(yaxis, yname) 
    plt.grid(True)
    plt.show()

main()    
# EOF