#
#
# This module is used commonly by the Inkscape extension and the Blender add-on
# that render the stroke font text
#
# Copyright (C) 2019  Shrinivas Kulkarni
#
# License: MIT
#
# Not yet pep8 compliant

import os, re, sys
from xml.dom.minidom import parse, Document, getDOMImplementation

dataFileSubdir = 'strokefontdata'

##### XML Data Constants ########
xDefs = 'defs'
xFont = 'font'
xFontId = 'id'
xFontFace = 'font-face'
xFontFamily = 'font-family'
xCRInfo = 'metadata'
xSize = 'units-per-em'
xSpaceROff = 'horiz-adv-x'
xChar = 'unicode'
xROff = 'horiz-adv-x'
xGlyph = 'glyph'
xPath = 'd'
xMissingGlyph = 'missing-glyph'
xGlyphName = 'glyph-name'

xAscent='ascent'
xDescent = 'descent'
xCapHeight = 'cap-height'
xXHeight = 'x-height'


def getFontNames(parentPath):
    dataFileDirPath = parentPath + '/' + dataFileSubdir
    return sorted([fname[:-4] for fname in os.listdir(dataFileDirPath)
                   if fname.endswith('.svg')], key=lambda s: s.lower())

def getDefaultExtraInfo(fontName, fontSize):
    info = {}
    info[xAscent] = 0.8 * fontSize
    info[xDescent] = -0.2 * fontSize
    info[xCapHeight] = 0.5 * fontSize
    info[xXHeight] = 0.3 * fontSize
    info[xSpaceROff] = 0.5 * fontSize
    info[xFontId] = ''.join(fontName.split(' '))
    info[xSize] = fontSize
    return info


class CharData(object):
    def __init__(self, char, rOffset, glyphName = ''):
        self.char = char
        self.rOffset = rOffset
        self.bbox = self.getBBox() # Abstract
        self.glyphName = glyphName if glyphName != '' else char


