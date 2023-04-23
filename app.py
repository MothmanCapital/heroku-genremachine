# Music Genre Machine
# Python Flask app that chooses words from predefined lists
# -----

import random, os, logging, httpimport

# imports for firestore
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
from firebase_admin import firestore

from flask import Flask, render_template, request, flash, redirect, url_for
from difflib import SequenceMatcher

from UrlShare import UrlShare

with httpimport.github_repo('MothmanCapital', 'pyunsplash', branch = 'add-support-for-embed-urls'):
    from pyunsplash import PyUnsplash

# initialize firestore connection
cred = credentials.Certificate("genremachine.json")
firebase_admin.initialize_app(cred)

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
    if line.strip() and (line != None) and (line[0] != "#"):
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
  randomWord = ""
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
  if len(matchingWordList) > 0:
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

def randColor():
    color = "%06x" % random.randint(0, 0xFFFFFF)
    return str(color)

def getUnsplashPhoto(search_term, w=640, h=480):
  # instantiate pyunsplash connection object
  api = PyUnsplash(api_key=client_id)

  print(search_term.strip("-"))

  try:
    # Retrieve random photo matching search term from unsplash
    unsplash_photo_coll = api.photos(type_='random', count=1, query=search_term.strip("-"))

    # retrieve raw url of photo
    unsplash_photo = next(unsplash_photo_coll.entries).body['urls']['raw'] + "&w=" + str(w) + "&h=" + str(h)
    bg_image = r'url("' + unsplash_photo + r'")'
  except:
    bg_image = "linear-gradient(" + str(random.randint(0, 180)) + "deg, #" + randColor() + ", #" + randColor() + ")"

  return bg_image

app = Flask(__name__)

@app.route("/")
def index():
  print("-----new genre-----")
  wordsList = processWordList(wordsCombined)
  phrase = []
  phraseTags = []
  unsplash_search_eligible = []
  finalPhrase = ""
  for phraseIdx in range(phraseLength):
    pickedWord = getWordByTags(wordsList, phraseIdx)
    pickedWordTags = getTags(pickedWord, wordsList)
    # check to see if word can be photo searched
    if 'p' in pickedWordTags:
      unsplash_search_eligible.append(pickedWord)

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

  # Pick background photo 
  print("searchable words: ")
  print(unsplash_search_eligible)

  if len(unsplash_search_eligible) > 0:
    search_term = random.choice(unsplash_search_eligible)
    print("searching for " + search_term)
    bg_image = getUnsplashPhoto(search_term)
  else:
    print("default search for ocean picture, none of the random terms look like they would work")
    search_term = "ocean"
    bg_image = getUnsplashPhoto('ocean')

  print(bg_image)
  # Join dashed words together
  for phraseIdx in range(phraseLength):
    if not(phrase[phraseIdx].endswith('-')):
      finalPhrase += phrase[phraseIdx] + " "
    else:
      finalPhrase += phrase[phraseIdx]

  print(finalPhrase)

  # abandoned this method of searching for picture
  # bg_search_term = max(finalPhrase.split(" "), key=len)
  # print(bg_search_term)

  return render_template("index.html", result=finalPhrase, bg_image=bg_image, search_term=search_term)

def save_url(phrase=None, img=None, search=None):
  new_shared_url = UrlShare(phrase, img, search)
  new_shared_url.commit()

@app.route("/share", defaults={'share_uuid': None})
@app.route("/share/<share_uuid>") # , methods=['GET', 'POST'])
def share(share_uuid):
  # Initialize Firebase connection
  db = firestore.Client(project='genremachine-2e8a4')
  shared_genre = db.collection(u'shared_urls').document(share_uuid)

  if share_uuid == None:
    save_url(phrase=None, img=None, search=None)
  sg = shared_genre.get()
  if sg.exists:
      print(sg.to_dict())
      return sg.to_dict()
  else:
      print(u'No such document!')
      return "No such document!"

if __name__ == "__main__":
    app.run()
    gunicorn_logger = logging.getLogger('gunicorn.error')
