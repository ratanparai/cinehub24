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


class tmdbscraper:
    
    API = base64.urlsafe_b64decode("N2U5MTYyMjM1NWFjZjI3NDM3ODQzNjcyMzRlOTFhODU=")
    
    def searchMovie(self, name, year=""):
        URL = "http://api.themoviedb.org/3/search/movie?api_key="+self.API+"&query=" + urllib.quote_plus(name) + "&year=" + str(year)
        result = urlopen(URL)
        moviejson = json.load(result)
        
        if moviejson['total_results'] == 0 :
            return 0
        
        return moviejson['results'][0]['id']
    
    def getMovieInfo(self, name):
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
            
        # invoke search
        movieId = self.searchMovie(searchName, searchYear)
        
        if movieId == 0 :
            return myMovieInfo
        
        DETAIL_URL = "http://api.themoviedb.org/3/movie/"+ str(movieId) +"?api_key="+self.API
        
        CREDIT_URL = "http://api.themoviedb.org/3/movie/"+ str(movieId) + "/credits?api_key="+ self.API
        
        result = urlopen(DETAIL_URL)
        mJson = json.load(result)
        
        creditResult = urlopen(CREDIT_URL)
        cJson = json.load(creditResult)     
        
        # encode strings to "utf-8" becuase kodi give error while showing unicode character
        myMovieInfo.title =  mJson['title'].encode('utf-8')
        myMovieInfo.imdbid = mJson['imdb_id'].encode('utf-8')
        myMovieInfo.totalVote =  mJson['vote_average'] #rating
        myMovieInfo.rating = mJson['vote_count']
        myMovieInfo.overview =  mJson['overview'].encode('utf-8')
        myMovieInfo.runtime = mJson['runtime'] * 60
        myMovieInfo.tagline = mJson['tagline'].encode('utf-8') #short description
        myMovieInfo.releaseDate =  mJson['release_date'].encode('utf-8')
        tYear = mJson['release_date'].encode('utf-8')
        myMovieInfo.year = tYear[0:4]

        gList = []
        for genre in mJson['genres'] :
            gList.append(genre['name'].encode('utf-8'))
            
        genres = ' / '.join(gList)
        
        myMovieInfo.genres =  genres
        
        try:
            myMovieInfo.posterImage = "https://image.tmdb.org/t/p/w396" + mJson['poster_path']
        except:
            pass
        try:
            myMovieInfo.backdropImage = "https://image.tmdb.org/t/p/w780" + mJson['backdrop_path']
        except: 
            pass
        
        try: 
            myMovieInfo.director = cJson['crew'][0]['name']
            myMovieInfo.writer = cJson['crew'][1]['name']
        except:
            pass
        
        listCast = cJson['cast']
        
        castName = []
        castChar = []
        for cast in listCast:
            name = cast['name']
            castName.append(name)
            character = cast['character']
            castChar.append(character)
        
        myMovieInfo.castandrole = zip(castName, castChar)
        
        return myMovieInfo
            
    