class FontData:
    def __init__(self, parentPath, fontName, fontSize, charDataFactory):
        dataFileDirPath = parentPath + '/' + dataFileSubdir
        self.dataFilePath = dataFileDirPath + '/' + fontName + '.svg'
        self.fontName = fontName
        self.glyphMap = {}
        self.fontSize = fontSize
        self.spaceWidth = fontSize / 2
        self.crInfo = ''
        fontDefs = None
        self.charDataFactory = charDataFactory

        if(not os.path.isdir(dataFileDirPath)):
            os.makedirs(dataFileDirPath)

        try:
            with open(self.dataFilePath, encoding="UTF-8") as xml:
                dataDoc = parse(xml)
            fontDefs = dataDoc.getElementsByTagName(xDefs)[0]
        except Exception as e:
            pass

        if(fontDefs is not None):
            fontFaceElem = fontDefs.getElementsByTagName(xFontFace)[0]
            fontElem = fontDefs.getElementsByTagName(xFont)[0]

            crElem = dataDoc.getElementsByTagName(xCRInfo)[0]
            if(len(crElem.childNodes) > 0):
                self.crInfo = crElem.childNodes[0].nodeValue

            self.fontName = fontFaceElem.getAttribute(xFontFamily)
            oldFontSize = float(fontFaceElem.getAttribute(xSize))

            info = {}

            try:
                info[xSize] = oldFontSize
                info[xFontId] = fontElem.getAttribute(xFontId)
                info[xAscent] = float(fontFaceElem.getAttribute(xAscent))
                info[xDescent] = float(fontFaceElem.getAttribute(xDescent))
                info[xCapHeight] = float(fontFaceElem.getAttribute(xCapHeight))
                info[xXHeight] = float(fontFaceElem.getAttribute(xXHeight))
                info[xSpaceROff] = float(fontElem.getAttribute(xSpaceROff))
            except Exception as e:
                # ~ inkex.errormsg(str(e))
                info = getDefaultExtraInfo(self.fontName, oldFontSize)

            glyphElems = fontDefs.getElementsByTagName(xGlyph)
            for e in glyphElems:
                char = e.getAttribute(xChar)
                rOffset = float(e.getAttribute(xROff))
                glyphName = e.getAttribute(xGlyphName)
                if(glyphName == 'space'):
                    info[xSpaceROff] = rOffset
                else:
                    pathStr = e.getAttribute(xPath)
                    if(pathStr != None and pathStr.strip() != ''):
                        charData = charDataFactory.getCharData(char, rOffset, pathStr, glyphName)

                        scaleFact = fontSize / oldFontSize
                        charData.scaleGlyph(scaleFact, -scaleFact)

                        self.glyphMap[char] = charData

            self.extraInfo = {}
            for key in info:
                if(isinstance(info[key], float) or isinstance(info[key], int)):
                    self.extraInfo[key] = fontSize * info[key] / oldFontSize
                else:
                    self.extraInfo[key] = info[key]

            self.spaceWidth = self.extraInfo[xSpaceROff]
        else:
            self.extraInfo = getDefaultExtraInfo(self.fontName, self.fontSize)

    def updateGlyph(self, char, rOffset, pathStr, glyphName):
        charData = self.charDataFactory.getCharData(char, rOffset, pathStr, glyphName)
        self.glyphMap[char] = charData

    def setCRInfo(self, crInfo):
        if(crInfo is not None and crInfo != ''):
            self.crInfo = crInfo

    def setExtraInfo(self, extraInfo):
        self.extraInfo = extraInfo

    def hasGlyphs(self):
        return len(self.glyphMap) > 0

    # invertY = True because glyph was inverted in FontData constructor
    def updateFontXML(self, invertY = True):
        imp = getDOMImplementation()
        doctype = imp.createDocumentType('svg', "-//W3C//DTD SVG 1.1//EN", \
            "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd")
        doc = imp.createDocument(None, 'svg', doctype)
        docElem = doc.documentElement
        docElem.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        docElem.setAttributeNS("xmls", "xmlns:xlink", "http://www.w3.org/1999/xlink")
        docElem.setAttribute("version", "1.1")

        fontDefs = doc.createElement(xDefs)
        docElem.appendChild(fontDefs)

        info = self.extraInfo
        spaceWidthStr = str(info[xSpaceROff])

        fontElem = doc.createElement(xFont)
        fontElem.setAttribute(xSpaceROff, spaceWidthStr)
        fontElem.setAttribute(xFontId, self.fontName)
        fontDefs.appendChild(fontElem)

        fontFaceElem = doc.createElement(xFontFace)
        fontFaceElem.setAttribute(xFontFamily, self.fontName)
        fontFaceElem.setAttribute(xSize, str(self.fontSize))
        fontFaceElem.setAttribute(xAscent, str(info[xAscent]))
        fontFaceElem.setAttribute(xDescent, str(info[xDescent]))
        fontFaceElem.setAttribute(xCapHeight, str(info[xCapHeight]))
        fontFaceElem.setAttribute(xXHeight, str(info[xXHeight]))

        fontElem.appendChild(fontFaceElem)

        crElem = doc.createElement(xCRInfo)
        docElem.appendChild(crElem)

        if (self.crInfo != ''):
            crElem.appendChild(doc.createTextNode(self.crInfo))

        missingGlyphElem = doc.createElement(xMissingGlyph)
        missingGlyphElem.setAttribute(xROff, spaceWidthStr)
        fontElem.appendChild(missingGlyphElem)

        glyphElem = doc.createElement(xGlyph)
        glyphElem.setAttribute(xChar, ' ')
        glyphElem.setAttribute(xGlyphName, 'space')
        glyphElem.setAttribute(xROff, spaceWidthStr)
        fontElem.appendChild(glyphElem)

        for char in self.glyphMap:
            charData = self.glyphMap[char]
            if(invertY): charData.scaleGlyph(1, -1)
            glyphElem = doc.createElement(xGlyph)

            glyphElem.setAttribute(xChar, char)
            glyphElem.setAttribute(xGlyphName, charData.glyphName)
            glyphElem.setAttribute(xPath, charData.pathStr)
            glyphElem.setAttribute(xROff, str(charData.rOffset))

            fontElem.appendChild(glyphElem)

        with open(self.dataFilePath, "w", encoding="UTF-8") as f:
            xmlStr = doc.toxml(encoding="UTF-8")
            if(sys.version_info.major == 3): xmlStr = xmlStr.decode("UTF-8")
            f.write(xmlStr)


