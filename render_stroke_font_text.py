#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inkscape extension to render text with the stroke fonts.

The path data used to render the text is generated by the 
'Generate Font Data' extension

The original concept is from Hershey Text extension (Copyright 2011, Windell H. Oskay), 
that comes bundled with Inkscape

This tool extends it with a number of rendering options like flow in boxes, 
text alignment and char & line spacing

Copyright 2019 Shrinivas Kulkarni

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from inkex import addNS, NSS, Effect, errormsg
import os, sys
from simplepath import parsePath, translatePath, formatPath

sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

from stroke_font_common import CommonDefs, InkscapeCharDataFactory, getEtree, getAddFnTypes
from stroke_font_common import computePtInNode, getDecodedChars 
from stroke_font_common import getViewCenter, runEffect, getSelectedElements
from stroke_font_common import formatStyle, getCharStyle, getTranslatedPath, getCurrentLayer

from stroke_font_manager import DrawContext

class InkscapeFontRenderer:
    def __init__(self, layer, vc, strokeWidth):
        self.layer = layer
        self.g = None
        self.currG = None
        self.vc = computePtInNode(vc, layer)

        self.strokeWidth = strokeWidth
        self.box = None

    def renderChar(self, charData, x, y, naChar):
        d =  charData.pathStr        
        style = getCharStyle(self.strokeWidth, naChar)
            
        d = getTranslatedPath(d, x, y)
            
        attribs = {'style':formatStyle(style), 'd':d}
        getEtree().SubElement(self.currG, addNS('path','svg'), attribs) 
        
    def beforeRender(self):
        self.g = getEtree().SubElement(self.layer, 'g')
        self.currG = self.g
    
    def newBoxToBeRendered(self, box, addPlane):        
        boxG = getEtree().SubElement(self.layer, 'g')
        
        if('transform' in box.attrib):            
            boxG.set('transform', box.get('transform'))
            
        box.getparent().remove(box)
        
        # order important!
        self.g.append(box)
        self.g.append(boxG)
        self.currG = boxG
        self.box = box
        
    def moveBoxInYDir(self, moveBy):
        t = 'translate(' + str(0) + ',' + str(moveBy) + ')'
        self.currG.set('transform', t)

    def centerInView(self, width, height):          
        t = 'translate(' + str(self.vc[0] - width) + ',' + str(self.vc[1] - height) + ')'            
        self.g.set('transform', t)

    def renderPlainText(self, text, size, x = None, y = None, objName = None):
        textStyle = {'fill':'#000000', 'fill-opacity':'1'}            
        textStyle['font-size'] = str(size)
        attribs = {'style':formatStyle(textStyle)}
        if(x != None and y != None):
            attribs['transform'] = 'translate(' + str(x) + ', '+ str(y)+')'
        
        textElem = getEtree().SubElement(self.g, addNS('text','svg'), attribs)        
        textElem.text = text

    def getBoxLeftTopRightBottom(self, box):
        x1 = float(box.get('x'))
        y1 = float(box.get('y'))
        w = float(box.get('width'))
        h = float(box.get('height'))

        x2 = w + x1
        y2 = h + y1

        return x1, y1, x2, y2
        
    def getBoxFromCoords(self, x1, y1, x2, y2):
        attribs = {'x':str(x1), 'y':str(y1), 'width':str(x2-x1), 'height':str(y2-y1)}
        attribs['style'] = self.box.get('style')
        self.box = getEtree().SubElement(self.layer, addNS('rect','svg'), attribs)        
        return self.box
        
    def getDefaultStartLocation(self):
        return 0, 0

