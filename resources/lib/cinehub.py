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
from BeautifulSoup import BeautifulSoup
import requests
from movieinfo import movieinfo
from tmdbscraper import tmdbscraper
import xbmcaddon
import urllib
import base64

class cinehub:
    
    # Perform login task and return request.session() object
    def login(self):
        
        # Login url 
        loginUrl = "http://www.cinehub24.com/auth/login"
        
        myAddon = xbmcaddon.Addon()
        
        
        USERNAME = myAddon.getSetting("user_name")
        PASSWORD = myAddon.getSetting("user_password")
        

        
        if USERNAME == "" or PASSWORD == "" :
            myAddon.openSettings()
        
        session_requests = requests.session()
    
        # Create payload
        payload = {
            "user_name": USERNAME, 
            "user_password": PASSWORD,
            'doLogin' : 'true',
            'submit' : 'Login' 
        }
    
        # Perform login
        result = session_requests.post(loginUrl, data = payload, headers = dict(referer = loginUrl))
        
        # check if login successfull
        # TODO
        
        return session_requests
    
    def getAllMovieList(self, session, page=1):
        URL = "http://www.cinehub24.com/net/section/english-movie/onlineContent.aspx/" + str(page)
        return self.getMovieList(session, URL, page)
    
    
    def getMovieList(self, session, URL, page = 1 ): 
        # url for all movie list
        #URL = "http://www.cinehub24.com/net/section/english-movie/onlineContent.aspx/" + str(page)
        
        # get the html 
        result = session.get(URL).content
        
        # make it ready for scraping
        soup = BeautifulSoup(result)
        
        # get movie list box
        movieBoxs = soup.findAll('div', attrs={'class': ['movie-list-hldr' , 'movie-list-hldr movielist-active']})
        
        
        
        movielist = []
        
        for movieBox in movieBoxs:
            # movie link 
            movieLink = movieBox.find('div', attrs={'class' : 'movie-list-des'}).find('a')
            #print movieLink['href']
            
            # get real movie links
            links = movieLink['href']
            
            minfo = movieinfo()
           
            minfo.url = self.getVideoLink(session, links)
            
            #self.getVideoLink(session, links)
            
            if minfo.url :   
                
                #movie title
                movieTitle = movieLink.find('b')
                #print movieTitle.string
                minfo.name = movieTitle.string
                
                movielist.append(minfo)
                
    
        return movielist
    
    def getVideoLink(self, session, URL):
        
        # get html file
        result = session.get(URL).content
        
        # create soup for scrapping
        soup = BeautifulSoup(result)
        
        linkTable = soup.find('table', attrs={'id': 'travel'})
        
        tdId = 1
        for i in range(1,5):
            try:
                tempName =  linkTable.find('tbody').findAll('td')[tdId].find('b').string
                #print tempName
                
                # video file format mp4, avi and mkv and not containing sample
                if tempName.find('.mp4') != -1 or tempName.find('.avi') != -1 or tempName.find('.mkv') != -1 :
                    if tempName.lower().find("sample") != -1 or tempName.lower().find("trailer") != -1 :
                        pass
                    else:
                        tempVideoLink = linkTable.find('tbody').findAll('td')[tdId+3].find('a')['href']
                        result = session.get(tempVideoLink).content    
                        soup = BeautifulSoup(result)
                        link =  soup.find('div', attrs={'id': 'download_btn_r'}).find('a')['href']
                        return link.strip()
                else:
                    tdId += 5
            except:
                break
            
        
    def getMyMovieInfoList(self, page = 1):  
        session = self.login()
        mymovieinfos = self.getAllMovieList(session, page) 
        
        movieList = []
        
        print "getting mymovieinfo..."
        for mymovieinfo in mymovieinfos:
            tScrap = tmdbscraper()
            mymovieinfo = tScrap.getMovieInfo(mymovieinfo)
            
            if mymovieinfo.imdbid:
                movieList.append(mymovieinfo)
                print mymovieinfo.title
        
        return movieList
    
    def searchMovies(self, searchTerm):
        searchTerm = searchTerm.strip()
        searchTerm = searchTerm.replace(" ", "+")
        URL = "http://www.cinehub24.com/search/{0}.aspx".format(searchTerm)
        
        session = self.login()
        mymovieinfos = self.getMovieList(session, URL, 1)
        
        movieList = []
        for mymovieinfo in mymovieinfos:
            tScrap = tmdbscraper()
            mymovieinfo = tScrap.getMovieInfo(mymovieinfo)
            try:
                if mymovieinfo.imdbid:
                    movieList.append(mymovieinfo)
                    print mymovieinfo.title
            except:
                pass
        return movieList
       
        
