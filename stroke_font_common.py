#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Defintion of Common functions and variables used by stroke font extensions

Copyright (C) 2019  Shrinivas Kulkarni

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''

import sys, os, fileinput, re, locale
from inkex import errormsg, addNS, NSS
from xml.dom.minidom import parse, Document
from math import ceil

# TODO: Find inkscape version
try:
    from lxml import etree
    from inkex import Style, Boolean
    from inkex.paths import Path, CubicSuperPath, Transform
    from inkex import bezier
    ver = 1.0 
except:
    from inkex import etree
    import simplestyle, cubicsuperpath, simplepath, simpletransform
    from cubicsuperpath import CubicSuperPath
    ver = 0.92
    try:
        from simpletransform import computePointInNode
        oldVersion = False
    except:
        oldVersion = True # older than 0.92

# sys path already includes the module folder
from stroke_font_manager import CharData, getFontNames, xAscent, \
    xDescent, xCapHeight, xXHeight, xSpaceROff, xFontId, xSize

class CommonDefs:
    inkVer = ver
    pyVer = sys.version_info.major

    # inx filed that have the font list to be synchronized
    inxFilesWithDynFont = ['render_stroke_font_text.inx', 'edit_stroke_font.inx']

    vgScaleFact = 2.
    lineT = .005

    idAttribName = 'id'
    hGuideIDPrefix = 'h_'
    lvGuideIDPrefix = 'lv_'
    rvGuideIDPrefix = 'rv_'

    fontOtherInfo = 'otherInfo'

    encoding = sys.stdin.encoding
    if(encoding == 'cp0' or encoding is None):
        encoding = locale.getpreferredencoding()


######### Function variants for 1.0 and 0.92 - Start ##########

# Used only in 0.92
def getPartsFromCubicSuper(csp):
    parts = []
    for subpath in csp:
        part = []
        prevBezPt = None            
        for i, bezierPt in enumerate(subpath):
            if(prevBezPt != None):
                seg = [prevBezPt[1], prevBezPt[2], bezierPt[0], bezierPt[1]]
                part.append(seg)
            prevBezPt = bezierPt
        parts.append(part)
    return parts

def formatStyle(styleStr):
    if(CommonDefs.inkVer == 1.0):
        return str(Style(styleStr))
    else:
        return simplestyle.formatStyle(styleStr)

def getCubicSuperPath(d = None):
    if(CommonDefs.inkVer == 1.0):
        if(d == None): return CubicSuperPath([])
        return CubicSuperPath(Path(d).to_superpath())
    else:
        if(d == None): return []
        return CubicSuperPath(simplepath.parsePath(d))

def getCubicLength(csp):
    if(CommonDefs.inkVer == 1.0):
        return bezier.csplength(csp)[1]
    else:
        parts = getPartsFromCubicSuper(cspath)
        curveLen = 0
        for i, part in enumerate(parts):
            for j, seg in enumerate(part):
                curveLen += bezmisc.bezierlengthSimpson((seg[0], seg[1], seg[2], seg[3]), \
                tolerance = tolerance)
        return curveLen

def getCubicBoundingBox(csp):
    if(CommonDefs.inkVer == 1.0):
        bbox = csp.to_path().bounding_box()
        return bbox.left, bbox.right, bbox.top, bbox.bottom
    else:
        return simpletransform.refinedBBox(csp)

def formatSuperPath(csp):
    if(CommonDefs.inkVer == 1.0):
        return csp.__str__()
    else:
        return cubicsuperpath.formatPath(csp)

def getParsedPath(d):
    if(CommonDefs.inkVer == 1.0):
        # Copied from Path.to_arrays for compatibility
        return [[seg.letter, list(seg.args)] for seg in Path(d).to_absolute()]
    else:
        return simplepath.parsePath(d)

def applyTransform(mat, csp):
    if(CommonDefs.inkVer == 1.0):
        csp.transform(mat)
    else:
        simpletransform.applyTransformToPath(mat, csp)

def getTranslatedPath(d, posX, posY):
    if(CommonDefs.inkVer == 1.0):
        path = Path(d)
        path.translate(posX, posY, inplace = True)
        return path.to_superpath().__str__()
    else:
        path = simplepath.parsePath(d)
        simplepath.translatePath(path, posX, posY)
        return simplepath.formatPath(path)

def getTransformMat(matAttr):
    if(CommonDefs.inkVer == 1.0):
        return Transform(matAttr)
    else:
        return simpletransform.parseTransform(matAttr)

def getCurrentLayer(effect):
    if(CommonDefs.inkVer == 1.0):
        return effect.svg.get_current_layer()
    else:
        return effect.current_layer

def getViewCenter(effect):
    if(CommonDefs.inkVer == 1.0):
        return effect.svg.namedview.center
    else:
        return effect.view_center

