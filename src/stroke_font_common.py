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

import inkex, os, fileinput
from xml.dom.minidom import parse, Document
from cubicsuperpath import CubicSuperPath, formatPath
from simplepath import parsePath

class CommonDefs:
    extXmlFileName = 'render_stroke_font_text.inx'
    
    vgScaleFact = 2.
    guideAttribName = 'guide'
    hGuideAttrib = 'h'
    lvGuideAttrib = 'lv'
    rvGuideAttrib = 'rv'
    hSeqAttribName = 'hSeq'
    vSeqAttribName = 'vSeq'

    dataFileName = 'customstrokefontdata.xml'
    ##### XML Data Constants ########
    xRoot = 'strokefonts'
    xFont = 'font'
    xName = 'name'
    xSize = 'size'
    xGlyph = 'glyph'
    xChar = 'char'
    xWidth = 'width'
    xCRInfo = 'crinfo'
    
    #### XML Comment ####
    xHeader = 'The data file defining the stroke fonts'

def getDataFileDoc(dataFilePath):
    try:
        # ~ doc = parse(dataFilePath)
        with open(dataFilePath) as xml:
            doc = parse(xml)        
    except:
        doc = Document()
        rootElem = doc.createElement(CommonDefs.xRoot)
        doc.appendChild(doc.createComment(CommonDefs.xHeader))
        doc.appendChild(rootElem)
        
    return doc
    
def updateDataFile(doc, dataFilePath):
    f = open(dataFilePath, "w")
    f.write(doc.toxml(encoding="utf-8"))
    f.close()
        
def indentStr(cnt):
    ostr = ''
    for i in range(0, cnt):
        ostr += '    '
    return ostr
    
def syncFontList(doc):
    sectMarker = '<!-- ##! dynamically generated portion'

    found = False
    outStr = indentStr(1) + sectMarker + ' [start] -->\n'
    xmlFilePath = os.path.dirname(os.path.abspath(__file__)) + "/" + CommonDefs.extXmlFileName
    
    try:
        fontNames = [e.getAttribute(CommonDefs.xName) for e in \
            doc.getElementsByTagName(CommonDefs.xFont)]

        for fName in fontNames:
            outStr += indentStr(2) + '<item value="' + fName + '">' + fName + '</item>\n'
    
        outStr += indentStr(1) + sectMarker + ' [end] -->\n'
    
        for line in fileinput.input(xmlFilePath, inplace = 1):
            if sectMarker in line:
                if(found):
                    print outStr,
                    found = False
                else:
                    found = True
            else:
                if(not found):
                    print line,

    except Exception as e:
        inkex.errormsg(_('Error updating font list...\n' + str(e)))

def scaleGlyph(glyphD, scaleFactor):
    
    cspath = CubicSuperPath(parsePath(glyphD))
    for subpath in cspath:
        for bezierPts in subpath:
            for i in range(0, len(bezierPts)):
                #No worries about origin...
                bezierPts[i] = [bezierPts[i][0] * scaleFactor, 
                    bezierPts[i][1] * scaleFactor]                    
    return formatPath(cspath)
    
class FontData:
    
    def __init__(self, dataDoc, fontName):
        self.fontName = fontName
        self.glyphMap = {}
        self.crInfo = ""
        self.fontSize = -1
        self.fontElem = None

        fontElems = [e for e in dataDoc.getElementsByTagName(CommonDefs.xFont) \
            if e.getAttribute(CommonDefs.xName) == fontName]

        if(len(fontElems) > 0):
            self.fontElem = fontElems[0]            
            crElem = self.fontElem.getElementsByTagName(CommonDefs.xCRInfo)[0]
            if(len(crElem.childNodes) > 0):
                self.crInfo = crElem.childNodes[0].data

            self.fontSize = float(self.fontElem.getAttribute(CommonDefs.xSize))
            glyphElems = self.fontElem.getElementsByTagName(CommonDefs.xGlyph)
            
            for e in glyphElems:
                char = e.getAttribute(CommonDefs.xChar)
                rOffset = e.getAttribute(CommonDefs.xWidth)
                glyphD = e.childNodes[0].data
                self.glyphMap[char] = [rOffset, glyphD]

    def isNew(self):
        return self.fontElem == None
    
    def scaleFont(self, newFontSize):        
        if(self.fontSize > 0):
            for char in self.glyphMap:            
                rOffset = float(self.glyphMap[char][0])
                glyphD = self.glyphMap[char][1]
                newD = scaleGlyph(glyphD, newFontSize / self.fontSize)
                scaledOffset = rOffset * newFontSize / self.fontSize
                self.glyphMap[char] = [scaledOffset, newD]
            
        self.fontSize = newFontSize
    
    def setCRInfo(self, crInfo):
        self.crInfo = crInfo
        
    def updateFontElemInDoc(self, doc):
        if(self.fontElem != None):
            doc.documentElement.removeChild(self.fontElem)
        
        self.fontElem = doc.createElement(CommonDefs.xFont)
        doc.documentElement.appendChild(self.fontElem)
        self.fontElem.setAttribute(CommonDefs.xName, self.fontName)
        self.fontElem.setAttribute(CommonDefs.xSize, str(self.fontSize))
        
        crElem = doc.createElement(CommonDefs.xCRInfo)
        crElem.appendChild(doc.createTextNode(self.crInfo))
        self.fontElem.appendChild(crElem)
        
        for char in self.glyphMap:
            val = self.glyphMap[char]
            width = val[0]
            pathStr = val[1]

            glyphElem = doc.createElement(CommonDefs.xGlyph)
            glyphElem.setAttribute(CommonDefs.xChar, char)
            glyphElem.setAttribute(CommonDefs.xWidth, str(width))
            glyphElem.appendChild(doc.createTextNode(pathStr))
            self.fontElem.appendChild(glyphElem)
