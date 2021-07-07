# Music Genre Machine
# Python Flask app that chooses words from predefined lists
# -----

import random
from flask import Flask, render_template
from difflib import SequenceMatcher

wordsCombined = []
exclusiveTags = []
phraseLength = 3

def readFiles(filename, listToReadInto):
  fileHolder = open(filename, 'r')
  for line in fileHolder:
    if line.strip() and (line != None):
      listToReadInto.append(line.strip())
  return listToReadInto
  fileHolder.close()

# Could be moved into the main app route to refresh word list live instead of having to restart the app
readFiles('combined.txt', wordsCombined)
readFiles('exclusive-tags.txt', exclusiveTags)

def processWordList(listToProcess):
  wordStorage = []
  for w in listToProcess:
    wordTemp = []
    w = w.strip()
    wordTemp.append(w.split(';')[0])
    wordTemp.append(w.split(';')[1].split(','))
    wordStorage.append(wordTemp)
  return wordStorage

def getWordByTags(wordListFilter, *tagFilterList):
  matchingWordList = []
  exclusiveTagsFilterList = []
  inclusiveTagsFilterList = []
  for t in tagFilterList:
    t = str(t)
    if t is not "None":
      if t in exclusiveTags:
        exclusiveTagsFilterList.append(t)
        # print("exclusive tag: " + t)
      else:
        inclusiveTagsFilterList.append(t)
        # print("regular tag: " + t)
    else:
      getWordByTags(wordListFilter, tagFilterList)
  for l in wordListFilter:
    if all(search in l[1] for search in inclusiveTagsFilterList):
      # matchingWordList.append(l[0])
      if all(search not in l[1] for search in exclusiveTagsFilterList):
        matchingWordList.append(l[0])
  randomWord = random.choice(matchingWordList)
  return randomWord

def getTags(wordToCheck, wordsList):
  wordIdx = [i for i, ele in wordsList].index(wordToCheck)
  # print("wordIdx: ")
  # print(wordIdx)
  return wordsList[wordIdx][1]

def getWordWithoutTags(wordListFilter, *tagFilterList):
  returnList = []
  for l in wordListFilter:
    if all(search in l[1] for search in tagFilterList):
      returnList.append(l[0])
  randomWord = random.choice(returnList)
  return randomWord

app = Flask(__name__)

@app.route("/")
def index():
  wordsList = processWordList(wordsCombined)
  phrase = []
  phraseTags = []
  finalPhrase = ""
  for phraseIdx in range(phraseLength):
    pickedWord = getWordByTags(wordsList, phraseIdx)
    pickedWordTags = getTags(pickedWord, wordsList)
    for pt in (pickedWordTags):
      if not pt.isdecimal():
        # not appending tags indicating position
        # which are numeric
        phraseTags.append(pt)
    if (phraseIdx == 0):
    # If index is zero we are getting adjective 1 and not using sequence matcher
      phrase.append(pickedWord)
    else:
    # if we aren't on the first word in the phrase...
    # compare current word with previous word in phrase
      s = SequenceMatcher(None, phrase[phraseIdx-1], pickedWord)
      while s.ratio() > 0.8:
        print("Word too similar:")
        print(pickedWord)
        pickedWord = getWordByTags(wordsList, str(phraseIdx), phraseTags)
        s = SequenceMatcher(None, phrase[phraseIdx-1], pickedWord)
      phrase.append(pickedWord)

  # Join dashed words together
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
