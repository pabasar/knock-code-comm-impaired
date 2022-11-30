# -*- coding: utf-8 -*-

# Real time looping code
# Knocking for any desired number of words
# In the loop one word at a time

!pip install gTTS
!pip install pyspellchecker

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
from numpy.core.fromnumeric import mean
import pandas as pd
# %matplotlib inline
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import pickle
import imageio

from PIL import Image
from keras.preprocessing import image

import cv2
import os 
import glob
import argparse

from google.colab.patches import cv2_imshow

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

import matplotlib.pyplot as plt
import numpy as np
import wave, sys

import soundfile
import wave

from itertools import groupby
import collections

import librosa
import soundfile as sf

from io import BytesIO
from base64 import b64decode
from google.colab import output
from IPython.display import Javascript

import time

from spellchecker import SpellChecker

spell = SpellChecker()

from google.colab import drive
drive.mount('/content/drive')

knock_code_dict = {
    'A':'101',
    'B':'1011',
    'C':'10111',
    'D':'101111',
    'E':'1011111',
    'F':'1101',
    'G':'11011',
    'H':'110111',
    'I':'1101111',
    'J':'11011111',
    'L':'11101',
    'M':'111011',
    'N':'1110111',
    'O':'11101111',
    'P':'111011111',
    'Q':'111101',
    'R':'1111011',
    'S':'11110111',
    'T':'111101111',
    'U':'1111011111',
    'V':'1111101',
    'W':'11111011',
    'X':'111110111',
    'Y':'1111101111',
    'Z':'11111011111'
}

RECORD = """
const sleep  = time => new Promise(resolve => setTimeout(resolve, time))
const b2text = blob => new Promise(resolve => {
  const reader = new FileReader()
  reader.onloadend = e => resolve(e.srcElement.result)
  reader.readAsDataURL(blob)
})
var record = time => new Promise(async resolve => {
  stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  recorder = new MediaRecorder(stream)
  chunks = []
  recorder.ondataavailable = e => chunks.push(e.data)
  recorder.start()
  await sleep(time)
  recorder.onstop = async ()=>{
    blob = new Blob(chunks)
    text = await b2text(blob)
    resolve(text)
  }
  recorder.stop()
})
"""

def record(sec=3):
  
  files = glob.glob('/content/drive/MyDrive/knock_code_research/input_sample/*')
  for f in files:
    os.remove(f)
  
  print("")
  print("Knock Now...")
  display(Javascript(RECORD))
  sec += 1
  s = output.eval_js('record(%d)' % (sec*1000))
  b = b64decode(s.split(',')[1])
  with open('/content/drive/MyDrive/knock_code_research/input_sample/temp.wav','wb') as f:
    f.write(b)
  return '/content/drive/MyDrive/knock_code_research/input_sample/temp.wav'
  #return b #byte stream

# visualize waveform of audio file and save as an image

def visualize(path: str):

	raw = wave.open(path, 'r')

	signal = raw.readframes(-1)
	signal = np.frombuffer(signal, dtype ="int16")

	f_rate = raw.getframerate()

	time = np.linspace(
		0, # start
		len(signal) / f_rate,
		num = len(signal)
	)

	plt.axis("off")
	plt.figure(1)
	
	plt.plot(time, signal)
	#plt.show()
	#img = plt.show()
	
	files = glob.glob('/content/drive/MyDrive/knock_code_research/waveforms/*')
	for f in files:
		os.remove(f)
	
	fig1 = plt.gcf()
	plt.show()
	plt.draw()
	fig1.savefig('/content/drive/MyDrive/knock_code_research/waveforms/sample.png', dpi=300, transparent=True)

def letter_code_out(input_lst):
  zero_ind = []
  for i in range(len(input_lst)):
    if input_lst[i]=='0':
      zero_ind.append(i)

  for i in range(len(zero_ind)):
    if i%2!=0:
      input_lst[zero_ind[i]]='-'

  letter_code_str = ''
  letter_code_str = letter_code_str.join(input_lst)


  letter_code = letter_code_str.split('-')

  return letter_code

from math import log
words = open("/content/drive/MyDrive/knock_code_research/words/sowpods.txt").read().split()
wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
maxword = max(len(x) for x in words)

# Function to seperate words
def infer_spaces(s):

    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
        return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)

    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i)
        cost.append(c)

    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))

def spell_check(word):
  misspelled = spell.unknown([word])

  suggestions = []

  for i in misspelled:
    suggestions = list(spell.candidates(i))

  if len(suggestions)!=0:
    return False
  else:
    return True

# Function to correct C and K confusion
def ck_correction(ck_word):
  misspelled = spell.unknown([ck_word])

  suggestions = []

  for i in misspelled:
    suggestions = list(spell.candidates(i))


  corrected = ''
  word_list_appl = []

  for i in suggestions:
    if (('c' in i) or ('k' in i)) and len(i)==len(ck_word):
      word_list_appl.append(i)


  non_c_ind = []
  c_ind = []

  for i in range(len(ck_word)):
    if ck_word[i]!='c':
      non_c_ind.append(i)
    if ck_word[i]=='c':
      c_ind.append(i)


  word_list_appl2 = []

  for i in word_list_appl:
    match_nc = 0
    for j in non_c_ind:
      if ck_word[j]==i[j]:
        match_nc+=1
    if match_nc==len(non_c_ind):
      word_list_appl2.append(i)

  for i in word_list_appl2:
    match_c = 0
    for j in c_ind:
      if i[j]=='c' or i[j]=='k':
        match_c+=1
    if match_c==len(c_ind):
      corrected=i
 

  if len(corrected)!=0:
    return corrected
  else:
    return ck_word

