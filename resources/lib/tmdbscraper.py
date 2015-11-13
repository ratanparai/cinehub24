# -*- coding: utf-8 -*-

'''
    Genesis Add-on
    Copyright (C) 2015 Ratan Sunder Parai

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from urllib import urlopen
import json
from movieinfo import movieinfo
import re
import urllib
import base64
import os
import xbmc
import sqlite3

class tmdbscraper:
    
    # path to database
    dburl = urldb = os.path.join(xbmc.translatePath("special://userdata/addon_data/plugin.video.cinehub/cinehubdb.db"))
    
    API = base64.urlsafe_b64decode("N2U5MTYyMjM1NWFjZjI3NDM3ODQzNjcyMzRlOTFhODU=")
    
    def __init__(self):
        self.dbcon = sqlite3.connect(self.dburl)
        self.dbcur = self.dbcon.cursor()
    
    def searchMovie(self, name, year=""):
        URL = "http://api.themoviedb.org/3/search/movie?api_key="+self.API+"&query=" + urllib.quote_plus(name) + "&year=" + str(year)
        result = urlopen(URL)
        moviejson = json.load(result)
        
        if moviejson['total_results'] == 0 :
            return 0
        
        return moviejson['results'][0]['id']
    
    def getMovieInfoFromCache(self, res):
        '''
        return movieinfo object created from database result
        '''
        
        print "return movieinfo object"
        
        result = []
        for m in res:
            result.append(m)
        
        
        myMovieInfo = movieinfo()
        
        myMovieInfo.title = result[1]
        myMovieInfo.imdbid = result[2]
        myMovieInfo.genres = result[3]
        myMovieInfo.rating = result[4]
        myMovieInfo.runtime = result[5]
        myMovieInfo.tagline = result[6]
        myMovieInfo.totalVote = result[7]
        myMovieInfo.releaseDate = result[8]
        myMovieInfo. overview = result[9]
        myMovieInfo.posterImage = result[10]
        myMovieInfo.backdropImage = result[11]
        myMovieInfo.year = result[12]
        myMovieInfo.writer = result[13]
        myMovieInfo.director = result[14]
        myMovieInfo.castandrole = eval(result[15])
        myMovieInfo.trailer = result[16]
        
        
        return myMovieInfo
    
    def getMovieInfo(self, name, imdbid='', videoUrl=''):
        # check if the info is available in cache
        print "checking if imdbid is provided..."
        print "imdbid = " + imdbid
        if imdbid:
            print "got imdbid"
            t = (imdbid,)
            searchQuery = "SELECT * FROM movie_info WHERE imdbid = ?"
            self.dbcur.execute(searchQuery, t )
            result =self.dbcur.fetchone()
            
            if result:
                return self.getMovieInfoFromCache(result)
        
        print "no imdbid provided."
        print "check if videoUrl is provided"
        if videoUrl:
            print "got videoUrl: " + videoUrl
            t = (videoUrl, )
            searchQuery = "SELECT * FROM movie_info WHERE url = ?"
            self.dbcur.execute(searchQuery, t)
            result =self.dbcur.fetchone()
            print "check if match found"
            if result:
                print "match found with the name of movie : " + name
                return self.getMovieInfoFromCache(result)
        
        # create movieinfo object to return
        myMovieInfo = movieinfo()
        
        # set file name to movieinfo object
        myMovieInfo.name = name
        
        # delete first bracket ( from name
        name = name.replace("(", "")
        name = name.replace(")", "")
        name = name.replace("[", "")
        name = name.replace("]", "")
        name = name.replace(".", " ")
        name = name.replace("_", " ")
        name = name.replace("{", "")
        name = name.replace("}", "")
        
        mgroup = re.split('[0-9]{4}', name)
    
        if mgroup :
            searchName =  mgroup[0].strip()
        else:
            searchName = name
            
        m = re.search('[0-9]{4}', name)
        if m:
            searchYear = m.group(0)
        else:
            searchYear = ""
            
        # check if any movie info is avaiable in name, year pair
        # if year is available for better recognition
        if searchYear != "":
            print "searchYear: " + searchYear
            t = (searchName, searchYear)
            searchQuery = "SELECT * FROM movie_info WHERE title=? AND year=?"
            self.dbcur.execute(searchQuery, t)
            result =self.dbcur.fetchone()
            if result:
                return self.getMovieInfoFromCache(result)
            
            
        # invoke search
        movieId = self.searchMovie(searchName, searchYear)
        
        if movieId == 0 :
            return myMovieInfo
        
        DETAIL_URL = "http://api.themoviedb.org/3/movie/"+ str(movieId) +"?api_key="+self.API
        
        CREDIT_URL = "http://api.themoviedb.org/3/movie/"+ str(movieId) + "/credits?api_key="+ self.API
        
        TRAILER_URL = "http://api.themoviedb.org/3/movie/%s/videos?api_key=%s" %(str(movieId), self.API)
        
        
        
        result = urlopen(DETAIL_URL)
        mJson = json.load(result)
        
        creditResult = urlopen(CREDIT_URL)
        cJson = json.load(creditResult) 
        
        trailerResult = urlopen(TRAILER_URL)
        tJson = json.load(trailerResult)    
        
        # encode strings to "utf-8" becuase kodi give error while showing unicode character
        myMovieInfo.title =  mJson['title'].encode('utf-8')
        myMovieInfo.imdbid = mJson['imdb_id'].encode('utf-8')
        myMovieInfo.rating =  mJson['vote_average'] #rating
        myMovieInfo.totalVote = mJson['vote_count']
        myMovieInfo.overview =  mJson['overview'].encode('utf-8')
        myMovieInfo.runtime = mJson['runtime'] * 60
        myMovieInfo.tagline = mJson['tagline'].encode('utf-8') #short description
        myMovieInfo.releaseDate =  mJson['release_date'].encode('utf-8')
        tYear = mJson['release_date'].encode('utf-8')
        myMovieInfo.year = tYear[0:4]

        # get imdb rating 
        try:
            OMDB_URL = "http://www.omdbapi.com/?i=%s&plot=short&r=json" % myMovieInfo.imdbid
            omdbResult = urlopen(OMDB_URL)
            oJson = json.load(omdbResult) 
            
            if oJson['imdbVotes'] != 'N/A' and myMovieInfo.totalVote < oJson['imdbVotes']:
                myMovieInfo.rating =  oJson['imdbRating'] #rating
                myMovieInfo.totalVote = oJson['imdbVotes']
        except:
            pass
        gList = []
        for genre in mJson['genres'] :
            gList.append(genre['name'].encode('utf-8'))
            
        genres = ' / '.join(gList)
        
        myMovieInfo.genres =  genres
        
        try:
            myMovieInfo.posterImage = mJson['poster_path']
        except:
            pass
        try:
            myMovieInfo.backdropImage = mJson['backdrop_path']
        except: 
            pass
        
        try: 
            myMovieInfo.director = cJson['crew'][0]['name']
            myMovieInfo.writer = cJson['crew'][1]['name']
        except:
            pass
        
        try:
            myMovieInfo.trailer = str(tJson['results'][0]['key'])
        except:
            pass
        
        if cJson.has_key('cast'):
            listCast = cJson['cast']
            
            castName = []
            castChar = []
            for cast in listCast:
                name = cast['name']
                castName.append(name)
                character = cast['character']
                castChar.append(character)
            
            myMovieInfo.castandrole = zip(castName, castChar)
        
        self.saveMovieCache(myMovieInfo, videoUrl)
        
        return myMovieInfo
    
    def saveMovieCache(self, myMovieInfo, url):
        print "save movie info to database"
        t = (url ,myMovieInfo.title ,myMovieInfo.imdbid ,str(myMovieInfo.genres) ,myMovieInfo.rating ,myMovieInfo.runtime ,myMovieInfo.tagline ,myMovieInfo.totalVote ,myMovieInfo.releaseDate ,myMovieInfo.overview ,myMovieInfo.posterImage ,myMovieInfo.backdropImage ,myMovieInfo.year ,myMovieInfo.writer ,myMovieInfo.director , str(myMovieInfo.castandrole), str(myMovieInfo.trailer))
        insertQuery = '''INSERT INTO movie_info
                    (url ,title ,imdbid ,genres ,rating ,runtime ,tagline ,totalVote ,releaseDate ,overview ,posterImage ,backdropImage ,year ,writer ,director ,castandrole, trailer)
                VALUES
                    (? , ? , ? , ? , ? , ? , ? , ? , ? , ?, ? , ?, ?, ?, ? , ?, ?)
                    '''
        self.dbcon.text_factory = str
        self.dbcur.execute(insertQuery, t)
        
        self.dbcon.commit()
    
    def __del__(self):
        try:
            self.dbcon.close()
        except:
            pass
            
    