#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Inkscape extension to generate template for designing / tracing custom stroke fonts

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

from inkex import Effect
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__))) 
from stroke_font_common import CommonDefs, getDecodedChars, createTempl, addText
from stroke_font_common import getAddFnTypes, runEffect
from stroke_font_manager import xSpaceROff, getDefaultExtraInfo

class CustStrokeFontTempl(Effect):

    def __init__(self):
        Effect.__init__(self)

        addFn, typeFloat, typeInt, typeString, typeBool = getAddFnTypes(self)

        addFn('--rowCnt', action = 'store', type = typeInt, dest = 'rowCnt', default = '5', \
          help = 'Number of rows (horizontal guides) in the template')

        addFn("--createGlyphs", action="store", type=typeBool, dest="createGlyphs", \
            default=True, help = 'Render glyphs of the source font family for tracing ')

        addFn('--srcFontFamily', action = 'store', type = typeString, dest = 'srcFontFamily', \
          help = 'Exact name of the source font family')

        addFn('--fontSize', action = 'store', type = typeInt, dest = 'fontSize', default = '100', \
          help = 'Size of the source glyphs to be rendered')

        addFn('--spaceWidth', action = 'store', \
          type = typeInt, dest = 'spaceWidth', default = '50', \
          help = 'Width of the space character (generally 1/3 to 1/2 times the font size')

        addFn('--fontType', action = 'store', type = typeString, dest = 'fontType', \
            default = 'normal', help = 'Font Style')

        addFn('--startGlyph', action = 'store', type = typeString, dest = 'startGlyph', \
            default = '0', help = 'Starting glyph to be rendered')

        addFn('--glyphCnt', action = 'store', type = typeInt, dest = 'glyphCnt', \
            default = '75', help = 'Number of template glyphs')

        addFn("--rvGuides", action = "store", type = typeBool, dest = "rvGuides", \
            default = False, help = 'Render vertical guide at the right of each glyph')

        addFn("--tab", action = "store", type = typeString, dest = "tab", \
            default = "sampling", help="Tab") 
          
    def addElem(self, templLayer, editLayer, glyphIdx, posX, posY):
        if(self.createTTGlyphs):
            if(CommonDefs.pyVer == 2):
                glyph = unichr(ord(self.startGlyph) + glyphIdx)
            else:
                glyph = chr(ord(self.startGlyph) + glyphIdx)
            addText(templLayer, glyph, posX, posY, self.textStyle)
            
        return None

    def effect(self):
        #TODO: Maybe validate if a template was already created
        rowCnt = self.options.rowCnt
        srcFontFamily = self.options.srcFontFamily
        fontType = self.options.fontType
        glyphCnt = self.options.glyphCnt
        rvGuides = self.options.rvGuides
        fontSize = self.options.fontSize
        spaceWidth = self.options.spaceWidth
        
        self.createTTGlyphs = self.options.createGlyphs
        sg = self.options.startGlyph
        self.startGlyph = None
        if(len(sg) > 0):
            if(len(sg) == 4):
                try: self.startGlyph = eval("u'\\u" + sg + "'")
                except: pass
            if(self.startGlyph == None):
                self.startGlyph = getDecodedChars(sg)[0]
        else:
            self.startGlyph = 'A'

        lineT = CommonDefs.lineT * fontSize

        if('bold' in fontType):
            fontWeight = 'bold'
        else:
            fontWeight = 'normal'
            
        if('italic' in fontType):
            fontStyle = 'italic'
        else:
            fontStyle = 'normal'
        
        self.textStyle = {'font-family':srcFontFamily, 'font-size':str(fontSize),\
        'fill':'#e6e6e6', 'fill-opacity':'.5', 'stroke':'#000000', 'stroke-width':str(lineT),\
        'stroke-opacity':'.6', 'font-style':fontStyle,'font-weight':fontWeight,\
        'text-align':'start'}

        vgScaleFact = CommonDefs.vgScaleFact

        fontName = 'NA'

        extraInfo = getDefaultExtraInfo(fontName, fontSize)
        extraInfo[xSpaceROff] = spaceWidth

        createTempl(self.addElem, self, extraInfo, rowCnt, glyphCnt, vgScaleFact, \
            rvGuides, lineT)
    
runEffect(CustStrokeFontTempl())
