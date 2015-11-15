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

import sys 
import xbmcgui
import xbmcplugin
from resources.lib.cinehub import cinehub
from urlparse import parse_qsl
import xbmc
from resources.lib.movieinfo import movieinfo
import urllib
import xbmcaddon
import os
import xbmcvfs
from resources.lib.tmdbscraper import tmdbscraper
import sqlite3

addon_handle = int(sys.argv[1])
__url__ = sys.argv[0]

# get addon path
addonInfo = xbmcaddon.Addon().getAddonInfo
addonPath = xbmc.translatePath(addonInfo('path'))
# get to media path
artPath = os.path.join(addonPath, 'resources', 'media')

def showCatagoryList():
    listing = []
    
   
    
    #Recent movie list
    listItem = xbmcgui.ListItem(label="Recent movies")
    url = '{0}?action=recentMovies'.format(__url__)
    is_folder = True
    # set thumb image
    listItem.setArt({'thumb' : os.path.join(artPath, 'movies.jpg') })
    listing.append((url, listItem, is_folder))
    
    # Search list
    listItem = xbmcgui.ListItem(label="Search Movies")
    url = '{0}?action=search&query='.format(__url__)
    is_folder = True
    # set thumb image
    listItem.setArt({'thumb' : os.path.join(artPath, 'search.jpg') })
    listing.append((url, listItem, is_folder))

    #Update Library
    listItem = xbmcgui.ListItem(label="Update Library")
    url = '{0}?action=updateLibrary'.format(__url__)
    is_folder = True
    # set thumb image
    listItem.setArt({'thumb' : os.path.join(artPath, 'update.jpg') })
    listing.append((url, listItem, is_folder))
    
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    
    xbmcplugin.endOfDirectory(addon_handle)
    
def showSearchResult(listOfMovies):
    
    xbmcplugin.setContent(addon_handle, 'movies')
    listing = []
    print len(listOfMovies)
    for movie in listOfMovies:
        url = '{0}?action=play&video={1}'.format(__url__, movie.url)
        bPosterImage =  "https://image.tmdb.org/t/p/w396%s" % movie.posterImage
        bBackdropImage = "https://image.tmdb.org/t/p/w780%s" % movie.backdropImage
        sPosterImage = "https://image.tmdb.org/t/p/w185%s" % movie.posterImage
        
        trailer_url = ''
        if movie.trailer:
            trailer_url = 'plugin://plugin.video.youtube/play/?video_id=%s' % movie.trailer 
        
        li = xbmcgui.ListItem(label=movie.title, thumbnailImage=sPosterImage)
        
        li.setArt({ 'poster': bPosterImage, 'fanart' : bBackdropImage, 'thumb' : sPosterImage })
        
        info = {
            'genre': movie.genres,
            'year': movie.year,
            'title': movie.title,
            'mediatype' : 'movie',
            'code' : movie.imdbid,
            'plot' : movie.overview,
            'rating' : movie.rating,
            'tagline' : movie.tagline,
            'duration' : movie.runtime,
            'premiered' : movie.releaseDate,
            'votes' : movie.totalVote,
            'castandrole' : movie.castandrole,
            'director' : movie.director,
            'writer' : movie.writer
        }
        
        li.setInfo('video', info)
        
        # add video info if available 
        
        # from database myvideos93 table files get id_file
        # stream details idFile search and check if iVideoWidth has any value
        # database location: userdata/database
        hasResolutionData = 0
        
        dburl = urldb = os.path.join(xbmc.translatePath("special://userdata/Database/MyVideos93.db"))
        dbcon = sqlite3.connect(dburl)
        dbcur = dbcon.cursor()
        
        searchUrl = "plugin://plugin.video.cinehub/?action=play&video=%s" % movie.url
        dbcur.execute("SELECT * FROM files WHERE strFilename = ? " , (searchUrl,))
        result = dbcur.fetchone()
        if result:
            idFile = result[0]
            print "idFile is " + str(idFile)
            dbcur.execute("SELECT * FROM streamdetails WHERE idFile = ? " , (idFile,))
            fResult = dbcur.fetchone()
            if fResult:
                iStreamType = fResult[1]
                if iStreamType == 0:
                    hasResolutionData = 1
                    print "Found video resolution info for moovie : " + movie.title
                
        if hasResolutionData == 0:
            if movie.url.find('720p') != -1 :
                li.addStreamInfo('video', { 'width' : 1280 , 'height': 720 })
            if movie.url.find('1080p') != -1:
                li.addStreamInfo('video', { 'width' : 1920 , 'height': 1080 })
        
        li.setProperty('IsPlayable', 'true')
        
        # add contex menu
        cm =[]
        cm.append(('Movie Informatiom', 'Action(Info)'))
        msg = 'RunPlugin({0}?action=addToLibrary&imdbid={1}&title={2}&year={3}&url={4})'.format(__url__, movie.imdbid, urllib.quote_plus(movie.title), movie.year, movie.url)
        cm.append(('Add To Library', msg))
        li.addContextMenuItems(cm, False)
        
        listing.append((url, li , False ))
    
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    

