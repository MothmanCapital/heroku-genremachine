import random
from flask import Flask, render_template
from difflib import SequenceMatcher

a = []
b = []
c = []

wordList = []
phraseLength = 3

x = open('prefix.txt', 'r')
y = open('first.txt', 'r')
z = open('second.txt', 'r')

for line in x:
  if line.strip():
    a.append(line)
for line in y:
  if line.strip():
    b.append(line)
for line in z:
  if line.strip():
    c.append(line)

wordList.append(a)
wordList.append(b)
wordList.append(c)

x.close()
y.close()
z.close()

def getWord(wordList, arr, idx):
  randomWord = random.choice(wordList)
  if idx > 0:
    s = SequenceMatcher(None, arr[idx-1], randomWord)
    if s.ratio() < 0.8:
      return randomWord
    else:
      getWord(wordList, arr, idx)
  else:
    return randomWord

app = Flask(__name__)

@app.route("/")
def index():

  phrase = []
  finalPhrase = ""
  for phraseIdx in range(phraseLength):
    phrase.append(str(getWord(wordList[phraseIdx], phrase, phraseIdx)).rstrip())

  for phraseIdx in range(phraseLength):
    if not(phrase[phraseIdx].endswith('-')):
      finalPhrase += phrase[phraseIdx] + " "
    else:
      finalPhrase += phrase[phraseIdx]
  print(finalPhrase)
  result = finalPhrase

  return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run()
