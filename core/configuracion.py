# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# streamondemand-pureita - XBMC Plugin
# Configuración
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

from core import downloadtools
from core import config
from core import logger

logger.info("[configuracion.py] init")

def mainlist(params,url,category):
    logger.info("[configuracion.py] mainlist")
    
    config.open_settings( )
