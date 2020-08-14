#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Inkscape extension to edit a stroke font
Dependencies: stroke_font_common.py and stroke_font_manager.py

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

import inkex
from inkex import Effect, addNS
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__))) 
from stroke_font_common import CommonDefs, InkscapeCharDataFactory, createTempl, getAddFnTypes
from stroke_font_common import getTranslatedPath, formatStyle, getEtree, runEffect
from stroke_font_manager import FontData, xPath, xGlyphName

class EditStrokeFont(Effect):

    def __init__(self):
        Effect.__init__(self)

        addFn, typeFloat, typeInt, typeString, typeBool = getAddFnTypes(self)
        
        addFn( "--fontName", action = "store", type = typeString, dest = "fontName", \
            default = 'Script', help = "The custom font to edit")

        addFn('--rowCnt', action = 'store', type = typeInt, dest = 'rowCnt', \
            default = '5', help = 'Number of rows (horizontal guides) in the template')

        addFn('--fontSize', action = 'store', type = typeInt, dest = 'fontSize', \
            default = '100', help = 'Size of the source glyphs to be rendered')

        addFn("--tab", action = "store", type = typeString, dest = "tab", \
            default = "sampling", help = "Tab") 
          
    def addElem(self, templLayer, editLayer, glyphIdx, posX, posY):
        char = self.fontChars[glyphIdx]
        charData = self.strokeFontData.glyphMap[char]
        
        d = getTranslatedPath(charData.pathStr, posX, posY)

        attribs = {'id':char, 'style':formatStyle(self.charStyle), \
            xPath:d, xGlyphName: charData.glyphName}
        getEtree().SubElement(editLayer, addNS('path','svg'), attribs) 
            
        return charData.rOffset


    def effect(self):
        rowCnt = self.options.rowCnt
        fontName = self.options.fontName
        fontSize = self.options.fontSize
        
        lineT = CommonDefs.lineT * fontSize
        strokeWidth = 0.02 * fontSize
        self.charStyle = { 'stroke': '#000000', 'fill': 'none', \
            'stroke-width':strokeWidth, 'stroke-linecap':'round', \
                'stroke-linejoin':'round'}

        vgScaleFact = CommonDefs.vgScaleFact        
        
        extPath = os.path.dirname(os.path.abspath(__file__))
        self.strokeFontData = FontData(extPath, fontName, fontSize, \
            InkscapeCharDataFactory())

        self.fontChars = sorted(self.strokeFontData.glyphMap.keys())
        
        glyphCnt = len(self.fontChars)
        
        createTempl(self.addElem, self, self.strokeFontData.extraInfo, rowCnt, \
            glyphCnt, vgScaleFact, True, lineT)
    
runEffect(EditStrokeFont())
