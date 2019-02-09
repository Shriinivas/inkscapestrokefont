#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Inkscape extension to synchronize the stroke font list with the generated data.

This effect updates the inx file of the effect that renders the text with the fonts 
from the data file.

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

import inkex, os, sys
from xml.dom.minidom import parse

sys.path.append(os.path.dirname(os.path.abspath(__file__))) 
from stroke_font_common import syncFontList, CommonDefs

class SyncFontListEffect(inkex.Effect):

    def __init__(self):
        inkex.Effect.__init__(self)

    def effect(self):
        dataFilePath = os.path.dirname(os.path.abspath(__file__)) + "/" + CommonDefs.dataFileName
        syncFontList(parse(dataFilePath))

effect = SyncFontListEffect()
effect.affect()