def showMoviesList(page=1):
    xbmcplugin.setContent(addon_handle, 'movies')
    
    myHub = cinehub()
    listOfMovies = myHub.getRecentMovieList(page)
    
    listing = []
    
    for movie in listOfMovies:
    
        url = '{0}?action=play&video={1}'.format(__url__, movie.url)
        
        
        bPosterImage =  "https://image.tmdb.org/t/p/w396%s" % movie.posterImage
        bBackdropImage = "https://image.tmdb.org/t/p/w780%s" % movie.backdropImage
        sPosterImage = "https://image.tmdb.org/t/p/w185%s" % movie.posterImage
        
        trailer_url = ''
        if movie.trailer:
            trailer_url = 'plugin://plugin.video.youtube/play/?video_id=%s' % movie.trailer 
        
        li = xbmcgui.ListItem(label=movie.title, thumbnailImage=sPosterImage)
        
        li.setArt({ 'poster': bPosterImage, 'fanart' : bBackdropImage, 'thumb' : sPosterImage })
        
        info = {
            'genre': movie.genres,
            'year': movie.year,
            'title': movie.title,
            'mediatype' : 'movie',
            'code' : movie.imdbid,
            'plot' : movie.overview,
            'rating' : movie.rating,
            'tagline' : movie.tagline,
            'duration' : movie.runtime,
            'premiered' : movie.releaseDate,
            'votes' : movie.totalVote,
            'castandrole' : movie.castandrole,
            'director' : movie.director,
            'writer' : movie.writer,
            'trailer' : trailer_url
        }
        
        li.setInfo('video', info)
        
        # add video info if available 
        
        # from database myvideos93 table files get id_file
        # stream details idFile search and check if iVideoWidth has any value
        # database location: userdata/database
        hasResolutionData = 0
        
        dburl = urldb = os.path.join(xbmc.translatePath("special://userdata/Database/MyVideos93.db"))
        dbcon = sqlite3.connect(dburl)
        dbcur = dbcon.cursor()
        
        searchUrl = "plugin://plugin.video.cinehub/?action=play&video=%s" % movie.url
        dbcur.execute("SELECT * FROM files WHERE strFilename = ? " , (searchUrl,))
        result = dbcur.fetchone()
        if result:
            idFile = result[0]
            print "idFile is " + str(idFile)
            dbcur.execute("SELECT * FROM streamdetails WHERE idFile = ? " , (idFile,))
            fResult = dbcur.fetchone()
            if fResult:
                iStreamType = fResult[1]
                if iStreamType == 0:
                    hasResolutionData = 1
                    print "Found video resolution info for moovie : " + movie.title
                
        if hasResolutionData == 0:
            if movie.url.find('720p') != -1 :
                li.addStreamInfo('video', { 'width' : 1280 , 'height': 720 })
            if movie.url.find('1080p') != -1:
                li.addStreamInfo('video', { 'width' : 1920 , 'height': 1080 })
        
        li.setProperty('IsPlayable', 'true')
        
        
        # add contex menu
        cm =[]
        cm.append(('Movie Informatiom', 'Action(Info)'))
        msg = 'RunPlugin({0}?action=addToLibrary&imdbid={1}&title={2}&year={3}&url={4})'.format(__url__, movie.imdbid, urllib.quote_plus(movie.title), movie.year, movie.url)
        cm.append(('Add To Library', msg))
        li.addContextMenuItems(cm, False)
        
        listing.append((url, li , False ))
    
    
    # Next page link action
    # added as a listitem
    new_page = int(page) + 1
    newStrPage = str(new_page)
    url = '{0}?action=recentMoviesWithPage&page={1}'.format(__url__, newStrPage)
    li = xbmcgui.ListItem(label="Next Page")
    li.setArt({'thumb' : os.path.join(artPath, 'next.jpg') })
    listing.append((url, li, True))
    
    
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    
def router(paramstring):

    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements

    params = dict(parse_qsl(paramstring[1:]))

    print "My sense are tickling.. Getting actions... Action received. Action = " + str(params)

    try:
        searchQuery = params['query']
    except:
        searchQuery = ''
    if searchQuery:
        print "WOOOOOOOOOOOOOOOOOOOOOOOOO. GOD SEARCH QUERY ====== %s" % searchQuery

    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'recentMovies':
            showMoviesList()
            
        elif params['action'] == 'search':
            try:
                k = xbmc.Keyboard('', 'Search Movies', False)
                k.doModal()
                query = k.getText() if k.isConfirmed() else None
                query = query.strip()
                if query == None or query == '':
                    return
                
                mHub = cinehub()
                mInfo = mHub.getSearchedMovieList(query)
                showSearchResult(mInfo)
            except:
                pass
                
        elif params['action'] == 'play':
            play_video(params['video'])
            
        elif params['action'] == 'playStream':
            print "all params : " + params['title']
            
            if params.has_key('imdbid'):
                play_stream(params['title'], params['year'], params['video'], params['imdbid'])
            else:
                play_stream(params['title'], params['year'], params['video'])
            
        elif params['action']=='recentMoviesWithPage':
            showMoviesList(params['page'])
            
        elif params['action'] == 'addToLibrary':
            print "plugin.video.cinehub: " + params['title']
            addMovieToLibrary(params['title'], params['year'], params['url'], params['imdbid'])

        elif params['action'] =='updateLibrary':
            if not xbmc.getCondVisibility('Library.IsScanningVideo'):
                xbmc.executebuiltin('UpdateLibrary(video)')

            
    else:

        showCatagoryList()
        
