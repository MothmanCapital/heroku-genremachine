# class for managing shared url data

import shortuuid

from time import time
from google.cloud import firestore


class UrlShare(object):
    def __init__(self, phrase=None, img_url=None, search_term=None, uuid=None, clicks=0):
        # Initialize Firebase connection
        self.db = firestore.Client(project="genremachine-2e8a4")
        self.collection = self.db.collection("shared_urls")
        if uuid == None:
            if (phrase == None) or (img_url == None) or (search_term == None):
                print("Must provide either uuid or all of: phrase, img_url, search_term")
            self.uuid = shortuuid.uuid()[:10]
            self.created = int(time())
            self.phrase = phrase
            self.img_url = img_url
            self.search_term = search_term
            self.clicks = clicks

            if self.check_duplicate():
                self.commit()
                print("Saved link")
            else:
                print("picture already in use. Did not save")


        else:
            self.uuid = uuid
            doc = self.collection.document(self.uuid).get().to_dict()
            self.created = doc['created']
            self.phrase = doc['phrase']
            self.img_url = doc['img']
            self.search_term = doc['search']
            self.clicks = doc['clicks']
            self.add_click()


    def add_click(self):
        self.clicks = int(self.clicks) + 1
        self.commit()

    def check_duplicate(self):
        duplicate_query = self.collection.where("img", "==", self.img_url).stream()
        for i in duplicate_query:
            if i:
                print(f"duplicate: {i.id} => {i.to_dict()}")
            return False
        else:
            return True

    def commit(self):
        self.collection.document(self.uuid).set(
            {
                "phrase": self.phrase,
                "img": self.img_url,
                "search": self.search_term,
                "created": self.created,
                "clicks": self.clicks,
            }
        )
        return True

    def __repr__(self):
        return f"UrlShare(\
        uuid={self.uuid}, \
        created={self.created}, \
        phrase={self.phrase}, \
        search_term={self.search_term}, \
        img_url={self.img_url}, \
        clicks={self.clicks}\
      )"
