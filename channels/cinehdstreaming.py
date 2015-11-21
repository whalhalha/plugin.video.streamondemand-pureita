# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para cinehdstreaming
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "cinehdstreaming"
__category__ = "F"
__type__ = "generic"
__title__ = "cinehdstreaming (IT)"
__language__ = "IT"


DEBUG = config.get_setting("debug")

host = "https://cinehdstreaming.wordpress.com"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host],
    ['Connection', 'keep-alive']
]

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.cinehdstreaming mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR red]Ultimi Film Inseriti[/COLOR]", action="peliculas", url="https://cinehdstreaming.wordpress.com/", thumbnail="https://cinehdstreaming.files.wordpress.com/2015/11/cinema-news.jpg"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Categorie[/COLOR]", action="categorias", url="https://cinehdstreaming.wordpress.com/", thumbnail="https://cinehdstreaming.files.wordpress.com/2015/11/stream.jpg"))
    itemlist.append( Item(channel=__channel__, title="[COLOR green]Cerca[/COLOR]", action="search", thumbnail="https://cinehdstreaming.files.wordpress.com/2015/11/cerca-un-film.jpg"))
    
    return itemlist


def categorias(item):
    logger.info("streamondemand.cinehdstreaming categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url, headers=headers)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<ul class="sub-menu">(.*?)</ul>')
    
    # The categories are the options for the combo
    patron = '<li id=[^=]+="menu-item menu-item-type-taxonomy[^>]+><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

def search(item,texto):
    logger.info("[cinehdstreaming.py] "+item.url+" search "+texto)
    item.url = "https://www.cinehdstreaming.wordpress.com/?s="+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("streamondemand.cinehdstreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<h2 class="entry-title">\s*<a href="(.*?)"[^>]+>(.*?)</a>.*?<p><a href.*?<img.*?src="(.*?)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
	
	

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        response = urllib2.urlopen(scrapedurl)
        html = response.read()
        start = html.find("<h2 class=")
        end = html.find("</div>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<.*?>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        #scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", fulltitle=scrapedtitle, show=scrapedtitle, title=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<div class="nav-previous"><a href="(.*)" ><span class="meta-nav">&larr;'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti >>[/COLOR]" , url=scrapedurl , folder=True) )

    return itemlist  
