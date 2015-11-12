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

addon_handle = int(sys.argv[1])
__url__ = sys.argv[0]

def showCatagoryList():
    listing = []
    
    #Recent movie list
    listItem = xbmcgui.ListItem(label="Recent movies")
    url = '{0}?action=recentMovies'.format(__url__)
    is_folder = True
    listing.append((url, listItem, is_folder))
    
    # Search list
    listItem = xbmcgui.ListItem(label="Search Movies")
    url = '{0}?action=search&query='.format(__url__)
    is_folder = True
    listing.append((url, listItem, is_folder))
    
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    
    xbmcplugin.endOfDirectory(addon_handle)
    
def showSearchResult(listOfMovies):
    
    xbmcplugin.setContent(addon_handle, 'movies')
    listing = []
    print len(listOfMovies)
    for movie in listOfMovies:
        url = '{0}?action=play&video={1}'.format(__url__, movie.url)
        li = xbmcgui.ListItem(label=movie.title, thumbnailImage=movie.posterImage)
        li.setArt({ 'poster': movie.posterImage, 'fanart' : movie.backdropImage, 'thumb' : movie.posterImage })
        
        info = {
            'genre': movie.genres,
            'year': movie.year,
            'title': movie.title,
            'mediatype' : 'movie',
            'code' : movie.imdbid,
            'plot' : movie.overview,
            'rating' : movie.totalVote,
            'tagline' : movie.tagline,
            'duration' : movie.runtime,
            'premiered' : movie.releaseDate,
            'votes' : movie.rating,
            'castandrole' : movie.castandrole,
            'director' : movie.director,
            'writer' : movie.writer
        }
        
        li.setInfo('video', info)
        
        li.setProperty('IsPlayable', 'true')
        
        # Add to library context menu
        cm = [] 
        msg = 'RunPlugin({0}?action=addToLibrary&title={1}&year={2}&url={3})'.format(__url__,  urllib.quote_plus(movie.title), movie.year, movie.url)
        print "plugin.video.cinehub: " + msg
        cm.append(('Add To Library', msg))
        li.addContextMenuItems(cm, False)
        
        listing.append((url, li , False ))
    
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    

def showMoviesList(page=1):
    xbmcplugin.setContent(addon_handle, 'movies')
    
    myHub = cinehub()
    listOfMovies = myHub.getMyMovieInfoList(page)
    
    listing = []
    
    for movie in listOfMovies:
    
        url = '{0}?action=play&video={1}'.format(__url__, movie.url)
        
        li = xbmcgui.ListItem(label=movie.title, thumbnailImage=movie.posterImage)
        
        
        li.setArt({ 'poster': movie.posterImage, 'fanart' : movie.backdropImage, 'thumb' : movie.posterImage })
        
        info = {
            'genre': movie.genres,
            'year': movie.year,
            'title': movie.title,
            'mediatype' : 'movie',
            'code' : movie.imdbid,
            'plot' : movie.overview,
            'rating' : movie.totalVote,
            'tagline' : movie.tagline,
            'duration' : movie.runtime,
            'premiered' : movie.releaseDate,
            'votes' : movie.rating,
            'castandrole' : movie.castandrole,
            'director' : movie.director,
            'writer' : movie.writer
        }
        
        li.setInfo('video', info)
        
        li.setProperty('IsPlayable', 'true')
        
        
        # add contex menu
        cm =[]
        msg = 'RunPlugin({0}?action=addToLibrary&title={1}&year={2}&url={3})'.format(__url__,  urllib.quote_plus(movie.title), movie.year, movie.url)
        print "plugin.video.cinehub: " + msg
        cm.append(('Add To Library', msg))
        li.addContextMenuItems(cm, False)
        
        listing.append((url, li , False ))
    
    
    # Next page link action
    # added as a listitem
    new_page = int(page) + 1
    newStrPage = str(new_page)
    url = '{0}?action=recentMoviesWithPage&page={1}'.format(__url__, newStrPage)
    li = xbmcgui.ListItem(label="Next Page")
    listing.append((url, li, True))
    
    
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    
def router(paramstring):

    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring[1:]))

    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'recentMovies':
            showMoviesList()
            
        elif params['action'] == 'search':
            print 'another action'
            try:
                k = xbmc.Keyboard('', 'Search Movies', False)
                k.doModal()
                query = k.getText() if k.isConfirmed() else None
                query = query.strip()
                if query == None or query == '':
                    return
                
                mHub = cinehub()
                mInfo = mHub.searchMovies(query)
                print "accepted movie count"
                print len(mInfo)
                showSearchResult(mInfo)
            except:
                return
                
        elif params['action'] == 'play':
            play_video(params['video'])
            
        elif params['action'] == 'playStream':
            print "all params : " + params['title']
            play_stream(params['title'], params['year'], params['video'])
            
        elif params['action']=='recentMoviesWithPage':
            showMoviesList(params['page'])
            
        elif params['action'] == 'addToLibrary':
            print "plugin.video.cinehub: " + params['title']
            addMovieToLibrary(params['title'], params['year'], params['url'])
            
    else:

        showCatagoryList()
        
def addMovieToLibrary(title, year , url):
    
    # get movie folder location
    # 
    # os.path.join is for translating between different OS path structure
    # xbmc.translatePath() is used for translating "speciall://sample" path to full path for writing to disk
    # xbmcaddon.Addon().getSetting('id') is for reading movie libray info from setting
    library_folder = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getSetting('movie_library')))
    print "Movie library path: " + library_folder
    
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
    
    content = '%s?action=playStream&title=%s&year=%s&video=%s' % (__url__, urllib.quote_plus(title), year, url)
    
    file.write(str(content))
    
    file.close()
    
    dialog = xbmcgui.Dialog()
    dialog.notification('Movie Added to library', title + " was added to library", xbmcgui.NOTIFICATION_INFO, 5000)
    
  
def play_video(path):

    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    
def play_stream(title, year, path):
    
    # get movie info
    mInfo = movieinfo()
    
    print "name received via stream : " + title
    mInfo.name = title
    mInfo.year = year
    
    scrobber = tmdbscraper()
    movie = scrobber.getMovieInfo(mInfo)
    
    info = {
            'genre': movie.genres,
            'year': movie.year,
            'title': movie.title,
            'mediatype' : 'movie',
            'code' : movie.imdbid,
            'plot' : movie.overview,
            'rating' : movie.totalVote,
            'tagline' : movie.tagline,
            'duration' : movie.runtime,
            'premiered' : movie.releaseDate,
            'votes' : movie.rating,
            'castandrole' : movie.castandrole,
            'director' : movie.director,
            'writer' : movie.writer
        }
    play_item = xbmcgui.ListItem(label=movie.title, thumbnailImage=movie.posterImage, path=path)
    
    play_item.setInfo('video', info)
    
    
    play_item.setArt({ 'poster': movie.posterImage, 'fanart' : movie.backdropImage, 'thumb' : movie.posterImage })
    
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    
if __name__ == '__main__':
    router(sys.argv[2])