class DrawContext:

    #bottomToTop flag indicates y increases from bottom towards top (e.g. in Blender)
    def __init__(self, parentPath, fontName, fontSize, charSpacing, wordSpacing,
                 lineSpacing, charDataFactory, renderer, bottomToTop = False):
        self.charSpacing = charSpacing
        self.lineSpacing = lineSpacing
        self.renderer = renderer
        self.bottomToTop = bottomToTop
        self.yCoeff = -1 if(bottomToTop) else 1

        self.strokeFontData = FontData(parentPath, fontName, fontSize, charDataFactory)

        self.spaceWidth = self.strokeFontData.spaceWidth * wordSpacing
        self.lineHeight = fontSize * lineSpacing

    def fontHasGlyphs(self):
        return self.strokeFontData.hasGlyphs()

    def getCharData(self, char):
        cd = self.strokeFontData.glyphMap.get(char)

        if(cd is None):
            naMargin = self.strokeFontData.fontSize * .1
            naSize = self.strokeFontData.fontSize * .5
            naOffset = (naSize + naMargin * 2)

            naPathStr = 'M ' + str(naMargin) + ',' + str(0) + ' h ' + \
                str(naSize) + ' v ' + str(-1 * self.yCoeff * naSize) + \
                    ' h ' + str(-1 * naSize) + ' Z'

            cd = self.strokeFontData.charDataFactory.getCharData(char, \
                naOffset, naPathStr, 'na')

            cd.bbox = [naMargin, naMargin + naSize, -1 * self.yCoeff * naSize, 0]

        return cd

    def getLineTopY(self, spaceWordData):
        topY = 0

        wordData = [c for w in spaceWordData if (w[1] is not None) for c in w[1]]

        for i, c in enumerate(wordData):
            # Reverse the comparison if y increases from bottom to top
            if (i == 0 or (self.yCoeff * c.bbox[2] < self.yCoeff * topY)):
                topY = c.bbox[2]

        return topY

    def getLineBottomY(self, spaceWordData):
        bottomY = 0

        wordData = [c for w in spaceWordData if (w[1] is not None) for c in w[1]]

        for i, c in enumerate(wordData):
            # Reverse the comparison if y increases from bottom to top
            if (i == 0 or self.yCoeff * c.bbox[3] > self.yCoeff * bottomY):
                bottomY = c.bbox[3]

        return bottomY

    # Calculate the width distribution among spaces for justified alignment
    # The apportioned width is proportional to word length and width of
    # preceding spaces
    def getDistWidths(self, spaceWordData, x, xRight):

        totalLineLen = self.getWordLineLen(spaceWordData)

        # Extra space to be distributed
        extra = xRight - x - totalLineLen

        # Total length to be considered
        llen = totalLineLen
        start = 0
        eLens = []

        if(spaceWordData[0][0] == 0):
            # Subtract the first word length as it's not considered in calculation
            # (spaces start after it)
            llen -= self.getWordLen(spaceWordData[0][1])
            start = 1
            eLens.append(0)

        for i in range(start, len(spaceWordData)):
            sw = spaceWordData[i]
            eL = sw[0] * self.spaceWidth + self.getWordLen(sw[1])
            eLens.append(eL * extra / llen)

        return eLens

    # In case a single word length is greater than rect width,
    # need to split it
    def splitWord(self, wordData, rectw):
        wordComps = []
        comp1 = wordData

        while(len(comp1) > 0 and self.getWordLen(comp1) > rectw):
            comp2 = []
            while(len(comp1) > 0 and self.getWordLen(comp1) > rectw):
                comp2.insert(0, comp1.pop())

            # Rectangle can't even fit a single letter
            if(len(comp1) == 0):
                break

            wordComps.append(comp1)
            comp1 = comp2

        wordComps.append(comp1)
        return wordComps

    # Word boundary is bbox minX of first letter upto bbox maxX of last
    # with charSpace * rOffsets dist between the chars in between
    def drawWordWithLenCalc(self, wordData, render=False, x=0, y=0):
        if(wordData is None or len(wordData) == 0):
            return 0

        nextX = x

        for i, charData in enumerate(wordData):
            # Always start from bbox minX of the first letter
            if(i == 0):
                nextX -= charData.bbox[0]

            if(render):
                naChar = self.strokeFontData.glyphMap.get(charData.char) is None
                self.renderer.renderChar(charData, nextX, y, naChar)

            xmax = charData.bbox[1]

            # Possible that a char other than the last one ends after it
            # Extreme case: charSpacing = 0
            if(i == 0 or nextX + xmax > maxLen):
                maxLen = nextX + xmax

            nextX += charData.rOffset * self.charSpacing

        # Calculate getWordLen separately because of last and first char
        # exceptions
        return maxLen

    def getWordLen(self, wordData):
        return self.drawWordWithLenCalc(wordData)

    def drawWord(self, x, y, wordData):
        return self.drawWordWithLenCalc(wordData, True, x, y)

    # Length of line of words, includes trailing spaces
    def getWordLineLen(self, spaceWordData):
        if(spaceWordData is None or len(spaceWordData) == 0):
            return 0

        wlLen = 0
        cnt = len(spaceWordData)

        # If last word is None, there are trailing spaces, consider their
        # length
        if(spaceWordData[-1][1] is None):
            cnt -= 1
            wlLen = spaceWordData[-1][0] * self.spaceWidth

        # spaceWordData is word and the length of its preceding spaces
        for i in range(0, cnt):
            sw = spaceWordData[i]
            wlLen += sw[0] * self.spaceWidth
            wlLen += self.getWordLen(sw[1])

        return wlLen

    def drawWordLine(self, spaceWordData, x, y, xRight, alignment):
        lineLen = self.getWordLineLen(spaceWordData)

        if(alignment == 'right'):
            x = xRight - lineLen
        elif(alignment == 'center'):
            x += (xRight - x - lineLen) / 2
        elif(alignment == 'justified'):
            eLens = self.getDistWidths(spaceWordData, x, xRight)

        nextX = x
        for i, sw in enumerate(spaceWordData):

            nextX += sw[0] * self.spaceWidth

            if(alignment == 'justified'):
                nextX += eLens[i]

            nextX = self.drawWord(nextX, y, sw[1])

        return nextX

    # the chars must end with \n
    def renderCharsInBox(self, chars, xLeft, yTop, xRight, yBottom, hAlignment, vAlignment):

        spaceWordData = []
        wordData = []
        procCharsIdx = 0
        x = xLeft
        y = yTop
        yTextBottom = yTop

        for i, char in enumerate(chars):
            if(char != ' ' and char != '\n'):
                charData = self.getCharData(char)
                wordData.append(charData)
                continue

            # At this point, wordData will have accumulated chars before this space/newline
            # Last element of spaceWordData will have spacewidths to be inserted before
            # this word data
            if(len(wordData) > 0):
                wLen = self.getWordLen(wordData)

                # Includes trailing spaces
                prevLineLen = self.getWordLineLen(spaceWordData)

                if(x + prevLineLen + wLen > xRight):

                    trailingSpaces = 0
                    if(len(spaceWordData) > 0 and spaceWordData[-1][1] is None):
                        trailingSpaces = spaceWordData.pop()[0]

                    # Create an array in case this single word is bigger than rect width,
                    # so that all chunks can be drawn here itself
                    # Most likely this array will contain only the line
                    # accumulate before this word
                    spaceWordDataArr = []

                    # Exhaust the line with the previous words first
                    if(len(spaceWordData) > 0):
                        spaceWordDataArr.append(spaceWordData)

                    # This single word is longer than the rect width can fit
                    if(x + wLen > xRight):
                        wordComps = self.splitWord(wordData, (xRight - x))

                        # Not even a single letter fits, so return
                        if(len(wordComps) == 1):
                            return yTextBottom, chars[procCharsIdx:]

                        # Add all the chunks, each on a new line
                        spaceWordDataArr += [[[0, wordComps[k]]]
                                             for k in range(0, len(wordComps) - 1)]

                        wordData = wordComps[-1]

                    # Draw as many lines as there are elements in the
                    # spaceWordDataArr
                    while(len(spaceWordDataArr) > 0):
                        spaceWordData = spaceWordDataArr.pop(0)
                        if(len(spaceWordData) > 0):

                            #TODO repetition(1)
                            # If the first line, align its top edge along the rect top
                            if(y == yTop):
                                y -= self.getLineTopY(spaceWordData)

                            lineBottom = (y + self.getLineBottomY(spaceWordData))

                            if(self.yCoeff * lineBottom > self.yCoeff * yBottom):
                                return yTextBottom, chars[procCharsIdx:]

                            self.drawWordLine(spaceWordData, x, y, xRight, hAlignment)

                            yTextBottom = lineBottom

                            # Shift marker for processed chars
                            procCharsIdx = i - \
                                sum(len(wd[0][1]) for wd in spaceWordDataArr) - len(wordData)

                            # This has to be repeated for 2 diff conditions,
                            # Complications not worth it.. so commenting out
                            # (Just ignore long sequence of trailing spaces for now)
                            # ~ if(x + trailingSpaces * self.spaceWidth > xRight \
                            # ~ and len(spaceWordDataArr) > 0):
                            # ~ y += self.lineHeight

                            trailingSpaces = 0
                            y += self.yCoeff * self.lineHeight

                    spaceWordData = [[0, wordData]]
                else:
                    if(len(spaceWordData) == 0):
                        spaceWordData = [[0, wordData]]
                    else:
                        spaceWordData[-1][1] = wordData

                wordData = []

            if(char == ' '):
                if(len(spaceWordData) == 0 or spaceWordData[-1][1] is not None):
                    spaceWordData.append([1, None])
                else:
                    spaceWordData[-1][0] += 1

            elif(char == '\n'):
                # Don't consider trailing spaces if hard new line
                if(len(spaceWordData) > 0 and spaceWordData[-1][1] is None):
                    spaceWordData.pop()

                if(len(spaceWordData) > 0):
                    #TODO repetition(2)
                    if(y == yTop):
                        y -= self.getLineTopY(spaceWordData)

                    lineBottom = (y + self.getLineBottomY(spaceWordData))

                elif(vAlignment == 'none'):
                    lineBottom = (y + self.yCoeff * self.lineHeight)
                else:
                    lineBottom = yTextBottom #Get from the previous text line

                if(self.yCoeff * lineBottom > self.yCoeff * yBottom):
                    return yTextBottom, chars[procCharsIdx:]

                if(len(spaceWordData) > 0):
                    self.drawWordLine(spaceWordData, x, y, xRight, hAlignment
                                      if hAlignment != 'justified' else 'left')
                    yTextBottom = lineBottom

                if(vAlignment == 'none' or len(spaceWordData) > 0):
                    y += self.yCoeff * self.lineHeight

                procCharsIdx = i

                spaceWordData = []

        return yTextBottom, None

    def renderCharsWithoutBox(self, chars):

        if(chars is None or len(chars) == 0):
            return

        x, y = self.renderer.getDefaultStartLocation()
        xRight = sys.float_info.max

        regex = re.compile('([ ]*)([^ ]+)')
        lines = chars.split('\n')

        wmax = 0
        hmax = 0

        self.renderer.beforeRender()

        for line in lines:
            res = regex.findall(line)
            spaceWordData = []
            for r in res:
                wordData = [self.getCharData(cd) for cd in r[1]]
                spaceWordData.append([len(r[0]), wordData])

            xr = self.drawWordLine(
                spaceWordData, x, y, xRight, alignment='left')

            if(xr > wmax):
                wmax = xr

            y += self.yCoeff * self.lineHeight

        self.renderer.centerInView(wmax / 2, y / 2)

    #Remove newline chars if alignment is not none
    def preprocess(self, chars, vAlignment, isFirstLine):
        newLine = False

        while(chars.startswith('\n')):
            newLine = True
            if(vAlignment != 'none'):
                chars = chars[1:]
            else:
                break

        # Retain leading spaces in case of newline ending and the very
        # first line of the text
        if(not newLine and not isFirstLine):
            chars = chars.strip()

        #required for the processing function
        if(not chars.endswith('\n')):
            chars += '\n'

        return chars

    def renderCharsInSelBoxes(self, chars, rectangles, margin, hAlignment, vAlignment, \
        addPlane = False, expandDir = None, expandDist = None):

        self.renderer.beforeRender()
        i = 0

        while(chars != None):
            if(i < len(rectangles)):
                box = rectangles[i]
            elif(expandDir != None and expandDist != None):
                x1, y1, x2, y2 = self.renderer.getBoxLeftTopRightBottom(rectangles[-1])
                w = abs(x2 - x1)
                h = abs(y2 - y1)

                if(expandDir == 'x'):
                    x1 += w + expandDist
                    x2 += w + expandDist
                elif(expandDir == 'y'):
                    y1 += self.yCoeff * (h + expandDist)
                    y2 += self.yCoeff * (h + expandDist)
                #TODO: Neat hadling for 2d rendering
                elif(expandDir == 'z'):
                    self.renderer.z += expandDist
                box = self.renderer.getBoxFromCoords(x1, y1, x2, y2)
                rectangles.append(box)
            else:
                break

            if(len(chars) == 0):
                return

            self.renderer.newBoxToBeRendered(box, addPlane)

            x1, y1, x2, y2 = self.renderer.getBoxLeftTopRightBottom(box)

            xLeft = x1 + margin
            yTop = y1 + self.yCoeff * margin

            xRight = x2 - margin
            yBottom = y2 - self.yCoeff * margin

            chars = self.preprocess(chars, vAlignment, (i == 0))
            lenCharsBeforeProc = len(chars)

            yTextBottom, chars = self.renderCharsInBox(chars, xLeft, yTop, \
                xRight, yBottom, hAlignment, vAlignment)

            if(vAlignment == 'center'):
                moveBy = (yBottom - yTextBottom) / 2
                self.renderer.moveBoxInYDir(moveBy)
            elif(vAlignment == 'bottom'):
                moveBy = yBottom - yTextBottom
                self.renderer.moveBoxInYDir(moveBy)

            if(chars is None or \
                (lenCharsBeforeProc == len(chars) and (len(rectangles)-1) == i)):
                return

            i += 1

    def renderGlyphTable(self):
        self.renderer.beforeRender()

        xStart, y = self.renderer.getDefaultStartLocation()
        x = xStart

        chars = [c for c in self.strokeFontData.glyphMap.keys()]
        chars = sorted(chars)

        text = "Font: " + self.strokeFontData.fontName
        self.renderer.renderPlainText(
            text, self.strokeFontData.fontSize, x, y, 'Font Name')

        y += self.yCoeff * self.strokeFontData.fontSize

        crInfoTxt = self.strokeFontData.crInfo

        maxStrSize = 100

        infoLines = crInfoTxt.split('\n')
        for line in infoLines:
            while(line != ""):
                crInfo = line[:maxStrSize]
                line = line[maxStrSize:]
                if(crInfo[-1].isalpha() and len(crInfoTxt) > 0 and crInfoTxt[0].isalpha()):
                    crInfo += '-'
                self.renderer.renderPlainText(
                    crInfo, self.strokeFontData.fontSize / 2, x, y, 'CR Info')

                y += self.yCoeff * self.strokeFontData.fontSize
        y += self.yCoeff * .5 * self.strokeFontData.fontSize

        hCnt = 10
        letterSpace = self.strokeFontData.fontSize * 2

        for i, char in enumerate(chars):
            if(i % hCnt == 0):
                x = xStart
                if(i > 0):
                    y += self.yCoeff * self.lineHeight
            self.renderer.renderPlainText(char, self.strokeFontData.fontSize / 2, x, y, char)
            x += letterSpace / 3
            self.drawWord(x, y, [self.getCharData(char)])
            x += letterSpace

        width = letterSpace * hCnt / 2
        height = y / 2
        self.renderer.centerInView(width, height)
