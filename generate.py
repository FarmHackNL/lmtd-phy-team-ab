from qgis.core import QgsApplication
from PyQt4.QtCore import QFileInfo
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
import ogr2ogr
import processing

# Write your code here to load some layers, use processing algorithms, etc.

def StringToRaster(raster):
    # Check if string is provided

    fileInfo = QFileInfo(raster)
    path = fileInfo.filePath()
    baseName = fileInfo.baseName()

    layer = QgsRasterLayer(path, baseName)
    #QgsMapLayerRegistry.instance().addMapLayer(layer)
    
    entries = []
    # Define band1
    boh1 = QgsRasterCalculatorEntry()
    boh1.ref = 'ndvi20160607sentinel@5'
    boh1.raster = layer
    boh1.bandNumber = 5
    entries.append( boh1 )
    	
    # Process calculation with input extent and resolution
    calc = QgsRasterCalculator( '(ndvi20160607sentinel@5) * 166.67 + 111.67', 'C:/Hackathon Farmhack data/Output/outputfile.tif', 'GTiff', layer.extent(), layer.width(), layer.height(), entries )
    calc.processCalculation()
    
    fileInfo = QFileInfo('C:/Hackathon Farmhack data/Output/outputfile.tif')
    path = fileInfo.filePath()
    baseName = fileInfo.baseName()
    
    layer = QgsRasterLayer(path, baseName)
    #QgsMapLayerRegistry.instance().addMapLayer(layer)
    
    if layer.isValid() is True:
        print "Layer was loaded successfully!"
    
    else:
        print "Unable to read basename and file path - Your string is probably invalid"
    
    shape = QgsVectorLayer('C:/Hackathon Farmhack data/perceel-hier-rdnew.geojson', 'perceel', 'ogr')
    #QgsMapLayerRegistry.instance().addMapLayer(shape)
    xmin = (shape.extent().xMinimum()) #extract the minimum x coord from our layer
    xmax = (shape.extent().xMaximum()) #extract our maximum x coord from our layer
    ymin = (shape.extent().yMinimum()) #extract our minimum y coord from our layer
    ymax = (shape.extent().yMaximum()) #extract our maximum y coord from our layer
    #prepare the extent in a format the VectorGrid tool can interpret (xmin,xmax,ymin,ymax)
    extent = str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax)  
    
    # raster the given shape
    processing.runalg('qgis:vectorgrid', extent, 20, 20, 0, 'C:/Hackathon Farmhack data/Output/rasterShapes.geojson')
    
    shapeRaster = QgsVectorLayer('C:/Hackathon Farmhack data/Output/rasterShapes.geojson', 'perceelRaster', 'ogr')
    shapeRaster.setCrs(QgsCoordinateReferenceSystem(28992,  QgsCoordinateReferenceSystem.EpsgCrsId))
    #QgsMapLayerRegistry.instance().addMapLayer(shapeRaster)
    
    #clip the raster returned
    processing.runalg('qgis:clip', shapeRaster, shape, 'C:/Hackathon Farmhack data/Output/clippedRaster.shp')

    #define oldPath and newPath
    ogr2ogr.main(["","-f", "ESRI Shapefile", "-s_srs", "epsg:28992", "-t_srs", "epsg:32632", "C:/Hackathon Farmhack data/Output/clippedRasterNew.shp", "C:/Hackathon Farmhack data/Output/clippedRaster.shp"])
    
    clippedRaster = QgsVectorLayer('C:/Hackathon Farmhack data/Output/clippedRasterNew.shp', 'clippedRaster', 'ogr')
    clippedRaster.setCrs(QgsCoordinateReferenceSystem(32632,  QgsCoordinateReferenceSystem.EpsgCrsId))
    #QgsMapLayerRegistry.instance().addMapLayer(clippedRaster)
    
    #zonalstatistics
    processing.runalg('qgis:zonalstatistics', layer, 1, clippedRaster, '', False, 'C:/Hackathon Farmhack data/Output/filledRaster.geojson')
    filledRaster = QgsVectorLayer('C:/Hackathon Farmhack data/Output/filledRaster.geojson', 'filledRaster', 'ogr')
    filledRaster.setCrs(QgsCoordinateReferenceSystem(32632,  QgsCoordinateReferenceSystem.EpsgCrsId))
    #QgsMapLayerRegistry.instance().addMapLayer(filledRaster)    
	
    ogr2ogr.main(["","-f", "GeoJSON", "-s_srs", "epsg:32632", "-t_srs", "epsg:4326", "C:/Hackathon Farmhack data/Output/taakkaart.geojson", "C:/Hackathon Farmhack data/Output/filledRaster.geojson"])
    taakkaart = QgsVectorLayer('C:/Hackathon Farmhack data/Output/taakkaart.geojson', 'taakkaart', 'ogr')
    QgsMapLayerRegistry.instance().addMapLayer(taakkaart)    
    
raster = 'C:/Hackathon Farmhack data/huiges1_2016_06_24_green_red_re_nir_ndvi.tif'

StringToRaster(raster)