def computePtInNode(vc, layer):
    if(CommonDefs.inkVer == 1.0):
        # ~ return (-Transform(layer.transform * mat)).apply_to_point(vc)
        return (-layer.transform).apply_to_point(vc)
    else:
        if(oldVersion):
            return list(vc)
        else:
            return computePointInNode(list(vc), layer)

def getSelectedElements(effect):
    if(CommonDefs.inkVer == 1.0):
        return effect.svg.selected
    else:
        return effect.selected

def getEtree():
    return  etree

def getAddFnTypes(effect):
    if(CommonDefs.inkVer == 1.0): 
        addFn = effect.arg_parser.add_argument
        typeFloat = float
        typeInt = int
        typeString = str
        typeBool = Boolean
    else: 
        addFn = effect.OptionParser.add_option
        typeFloat = 'float'
        typeInt = 'int'
        typeString = 'string'
        typeBool = 'inkbool'

    return addFn, typeFloat, typeInt, typeString, typeBool

def runEffect(effect):
    if(CommonDefs.inkVer == 1.0): effect.run()
    else: effect.affect()
    
######### Function variants for 1.0 and 0.92 - End ##########

def getDecodedChars(chars):
    if(CommonDefs.pyVer == 2):
        return chars.decode(CommonDefs.encoding)
    else: #if?
        return chars

def indentStr(cnt):
    ostr = ''
    for i in range(0, cnt):
        ostr += ' '
    return ostr

def getXMLItemsStr(sectMarkerLine, sectMarker, fontNames):
    lSpaces = sectMarkerLine.find(sectMarker)
    outStr = indentStr(lSpaces) + sectMarker + ' [start] -->\n'
    for fName in fontNames:
        outStr += indentStr(lSpaces + 4) + '<item value="' + fName + '">' + fName + '</item>\n'
    outStr += indentStr(lSpaces) + sectMarker + ' [end] -->\n'
    return outStr

def syncFontList(extPath):
    sectMarker = '<!-- ##! dynamically generated portion'

    sectMarkerLine = None
    xmlFilePaths = [extPath + "/" +  f for f in CommonDefs.inxFilesWithDynFont]

    try:
        fontNames = getFontNames(extPath)
        for xf in xmlFilePaths:
            for line in fileinput.input(xf, inplace = True):
                if sectMarker in line:
                    if(sectMarkerLine != None):
                        if(CommonDefs.pyVer == 3):
                            # For some reasons python2 giving syntax error without eval
                            eval("print(getXMLItemsStr(sectMarkerLine, sectMarker, fontNames), end = '')")
                        else:
                            print(getXMLItemsStr(sectMarkerLine, sectMarker, fontNames)),

                        sectMarkerLine = None
                    else:
                        sectMarkerLine = line
                else:
                    if(sectMarkerLine == None):
                        if(CommonDefs.pyVer == 3):
                            eval("print(line, end = '')")
                        else:
                            print(line),

    except Exception as e:
        errormsg('Error updating font list...\n' + str(e))

def addGridLine(layer, posX, posY, length, lType, style, attribs):
    line = etree.Element(addNS('path','svg'))
    d = 'M '+str(posX) + ' ' + str(posY) +' '+ lType +' '

    if(lType == 'H'):
        d += str(posX + length)
    if(lType == 'V'):
        d += str(posY + length)

    line.set('style', formatStyle(style))
    line.set('d', d)

    for key in attribs:
        line.set(key, attribs[key])

    layer.append(line)

def addText(layer, textStr, posX, posY, style):
    text = etree.Element(addNS('text','svg'))
    text.text = textStr

    text.set('x', str(posX))
    text.set('y', str(posY))

    text.set('style', formatStyle(style))

    layer.append(text)