def addMovieToLibrary(title, year , url, imdbid):
    
    # get movie folder location
    # 
    # os.path.join is for translating between different OS path structure
    # xbmc.translatePath() is used for translating "speciall://sample" path to full path for writing to disk
    # xbmcaddon.Addon().getSetting('id') is for reading movie libray info from setting
    library_folder = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getSetting('movie_library')))
    
    # make movie directory if not already created
    xbmcvfs.mkdir(library_folder)
    
    movie_folder_name = title +" (" + year + ")"
    
    # make movie folder
    folder = os.path.join(library_folder, movie_folder_name )
    xbmcvfs.mkdir(folder)
    
    # movie file name
    movie_file_name = movie_folder_name + ".strm"
    
    # get the path to the file
    movie_file = os.path.join(folder, movie_file_name)
    
    file = xbmcvfs.File(movie_file, 'w')
    
    content = '%s?action=playStream&imdbid=%s&title=%s&year=%s&video=%s' % (__url__, imdbid, urllib.quote_plus(title), year, url)
    
    file.write(str(content))
    
    file.close()
    
    dialog = xbmcgui.Dialog()
    dialog.notification('Movie Added to library', title + " was added to library", xbmcgui.NOTIFICATION_INFO, 5000)

    #if not xbmc.getCondVisibility('Library.IsScanningVideo'):
    #    xbmc.executebuiltin('UpdateLibrary(video)')
    
  
def play_video(path):

    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    
def play_stream(title, year, path, imdbid=''):
    
    # get movie info
    mInfo = movieinfo()
    
    # generate name
    name = '%s (%s)' % (title, str(year))
    
    scrobber = tmdbscraper()
    
    print "imdbid from play_stream " + imdbid
    
    if imdbid:
        movie = scrobber.getMovieInfo(name, imdbid=imdbid)
    else:
        movie = scrobber.getMovieInfo(name)
    
    info = {
            'genre': movie.genres,
            'year': movie.year,
            'title': movie.title,
            'mediatype' : 'movie',
            'code' : movie.imdbid,
            'plot' : movie.overview,
            'rating' : movie.rating,
            'tagline' : movie.tagline,
            'duration' : movie.runtime,
            'premiered' : movie.releaseDate,
            'votes' : movie.totalVote,
            'castandrole' : movie.castandrole,
            'director' : movie.director,
            'writer' : movie.writer
        }
    
    sPosterImage = "https://image.tmdb.org/t/p/w185" + movie.posterImage
    
    print "sPosterImage url while playing: " + sPosterImage
    
    play_item = xbmcgui.ListItem(label=movie.title, thumbnailImage=sPosterImage, path=path)
    
    play_item.setInfo('video', info)
    
    
    play_item.setArt({'thumb' : sPosterImage })
    
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    
if __name__ == '__main__':
    router(sys.argv[2])
