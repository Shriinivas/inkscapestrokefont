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

from inkex import Effect, etree, addNS, NSS
from math import ceil
from simplestyle import formatStyle
from stroke_font_common import CommonDefs

class CustStrokeFontTempl(Effect):

    def __init__(self):
        Effect.__init__(self)

        self.OptionParser.add_option('--rowCnt', action = 'store',
          type = 'int', dest = 'rowCnt', default = '5',
          help = 'Number of rows (horizontal guides) in the template')

        self.OptionParser.add_option("--createGlyphs",
            action="store", type="inkbool", dest="createGlyphs", default=True,
          help = 'Render glyphs of the source font family for tracing ')

        self.OptionParser.add_option('--srcFontFamily', action = 'store',
          type = 'string', dest = 'srcFontFamily', 
          help = 'Exact name of the source font family')

        self.OptionParser.add_option('--srcFontSize', action = 'store',
          type = 'int', dest = 'srcFontSize', default = '100',
          help = 'Size of the source glyphs to be rendered')

        self.OptionParser.add_option('--fontType', action = 'store',
          type = 'string', dest = 'fontType', default = 'normal',
          help = 'Font Style')

        self.OptionParser.add_option('--startGlyph', action = 'store',
          type = 'string', dest = 'startGlyph', default = '0',
          help = 'Starting glyph to be rendered')

        self.OptionParser.add_option('--glyphCnt', action = 'store',
          type = 'int', dest = 'glyphCnt', default = '75',
          help = 'Number of template glyphs')

        self.OptionParser.add_option("--rvGuides",
            action="store", type="inkbool", dest="rvGuides", default=False, 
                help = 'Render vertical guide at the right of each glyph')

        self.OptionParser.add_option("--tab", action="store", 
          type="string", dest="tab", default="sampling", help="Tab") 
          
    def addGridLine(self, layer, posX, posY, length, lType, style, attribs):        
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
        
    def addText(self, layer, textStr, posX, posY, style):
        text = etree.Element(addNS('text','svg'))
        text.text = textStr 

        text.set('x', str(posX))
        text.set('y', str(posY))

        text.set('style', formatStyle(style))

        layer.append(text)
        

    def effect(self):

        rowCnt = self.options.rowCnt
        createGlyphs = self.options.createGlyphs
        srcFontFamily = self.options.srcFontFamily
        fontType = self.options.fontType
        glyphCnt = self.options.glyphCnt
        rvGuides = self.options.rvGuides
        srcFontSize = self.options.srcFontSize
        
        if(len(self.options.startGlyph) > 0):
            startGlyph = unicode(self.options.startGlyph, 'utf-8')[0]
        else:
            startGlyph = 'A'

        lineT = .1
        
        if('bold' in fontType):
            fontWeight = 'bold'
        else:
            fontWeight = 'normal'
            
        if('italic' in fontType):
            fontStyle = 'italic'
        else:
            fontStyle = 'normal'
        
        hgStyle = {'stroke-width':str(lineT), 'opacity':'1', 'stroke':'#ff0066'}
        lvgStyle = {'stroke-width':str(lineT), 'opacity':'1', 'stroke':'#00aa88'}
        rvgStyle = {'stroke-width':str(lineT), 'opacity':'1', 'stroke':'#1b46ff'}
        textStyle = {'font-family':srcFontFamily, 'font-size':str(srcFontSize),\
        'fill':'#e6e6e6', 'fill-opacity':'.5', 'stroke':'#000000', 'stroke-width':str(lineT),\
        'stroke-opacity':'.6', 'font-style':fontStyle,'font-weight':fontWeight,\
        'text-align':'start'}
        
        vgScaleFact = CommonDefs.vgScaleFact

        spcY = srcFontSize * 3
        spcX = srcFontSize * 3
        vLineH = srcFontSize * vgScaleFact

        colCnt = int(ceil(float(glyphCnt) / float(rowCnt)))

        docW = (colCnt + 1) * spcX
        docH = (rowCnt + 1) * spcY

        svg = self.document.getroot()
        svg.set('width', str(docW))
        svg.set('height', str(docH))
        
        #Remove viewbox
        if('viewBox' in svg.attrib):
            svg.attrib.pop('viewBox')
        
        templLayer = etree.SubElement(svg, 'g')
        templLayer.set(addNS('label', 'inkscape'), 'Template')
        templLayer.set(addNS('groupmode', 'inkscape'), 'layer')
        
        gaName = CommonDefs.guideAttribName
        
        lvAttribs = {gaName: CommonDefs.lvGuideAttrib}
        rvAttribs = {gaName: CommonDefs.rvGuideAttrib}
        hAttribs = {gaName:CommonDefs.hGuideAttrib}
        
        hSeqAName = CommonDefs.hSeqAttribName
        vSeqAName = CommonDefs.vSeqAttribName
        
        for row in range(0, rowCnt):
            hAttribs[hSeqAName] = str(row)
            self.addGridLine(templLayer, 0, \
                (row + 1) * spcY, docW, 'H', hgStyle, hAttribs)

            lvAttribs[hSeqAName] = str(row)
            rvAttribs[hSeqAName] = str(row)
            
            for col in range(0, colCnt):
                glyphIdx = row * colCnt + col
                if(glyphIdx >= glyphCnt):
                    break
                    
                posX = (col + 1) * spcX  
                posY = (row + 1) * spcY + lineT / 2

                if(createGlyphs):
                    glyph = unichr(ord(startGlyph) + glyphIdx)
                    self.addText(templLayer, glyph, posX, posY, textStyle)
                    
                lvAttribs[vSeqAName] = str(col)
                self.addGridLine(templLayer, \
                    posX, posY + srcFontSize / 1.5, -vLineH, 'V', \
                        lvgStyle, lvAttribs)
                        
                if(rvGuides):
                    rvAttribs[vSeqAName] = str(col)
                    self.addGridLine(templLayer, \
                        posX + srcFontSize, posY + srcFontSize / 1.5, -vLineH, 'V', \
                            rvgStyle, rvAttribs)
            
effect = CustStrokeFontTempl()
effect.affect()
