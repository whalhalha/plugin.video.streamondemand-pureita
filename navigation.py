# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand-pureita
# Copyright 2015 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
#------------------------------------------------------------
# This file is part of streamondemand-pureita.
#
# streamondemand-pureita is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand-pureita is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand-pureita.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------

import os
import sys
import urlparse,urllib,urllib2

import xbmc
import xbmcgui
import xbmcaddon

import channelselector
import plugintools
from core.item import Item

			
def get_next_items( item ):

    plugintools.log("navigation.get_next_items item="+item.tostring())

    try:
        # ----------------------------------------------------------------
        #  Main menu
        # ----------------------------------------------------------------
        if item.channel=="navigation":
		            # --- Update channels list ---------------------------------------
            from core import config
            if item.action=="mainlist":
                plugintools.log("navigation.get_next_items Main menu")

                if config.get_setting("updatechannels")=="true":
                    try:
                        from core import updater
                        actualizado = updater.updatechannel("channelselector")

                        if actualizado:
                            import xbmcgui
                            advertencia = xbmcgui.Dialog()
                            advertencia.ok("tvalacarta",config.get_localized_string(30064))
                    except:
                        pass
            # ----------------------------------------------------------------

            if item.action=="mainlist":
                plugintools.log("navigation.get_next_items Main menu")
                itemlist = channelselector.getmainlist("bannermenu")

        elif item.channel=="channelselector":

            if item.action=="channeltypes":
                plugintools.log("navigation.get_next_items Channel types menu")
                itemlist = channelselector.getchanneltypes("bannermenu")

            elif item.action=="listchannels":
                plugintools.log("navigation.get_next_items Channel list menu")
                itemlist = channelselector.filterchannels(item.category,"bannermenu")

        elif item.channel=="configuracion":
            plugintools.open_settings_dialog()
            return []

        else:

            if item.action=="":
                item.action="mainlist"

            plugintools.log("navigation.get_next_items Channel code ("+item.channel+"."+item.action+")")

            # --- Update channels files --------------------------------------
            if item.action=="mainlist":
                from core import config
                if config.get_setting("updatechannels")=="true":
                    try:
                        from core import updater
                        actualizado = updater.updatechannel(item.channel)

                        if actualizado:
                            import xbmcgui
                            advertencia = xbmcgui.Dialog()
                            advertencia.ok("plugin",item.channel,config.get_localized_string(30063))
                    except:
                        pass
            # ----------------------------------------------------------------

            try:
                exec "import channels."+item.channel+" as channel"
            except:
                exec "import core."+item.channel+" as channel"

            from platformcode import xbmctools

            if item.action=="play":
                plugintools.log("navigation.get_next_items play")

                # Si el canal tiene una acción "play" tiene prioridad
                if hasattr(channel, 'play'):
                    plugintools.log("streamondemand-pureita.platformcode.launcher Channel has its own 'play' method")
                    itemlist = channel.play(item)
                    if len(itemlist)>0:
                        item = itemlist[0]

                        # FIXME: Este error ha que tratarlo de otra manera, al dar a volver sin ver el vídeo falla
                        try:
                            xbmctools.play_video(channel=item.channel, server=item.server, url=item.url, category=item.category, title=item.title, thumbnail=item.thumbnail, plot=item.plot, extra=item.extra, subtitle=item.subtitle, video_password = item.password, fulltitle=item.fulltitle, Serie=item.show)
                        except:
                            pass

                    else:
                        import xbmcgui
                        ventana_error = xbmcgui.Dialog()
                        ok = ventana_error.ok ("plugin", "No hay nada para reproducir")
                else:
                    plugintools.log("streamondemand-pureita.platformcode.launcher No channel 'play' method, executing core method")

                    # FIXME: Este error ha que tratarlo de otra manera, por al dar a volver sin ver el vídeo falla
                    # Mejor hacer el play desde la ventana
                    try:
                        xbmctools.play_video(channel=item.channel, server=item.server, url=item.url, category=item.category, title=item.title, thumbnail=item.thumbnail, plot=item.plot, extra=item.extra, subtitle=item.subtitle, video_password = item.password, fulltitle=item.fulltitle, Serie=item.show)
                    except:
                        pass


                return []

            elif item.action=="findvideos":
                plugintools.log("navigation.get_next_items findvideos")

                # Si el canal tiene una acción "findvideos" tiene prioridad
                if hasattr(channel, 'findvideos'):
                    plugintools.log("streamondemand-pureita.platformcode.launcher Channel has its own 'findvideos' method")
                    itemlist = channel.findvideos(item)
                else:
                    itemlist = []

                if len(itemlist)==0:
                    from servers import servertools
                    itemlist = servertools.find_video_items(item)

                if len(itemlist)==0:
                    itemlist = [ Item(title="No se han encontrado vídeos", thumbnail=os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_error.png" )) ]
            # ---------------add_serie_to_library-----------
            elif item.action=="add_serie_to_library":
                plugintools.log("navigation.get_next_items add_serie_to_library")
                from platformcode import library
                import xbmcgui
                
                # Obtiene el listado desde el que se llamó
                action = item.extra
                    
                # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
                if "###" in item.extra:
                    action = item.extra.split("###")[0]
                    item.extra = item.extra.split("###")[1]

                exec "itemlist = channel."+action+"(item)"

                # Progreso
                pDialog = xbmcgui.DialogProgress()
                ret = pDialog.create('streamondemand-pureita', 'Añadiendo episodios...')
                pDialog.update(0, 'Añadiendo episodio...')
                totalepisodes = len(itemlist)
                plugintools.log ("[launcher.py] Total Episodios:"+str(totalepisodes))
                i = 0
                errores = 0
                nuevos = 0
                for item in itemlist:
                    i = i + 1
                    pDialog.update(i*100/totalepisodes, 'Añadiendo episodio...',item.title)
                    plugintools.log("streamondemand-pureita.platformcode.launcher add_serie_to_library, title="+item.title)
                    if (pDialog.iscanceled()):
                        return
                
                    try:
                        #(titulo="",url="",thumbnail="",server="",plot="",canal="",category="Cine",Serie="",verbose=True,accion="strm",pedirnombre=True):
                        # Añade todos menos el que dice "Añadir esta serie..." o "Descargar esta serie..."
                        if item.action!="add_serie_to_library" and item.action!="download_all_episodes":
                            nuevos = nuevos + library.savelibrary( titulo=item.title , url=item.url , thumbnail=item.thumbnail , server=item.server , plot=item.plot , canal=item.channel , category="Series" , Serie=item.show.strip() , verbose=False, accion="play_from_library", pedirnombre=False, subtitle=item.subtitle, extra=item.extra )
                    except IOError:
                        import sys
                        for line in sys.exc_info():
                            logger.error( "%s" % line )
                        plugintools.log("streamondemand-pureita.platformcode.launcher Error al grabar el archivo "+item.title)
                        errores = errores + 1
                        
                pDialog.close()
                    
                # Actualizacion de la biblioteca
                itemlist=[]
                if errores > 0:
                    itemlist.append(Item(title="ERRORE, la serie NON si è aggiunta alla biblioteca o la fatto in modo incompleto"))
                    plugintools.log ("[launcher.py] No se pudo añadir "+str(errores)+" episodios")
                else:
                    itemlist.append(Item(title="La serie è stata aggiunta alla biblioteca"))
                    plugintools.log ("[launcher.py] Ningún error al añadir "+str(errores)+" episodios")
                    
                # FIXME:jesus Comentado porque no funciona bien en todas las versiones de XBMC
                #library.update(totalepisodes,errores,nuevos)
                #xbmctools.renderItems(itemlist, params, url, category)
                    
                #Lista con series para actualizar
                from core import config
                nombre_fichero_config_canal = os.path.join( config.get_library_path() , "series.xml" )
                if not os.path.exists(nombre_fichero_config_canal):
                    nombre_fichero_config_canal = os.path.join( config.get_data_path() , "series.xml" )

                plugintools.log("nombre_fichero_config_canal="+nombre_fichero_config_canal)
                if not os.path.exists(nombre_fichero_config_canal):
                    f = open( nombre_fichero_config_canal , "w" )
                else:
                    f = open( nombre_fichero_config_canal , "r" )
                    contenido = f.read()
                    f.close()
                    f = open( nombre_fichero_config_canal , "w" )
                    f.write(contenido)
                from platformcode import library
                f.write( library.title_to_folder_name(item.show)+","+item.url+","+item.channel+"\n")
                f.close();
                return itemlist
            # --------------------------------------------------------------------
            else:

                if item.action=="search":
                    tecleado = plugintools.keyboard_input()
                    if tecleado!="":
                        tecleado = tecleado.replace(" ", "+")
                        itemlist = channel.search(item,tecleado)
                elif item.channel=="novedades" and item.action=="mainlist":
                    itemlist = channel.mainlist(item,"bannermenu")
                elif item.channel=="buscador" and item.action=="mainlist":
                    itemlist = channel.mainlist(item,"bannermenu")
                else:
                    exec "itemlist = channel."+item.action+"(item)"

                for loaded_item in itemlist:

                    if loaded_item.thumbnail=="":
                        if loaded_item.folder:
                            loaded_item.thumbnail = os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_folder.png" )
                        else:
                            loaded_item.thumbnail = os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_nofolder.png" )

                if len(itemlist)==0:
                    itemlist = [ Item(title="No hay elementos para mostrar", thumbnail=os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_error.png" )) ]

    except:
        import traceback
        plugintools.log("navigation.get_next_items "+traceback.format_exc())
        itemlist = [ Item(title="Se ha producido un error", thumbnail=os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_error.png" )) ]


    return itemlist

def get_window_for_item( item ):
    plugintools.log("navigation.get_window_for_item item.channel="+item.channel+", item.action=="+item.action)

    # El menú principal va con banners + titulo
    if item.channel=="navigation" or (item.channel=="novedades" and item.action=="mainlist") or (item.channel=="buscador" and item.action=="mainlist") or (item.channel=="channelselector" and item.action=="channeltypes"):
        import window_channels
        window = window_channels.ChannelWindow("banner.xml",plugintools.get_runtime_path())

    # El listado de canales va con banners sin título
    elif item.channel=="channelselector" and item.action=="listchannels":
        import window_channels
        window = window_channels.ChannelWindow("channels.xml",plugintools.get_runtime_path())

    # El resto va con el aspecto normal
    else:
        import window_menu
        window = window_menu.MenuWindow("content.xml",plugintools.get_runtime_path())

    return window