class RenderStrokeFontText(Effect):
    def __init__( self ):
        Effect.__init__( self )

        addFn, typeFloat, typeInt, typeString, typeBool = getAddFnTypes(self)

        addFn( '--tab',  action = 'store', type = typeString, dest = 'tab', \
            default = 'splash', help = 'The active tab when Apply was pressed')
            
        addFn( '--action', action = 'store', type = typeString, dest = 'action', \
            default = 'render', help = 'The active option when Apply was pressed' )

        addFn( '--text', action = 'store', type = typeString, dest = 'text', \
            default = 'Hello World', help = 'The input text to render')
            
        addFn( '--filePath', action = 'store', type = typeString, dest = 'filePath', \
            default = '', help = 'Complete path of the text file')
            
        addFn( '--fontName', action = 'store', type = typeString, dest = 'fontName', \
            default = 'Script',  help = 'The custom font to be used for rendering')

        addFn('--fontSize', action = 'store', type = typeFloat, dest = 'fontSize', \
            default = '100', help = 'Size of the font')

        addFn('--charSpacing', action = 'store', type = typeFloat, dest = 'charSpacing', \
            default = '1', help = 'Spacing between characters')

        addFn('--wordSpacing', action = 'store', type = typeFloat, dest = 'wordSpacing', \
            default = '1', help = 'Spacing between words')

        addFn('--lineSpacing', action = 'store', type = typeFloat, dest = 'lineSpacing', \
            default = '1.5', help = 'Spacing between the lines')

        addFn('--strokeWidthMult', action = 'store', type = typeFloat, dest = 'strokeWidthMult', \
            default = '1', help = 'Stroke Width Proportion')

        addFn('--flowInBox', action = 'store', type = typeBool, dest = 'flowInBox', \
            default = False, help = 'Fit the text in the selected rectangle objects')

        addFn('--margin', action = 'store', type = typeFloat, dest = 'margin', default = '.1', \
          help = 'Inside margin of text within the box')

        addFn( '--hAlignment', action='store', type = typeString, dest = 'hAlignment', \
            default = 'left',  help='Horizontal text alignment within the box')

        addFn( '--vAlignment', action='store', type = typeString, dest = 'vAlignment', \
            default = 'none',  help='Vertical text alignment within the box')

        addFn( '--expandDir', action='store', type = typeString, dest = 'expandDir', \
            default = 'x', help='Create new rectangles if text doesn\'t fit the selected ones')

        addFn('--expandDist', action = 'store', type = typeFloat, dest = 'expandDist', \
            default = True, help = 'Offset distance between the newly created rectangles')

    def effect(self):
        fontName = self.options.fontName
        fontSize = self.options.fontSize
        filePath = self.options.filePath
        action = self.options.action
        strokeWidthMult = self.options.strokeWidthMult

        if(action == "renderTable"):
            charSpacing = 1
            wordSpacing = 1
            lineSpacing = 2
        else:
            charSpacing = self.options.charSpacing
            wordSpacing = self.options.wordSpacing
            lineSpacing = self.options.lineSpacing        
        
        flowInBox = self.options.flowInBox
        margin = self.options.margin
        hAlignment = self.options.hAlignment
        vAlignment = self.options.vAlignment
        expandDir = self.options.expandDir
        expandDist = self.options.expandDist
        
        if(expandDir == 'none'):
            expandDir = None
            expandDist = None

        extPath = os.path.dirname(os.path.abspath(__file__))
        
        strokeWidth = 0.02 * fontSize * strokeWidthMult
        
        layer = getCurrentLayer(self)
        renderer = InkscapeFontRenderer(layer, getViewCenter(self), strokeWidth)

        context = DrawContext(extPath, fontName, fontSize, \
            charSpacing, wordSpacing, lineSpacing, InkscapeCharDataFactory(), renderer) 
            
        if(not context.fontHasGlyphs()): 
            errormsg('No font data; please select a font and ' + \
                'ensure that the list is synchronized')
            return
        
        if(action == "renderTable"):
            context.renderGlyphTable()
            return 
            
        if(action == "renderText"):
            text = self.options.text
            text = text.replace('\\n','\n').replace('\\\n','\\n')
            text = getDecodedChars(text)
            
        elif(action == "renderFile"):
            try:
                readmode = 'rU' if CommonDefs.pyVer == 2 else 'r'
                with open(filePath, readmode) as f: 
                    text = f.read() 
                    if(CommonDefs.pyVer == 2): text = unicode(text, 'utf-8')
            except Exception as e:
                errormsg("Error reading the file specified in Text File input box."+ str(e))
                return

        if(text[0] == u'\ufeff'):
            text = text[1:]

        if(flowInBox == True):
            selElems = getSelectedElements(self)
            selIds = [selElems[key].get('id') for key in selElems.keys()]
            rectNodes = [r for r in self.document.xpath('//svg:rect', \
                namespaces=NSS) if r.get('id') in selIds]
            if(len(rectNodes) == 0):
                errormsg(_("No rectangle objects selected."))
                return
            context.renderCharsInSelBoxes(text, rectNodes, margin, hAlignment, vAlignment, \
                False, expandDir, expandDist)
        else:
            context.renderCharsWithoutBox(text)

runEffect(RenderStrokeFontText())
