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

from movieinfo import movieinfo
from urllib import urlopen
from BeautifulSoup import BeautifulSoup
import requests
import urllib
from tmdbscraper import tmdbscraper
import threading
import xbmcaddon
import os
import xbmc
import sqlite3
import sys

class cinehub:
    
    # movie list
    movieList = []
    
    # path to database
    dburl = urldb = os.path.join(xbmc.translatePath("special://userdata/addon_data/plugin.video.cinehub/cinehubdb.db"))
    
    def __init__(self):

        dbcon = sqlite3.connect(self.dburl)
        
        # for dic output
        # dbcon.row_factory = sqlite3.Row
        
        # get cursor
        dbcur = dbcon.cursor()
        
        # create database if not already created
        try:
            #create link_url table
            dbcur.execute("CREATE TABLE url_matcher (link_url text , video_url text)")
            
            #create movie_info table
            dbcur.execute('''CREATE TABLE movie_info
                (
                    url text,  
                    title text, 
                    imdbid text, 
                    genres text,
                    rating real,
                    runtime integer,
                    tagline text,
                    totalVote integer,
                    releaseDate text,
                    overview text,
                    posterImage text,
                    backdropImage text,
                    year integer,
                    writer text,
                    director text,
                    castandrole text,
                    trailer text
                )''')
            
            # commit change
            dbcon.commit()
        except:
            pass
        
        #close the database connection
        dbcon.close()
     
    # function to call the getMovieList with appropiate URL and page number
    def getSearchedMovieList(self, movieName):
        # create url
        url = "http://www.cinehub24.com/search/%s.aspx" % urllib.quote_plus(movieName)
        
        return self.getMovieList(url)

    
    # function to call the getMovieList with appropiate URL and page number
    def getRecentMovieList(self, page):
        # create url
        url = "http://www.cinehub24.com/net/section/english-movie/onlineContent.aspx/%s" % str(page)

        return self.getMovieList(url)
        
    def getMovieList(self, url):
        # get session for authorize url call
        session = self.doLogin()
        
        # get the html 
        result = session.get(url).content
        
        # make it ready for scraping
        soup = BeautifulSoup(result)
        
        # get movie list box
        movieBoxs = soup.findAll('div', attrs={'class': ['movie-list-hldr' , 'movie-list-hldr movielist-active']})
        
        # list of threads
        threads = []
        
        # send a number with the thread for sorting 
        i = 1
        for movieBox in movieBoxs:
            # movie link 
            movieLink = movieBox.find('div', attrs={'class' : 'movie-list-des'}).find('a')
            
            # get real movie links
            links = movieLink['href']
            # get movie title
            movieTitle = movieLink.find('b').string
            
            # start thread job
            t = threading.Thread(target=self.worker, args=(movieTitle, links, session, i))
            
            # append to threads so that can be stopped later
            threads.append(t)
            
            # start thread
            t.start()
            
            # increment the value of i for next number
            i = i + 1
        
        # stop thread job
        for t in threads:
            t.join() 
                
        
        return sorted(self.movieList, key=lambda movieinfo: movieinfo.sortid)
    
    def worker(self, name, url, session, sortid):
        # get cursor
        dbcon = sqlite3.connect(self.dburl)
        dbcur = dbcon.cursor()
        
        resolvedUrl = self.matchUrl(session, url, dbcon, dbcur)
        
        # close the connection
        dbcon.close()
        
        # if resolvedUrl is none then stop the thread and do nothing
        if resolvedUrl == None or resolvedUrl == "":
            return
        
        # save movie info into database
        
        # now try to get meta info from tmdb database
        scrapper = tmdbscraper()
        mMovieInfo = scrapper.getMovieInfo(name, videoUrl=resolvedUrl)
        
        # add previously resolved url to the list
        mMovieInfo.url = resolvedUrl
        
        # add sortid to movie to sort the movie after exiting the thread
        mMovieInfo.sortid = sortid
        
        # if movie info have no imdb id then return
        if mMovieInfo.imdbid:
            # add the movieino object to the movie list
            self.movieList.append(mMovieInfo)
    
    def matchUrl(self, session, url, dbcon, dbcur):        
        # check if the url is already being parsed
        t = (url,)
        dbcur.execute("SELECT * FROM url_matcher WHERE link_url = ? " , t)
        
        result = dbcur.fetchone() 
        
        
        # if we found it
        if result :
            # close the connection
            dbcon.close()
            # return the parsed video url
            print "found in databse: " + url
            return result[1]
        
        # if not found in database fetch the link 
        print "Not found in databae. starting query for url"
        return self.getVideoLink(session, url, dbcur, dbcon)
    # get playable video link for the movie if available
    # if no link is available then return nothing
    def getVideoLink(self, session, URL, dbcur, dbcon):
        
        # get html file
        result = session.get(URL).content
        
        # create soup for scrapping
        soup = BeautifulSoup(result)
        
        linkTable = soup.find('table', attrs={'id': 'travel'})
        
        tdId = 1
        for i in range(1,5):
            try:
                tempName =  linkTable.find('tbody').findAll('td')[tdId].find('b').string
                
                # get downloadable link
                tempVideoLink = linkTable.find('tbody').findAll('td')[tdId+3].find('a')['href']
                result = session.get(tempVideoLink).content    
                soup = BeautifulSoup(result)
                link =  soup.find('div', attrs={'id': 'download_btn_r'}).find('a')['href'].strip()
                
                # video file format mp4, avi and mkv and not containing sample
                if link.lower().endswith(('mp4' , 'avi' , 'mkv')) :
                    if link.lower().find("sample") != -1 or link.lower().find("trailer") != -1 :
                        tdId += 5
                    else:
                        print "inserting into database"
                        t = (URL, link)
                        dbcur.execute("INSERT INTO url_matcher VALUES (?, ?)", t)
                        dbcon.commit()
                        dbcon.close()
                        print "insert successful"
                        print "Link is : " + link
                        return link
                else:
                    tdId += 5
            except sqlite3.OperationalError:
                raise        
            
            except:
                break
        # if no link found insert empty link to database
        t = (URL, '')
        dbcur.execute("INSERT INTO url_matcher VALUES (?, ?)", t)
        dbcon.commit()
        dbcon.close()
    
    # Login to the cinehub24 server
    def doLogin(self):
        # Login url 
        loginUrl = "http://www.cinehub24.com/auth/login"
        
        myAddon = xbmcaddon.Addon()
        
        USERNAME = myAddon.getSetting("user_name")
        PASSWORD = myAddon.getSetting("user_password")
        
        # if no usename or password then show setting window
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
    
            
    
        