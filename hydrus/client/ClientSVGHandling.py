import typing

from qtpy import QtSvg
from qtpy import QtGui as QG
from qtpy import QtCore as QC

from hydrus.core import HydrusExceptions
from hydrus.core import HydrusImageHandling
from hydrus.core import HydrusSVGHandling

from hydrus.client.gui import ClientGUIFunctions

def LoadSVGRenderer( path: str ):
    
    renderer = QtSvg.QSvgRenderer()
    
    try:
        
        renderer.load( path )
        
    except:
        
        raise  HydrusExceptions.DamagedOrUnusualFileException( 'Could not load SVG file.' )
        
    
    if not renderer.isValid():
        
        raise  HydrusExceptions.DamagedOrUnusualFileException( 'SVG file is invalid!' )
        
    
    return renderer
    

def GenerateThumbnailBytesFromSVGPath( path: str, target_resolution: typing.Tuple[int, int], clip_rect = None ) -> bytes:
    
    # TODO: SVGs have no inherent resolution, so all this is pretty stupid. we should render to exactly the res we want and then clip the result, not beforehand
    
    renderer = LoadSVGRenderer( path )
    
    # Seems to help for some weird floating point dimension SVGs
    renderer.setAspectRatioMode( QC.Qt.AspectRatioMode.KeepAspectRatio )
    
    try:
        
        if clip_rect is None:
            
            ( target_width, target_height ) = target_resolution
            
            qt_image = QG.QImage( target_width, target_height, QG.QImage.Format_RGBA8888 )
            
        else:
            
            qt_image = QG.QImage( renderer.defaultSize(), QG.QImage.Format_RGBA8888 )
            
        
        qt_image.fill( QC.Qt.transparent )
        
        painter = QG.QPainter( qt_image )
        
        renderer.render( painter )
        
        painter.end()
        
        numpy_image = ClientGUIFunctions.ConvertQtImageToNumPy( qt_image )
        
        if clip_rect is None:
            
            thumbnail_numpy_image = numpy_image
            
        else:
            
            numpy_image = HydrusImageHandling.ClipNumPyImage( numpy_image, clip_rect )
            
            thumbnail_numpy_image = HydrusImageHandling.ResizeNumPyImage( numpy_image, target_resolution )
            
        
        return HydrusImageHandling.GenerateThumbnailBytesNumPy( thumbnail_numpy_image )
        
    except:
        
        raise HydrusExceptions.UnsupportedFileException()
        
    

HydrusSVGHandling.GenerateThumbnailBytesFromSVGPath = GenerateThumbnailBytesFromSVGPath

def GetSVGResolution( path: str ):
    
    renderer = LoadSVGRenderer( path )
    
    resolution = renderer.defaultSize().toTuple()
    
    return resolution
    

HydrusSVGHandling.GetSVGResolution = GetSVGResolution
