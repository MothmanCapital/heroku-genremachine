# Music Genre Machine
# Python Flask app that chooses words from predefined lists
# -----

import random, os, logging, httpimport

from flask import Flask, render_template, escape

from difflib import SequenceMatcher

with httpimport.github_repo('MothmanCapital', 'pyunsplash', branch = 'add-support-for-embed-urls'):
    from pyunsplash import PyUnsplash

client_id = os.environ['UNSPLASH_ID']
client_secret = os.environ['UNSPLASH_KEY']
redirect_uri = os.environ['UNSPLASH_REDIR']

# Initialize PyUnsplash app logging
logger = logging.getLogger()
logging.basicConfig(filename='app.log', level=logging.DEBUG)
logging.getLogger(PyUnsplash.logger_name).setLevel(logging.DEBUG)

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
    if (t != "None"):
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
  bg_search_term = max(finalPhrase.split(" "), key=len)
  print(bg_search_term)
  # unsplash_photo = api.photo.random(query=bg_search_term, w=550, h=200)[0]
  # py_un = PyUnsplash(api_key=client_id)
  api = PyUnsplash(api_key=client_id)
  unsplash_photo_coll = api.photos(type_='random', count=1, query=bg_search_term)
  # print(unsplash_photo_coll.__dict__)


  if not hasattr('unsplash_photo_coll.body', 'errors'):
    unsplash_photo = []
    for entry in unsplash_photo_coll.entries:
      unsplash_photo.append(entry)
  
    print("body ")
    print(unsplash_photo[0].body['urls'])
    print()
    print()

    unsplash_html_link = unsplash_photo[0].body['urls']['raw'] + "&w=550&h=200"
    print(unsplash_html_link)

  if unsplash_html_link:
    bg_image = str("url(\"") + str(unsplash_html_link) + str("\")")
  else:
    bg_image = str("linear-gradient(blue, green)")

  return render_template("index.html", result=result, bg_image=escape(bg_image))

if __name__ == "__main__":
    app.run()