def createTempl(callback, effect, extraInfo, rowCnt, glyphCnt, \
    vgScaleFact, createRvGuides, lineT):

        hgStyle = {'stroke-width':str(lineT), 'opacity':'1', 'stroke':'#ff0066'}
        lvgStyle = {'stroke-width':str(lineT), 'opacity':'1', 'stroke':'#00aa88'}
        rvgStyle = {'stroke-width':str(lineT), 'opacity':'1', 'stroke':'#1b46ff'}

        fontSize = extraInfo[xSize]
        spcY = fontSize * 3
        spcX = fontSize * 3

        fontSize = extraInfo[xSize]
        vLineH = fontSize * vgScaleFact

        colCnt = int(ceil(float(glyphCnt) / float(rowCnt)))

        docW = (colCnt + 1) * spcX
        docH = (rowCnt + 1) * spcY

        svg = effect.document.getroot()
        svg.set('width', str(docW))
        svg.set('height', str(docH))

        #Remove viewbox
        if('viewBox' in svg.attrib):
            svg.attrib.pop('viewBox')

        currLayers = svg.xpath('//svg:g', namespaces = NSS)
        for layer in currLayers:
            # Note: getparent()
            parentLayer = layer.getparent() if(CommonDefs.inkVer == 1.0) \
                else effect.getParentNode(layer)

            if(parentLayer != None):
                parentLayer.remove(layer)

        currExtraElems = svg.xpath('//svg:' + CommonDefs.fontOtherInfo, namespaces = NSS)
        for elem in currExtraElems:
            parentElem = elem.getparent() if(CommonDefs.inkVer == 1.0) \
                else effect.getParentNode(elem)
            parentElem.remove(elem)

        extraInfoElem = etree.SubElement(svg, CommonDefs.fontOtherInfo)
        extraInfoElem.set(xAscent, str(extraInfo[xAscent]))
        extraInfoElem.set(xDescent, str(extraInfo[xDescent]))
        extraInfoElem.set(xCapHeight, str(extraInfo[xCapHeight]))
        extraInfoElem.set(xXHeight, str(extraInfo[xXHeight]))
        extraInfoElem.set(xSpaceROff, str(extraInfo[xSpaceROff]))
        extraInfoElem.set(xFontId, str(extraInfo[xFontId]))
        extraInfoElem.set(xSize, str(extraInfo[xSize]))

        editLayer = etree.SubElement(svg, 'g')
        editLayer.set(addNS('label', 'inkscape'), 'Glyphs')
        editLayer.set(addNS('groupmode', 'inkscape'), 'layer')
        editLayer.set('id', 'glyph')#TODO: How to make this dynamic?
        view = svg.namedview if CommonDefs.inkVer == 1.0 else effect.getNamedView() 
        view.set(addNS('current-layer', 'inkscape'), editLayer.get('id'))

        templLayer = etree.SubElement(svg, 'g')
        templLayer.set(addNS('label', 'inkscape'), 'Template')
        templLayer.set(addNS('groupmode', 'inkscape'), 'layer')

        for row in range(0, rowCnt):

            hAttribs = {CommonDefs.idAttribName : CommonDefs.hGuideIDPrefix + str(row)}
            addGridLine(templLayer, 0, \
                (row + 1) * spcY, docW, 'H', hgStyle, hAttribs)

            for col in range(0, colCnt):
                glyphIdx = row * colCnt + col

                if(glyphIdx >= glyphCnt):
                    break

                posX = (col + 1) * spcX
                posY = (row + 1) * spcY# + lineT / 2

                #Caller can create whatever it wants at this position
                rOffset = callback(templLayer, editLayer, glyphIdx, posX, posY)
                if(rOffset == None):
                    rOffset = fontSize

                lvAttribs = {CommonDefs.idAttribName : CommonDefs.lvGuideIDPrefix + \
                     str(row).zfill(4) + '_' + str(col).zfill(4)}

                addGridLine(templLayer, \
                    posX, posY + fontSize / 1.5, -vLineH, 'V', \
                        lvgStyle, lvAttribs)

                if(createRvGuides):
                    rvAttribs = {CommonDefs.idAttribName : CommonDefs.rvGuideIDPrefix + \
                        str(row).zfill(4) + '_' + str(col).zfill(4)}

                    addGridLine(templLayer, \
                        posX + rOffset, posY + fontSize / 1.5, -vLineH, 'V', \
                            rvgStyle, rvAttribs)

def getCharStyle(strokeWidth, naChar):
    #na character is a filled box
    naStyle = { 'stroke': '#000000', 'fill': '#000000', 'stroke-width': strokeWidth}
    charStyle = { 'stroke': '#000000', 'fill': 'none', 'stroke-width': strokeWidth,
        'stroke-linecap':'round', 'stroke-linejoin':'round'}

    if(naChar):
        return naStyle
    else:
        return charStyle

class InkscapeCharData(CharData):
    def __init__(self, char, rOffset, pathStr, glyphName):
        self.pathStr = pathStr
        super(InkscapeCharData, self).__init__(char, rOffset, glyphName)

    def getBBox(self):
        return getCubicBoundingBox(getCubicSuperPath(self.pathStr))

    def scaleGlyph(self, scaleX, scaleY):
        self.rOffset *= scaleX
        cspath = getCubicSuperPath(self.pathStr)
        for subpath in cspath:
            for bezierPts in subpath:
                for i in range(0, len(bezierPts)):
                    #No worries about origin...
                    bezierPts[i] = [bezierPts[i][0] * scaleX, bezierPts[i][1] * scaleY]
        self.pathStr = formatSuperPath(cspath)
        self.bbox = getCubicBoundingBox(cspath)

class InkscapeCharDataFactory:
    def __init__(self):
        pass

    def getCharData(self, char, rOffset, pathStr, glyphName):
        return InkscapeCharData(char, rOffset, pathStr, glyphName)