import warnings
warnings.filterwarnings('ignore')

long_msg = ""

ans='Y'

# Looping
while (ans=='Y' or ans=='y'):

  time.sleep(3)

  audio = record(80)

  x,_ = librosa.load('/content/drive/MyDrive/knock_code_research/input_sample/temp.wav', sr=16000)
  sf.write('/content/drive/MyDrive/knock_code_research/input_sample/sample.wav', x, 16000)

  if __name__ == "__main__":
    path = sys.argv[1]
    visualize("/content/drive/MyDrive/knock_code_research/input_sample/sample.wav")
 
  img = cv2.imread('/content/drive/MyDrive/knock_code_research/waveforms/sample.png')
  imgIni = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert the input image to grayscale
  ret,img_t = cv2.threshold(imgIni,130,255,cv2.THRESH_BINARY_INV) # Binarize the image
  kernel = np.ones((4, 4), np.uint8)
  img_erosion = cv2.erode(img_t, kernel, iterations=1)
  kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(1,1))
  img_mphrd = cv2.morphologyEx(img_erosion, cv2.MORPH_CLOSE, kernel)
  contrs2 = cv2.findContours(img_mphrd, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
  cnts2 = sorted(contrs2, key=cv2.contourArea)[-1]
  x,y,w,h = cv2.boundingRect(cnts2)
  img_dst = img_mphrd[y:y+h, x:x+w]

  img_arr = np.array(img_dst)
  row_size = len(img_arr) - 1   # Getting the last index of the row
  col_size = len(img_arr[0]) - 1   # Getting the last index of the column

  mid_range = []

  for i in range(img_arr.shape[0]):
    if np.all(img_arr[i]==255):
      mid_range.append(i)

  mid_line = int(mean(mid_range))

  readY = int(mid_line/1.8)

  bw = ""

  for i in range(col_size):
    if img_arr[readY][i]==0:
      bw+="0"
    elif img_arr[readY][i]==255:
      bw+="1"

  bw = bw.strip('0')
  bw_list = [''.join(g) for _, g in groupby(bw)]

  one_len = []
  zero_len = []

  for i in bw_list:
    if i[0]=='1':
      one_len.append(len(i))
    elif i[0]=='0':
      zero_len.append(len(i))

  min_zero_len = 0
  min_one_len = 0

  min_zero_len = min(zero_len)
  min_one_len = min(one_len)

  bw_list_simp = [[],[],[],[],[],[],[],[],[]]

  for i in bw_list:
    if i[0]=='1':
      for x in range(len(bw_list_simp)):
        if len(i)<=(x+2)*min_one_len:
          bw_list_simp[x].append('1')
    
    if i[0]=='0':
      for x in range(len(bw_list_simp)):
        if len(i)>=(x+2)*min_zero_len:
          bw_list_simp[x].append('0')


  bw_str_lst = []

  for i in range(len(bw_list_simp)):
    str_temp = ''
    str_temp = ''.join(bw_list_simp[i])
    bw_str_lst.append(str_temp)

  letter_codes = []

  for i in range(len(bw_list_simp)):
    letter_codes.append(letter_code_out(bw_list_simp[i]))

  msg_lst = []

  for x in range(len(letter_codes)):
    message = ''
    for i in letter_codes[x]: 
      for j in knock_code_dict.items(): 
        if i==j[1]:
          message+=j[0]
    msg_lst.append(message.lower())

  while("" in msg_lst):
    msg_lst.remove("")

  for i in msg_lst[:]:
    if len(i) == 1:
      msg_lst.remove(i)  

  sentence = []

  frequency = collections.Counter(msg_lst)

  freq_dict = dict(frequency)

  for i in freq_dict:
    if freq_dict[i] == max(freq_dict.values()):
      sentence.append(i)

  word_seperated_imp = []

  for i in sentence:
    word_seperated_imp.append(infer_spaces(i))
    
  word_seperated_imp = list(set(word_seperated_imp))

  words_list = []

  for i in word_seperated_imp:
    words_list.append(i.split())

  if len(words_list[0])!=0:
    word_set = words_list[0]

  for i in word_set:
    for j in i:
      if 'c' in j:
        word_set = list(map(lambda x: x.replace(i, ck_correction(i)), word_set))  

  for i in word_set:
    long_msg += (i.capitalize()+' ')

  print("\033[1m" + long_msg + "\033[0m")

  ans = input("\nContinue? (Y/N)\n")

from gtts import gTTS
from IPython.display import Audio
from IPython.display import display
import os

language = 'en'

audio_obj = gTTS(text=long_msg, lang=language, slow=True)

speech_dir = glob.glob('/content/drive/MyDrive/knock_code_research/speech_out/*')
for f in speech_dir:
  os.remove(f)

audio_obj.save("/content/drive/MyDrive/knock_code_research/speech_out/speech.mp3")

wn = Audio("/content/drive/MyDrive/knock_code_research/speech_out/speech.mp3", autoplay=True)

# Output text and speech
print( "\033[1m" + long_msg + "\033[0m")
display(wn)

