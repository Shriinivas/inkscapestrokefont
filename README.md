# Inkscape Extensions to Create Custom Stroke Fonts and Render Text Using Them
The extensions provided here extend the functionality of the Hershey Text Effect
(Copyright 2011, Windell H. Oskay, www.evilmadscientist.com) to allow the users
to create their own fonts (including non-english ones) and render text using them. 

# Installation
Download inkscapestrokefont.zip and extract all its contents in the Inkscape user extension folder. 
The extension folder can be found from the System option in Edit->Preference dialog. <br>
You will need to restart Inkscape.

# Usage
After installation, the extensions appear under a new sub-menu 'Custom Stroke Font' under Extensions menu of inkscape.<br><br>
<b>Rendering Text<br></b>
![Demo](https://github.com/Shriinivas/inkscapestrokefont/blob/master/strokefontrender.gif)
To render a text string using the custom stroke fonts, use the Render Text extension. There are a number of options to taylor the rendering. <br>
To have an aligned text, create rectangle(s) and select it (them) before invoking the render text tool. Now check the 'Flow Text in Boxes' and select horizontal and vertical alignment options. If the 'Create Extended Rectangles' option has a value oher than 'None' and if the text does not fit the given set of rectangles, then new rectangles will be created in the selected direction to fit the entire text.<br>
It's possible to render an entire text file in stroke font with the 'Render text from file' option. For large files, however, it might take considerable time for rendering. The resulting file size may also become quite large, since path of every letter is stored separately.<br>
The extensions come with 3 pre-designed custom fonts. The existing Hershey Text fonts are also ported to the format required for these extensions. These fonts are available in the Render Text tool with prefix 'Hershey'.<br><br>
<b>Designing New Fonts<br> </b>
To create your own font you need to first create a template invoking 'Create Font Design Template' extension.
Then design the fonts with reference to the guides in the template. Each designed glyph should be a single SVG path 
(if there are multiple segments they need to be combined in a single path). The path should have the XML ID same as the 
character text. So A glyph representing A should have its ID set to 'A' (without quotes). <br>
You can duplicate the guides within the template to define new reference lines if that helps designing the font (example ScriptLastNodeOffset.svg and ScriptGlyphsAlignedWithEditExt.svg). But bear in mind, only the guides created by the Create Font Design Template extension will be used to calculate the offsets.<br><br>
After completing the design the 'Generate Font Data' extension needs to be invoked to store the path data of the 
glyphs. The glyphs of a font are stored in an XML file in strokefontdata subfolder within the user extensions folder. The name of the file is the same as the font name, so the font names have all the restrictions that are applicable to file names. If the xml for the given font exists, the glyphs are added to it (or replaced if there exist any with the same IDs), if not a new xml file is created. <br>
Glyphs can be designed incrementally and can have different templates. <br><br>
<b>Editing Stroke Font<br></b>
Invoke Edit Stroke Font extension to edit an existing font. Choose the font to be edited from the drop down, and enter the number of rows and size. All the stroke font glyphs of the selected font are displayed in the given size, arranged in rows with row count corresponding to the user entered number. You can edit the path of the glyphs. The IDs are already set. If you want to create a new glyph reusing paths of an existing one, just give it the ID corresponding to the new glyph after editing.<br>
To save the edited font invoke the Generate Font Data extension and (re)enter the exact font name. The Right Offset option value should always be Vertical Guide / Bounding box. The data generation process is the same as that for new fonts.<br> <br> 

The <b>Synchronize Font List</b> extension should be used to synchronize the font list with the list of font data files (if the folder contents are changed externally)<br>

<b>Sample Font Files<br></b>
Please refer to the SVGs in the fontsvg folder for sample font design. The three bundled  fonts use the same SVGs to 
generate the font data. <br><br>

<b>Video Tutorials<br></b> 
Part1: https://youtu.be/iCsnYlVjWA0 <br>
Part2: https://youtu.be/-7BjfxpUAfU <br>
Part3: https://youtu.be/3YBaZfPpNjc <br>


# Credits
The custom stroke fonts are derived from: Square Grotesk and Pinyon Script available under Open Font License on https://fontlibrary.org/<br><br>
The Hershey Fonts are ported from hersheydata.py from Windell H. Oskay.<br>
Here's the acknowledgement:
- The Hershey Fonts were originally created by Dr. A. V. Hershey while working at the U. S. National Bureau of Standards.
- The format of the Font data in this distribution was originally created by<br>
James Hurt<br>
Cognition, Inc.<br>
900 Technology Park Drive<br>
Billerica, MA 01821<br>
(mit-eddie!ci-dandelion!hurt)<br>

# Known Issues & Workarounds
- With the non-english characters, the Generate Font Data extension may produce an error. The workaround is: save the file,
re-open it and generate the data once again.<br>
- If you are using Inkscape on windows, there could be problems rendering extended (e.g. non-english) characters (like ö or ß) with the text keyed in the input text box. A workaround is to create a text file with the text containing these characters and render the text using, 'Render from file' option. <br>
- If you are using Inkscape on windows, an extended (e.g. non-English) character in the First Glyph of Create Font Design Template extension may not work right. In such cases, you can enter the 4 digit hex unicode value of the first character (e.g. 00C0 for À) in the First Glyph field. You will get the unicode values of the characters from the Character Map.<br>
- Currently there is no user interface for deleting or renaming the fonts. This can be done manually by deleteting or renaming the xml file in the strokefontdata folder followed by synchronization of the font list<br>

Please exercise caution while using the tools; save your work, before invoking any of these extensions.<br>
You may report the issues and defects on the Issues page here or in the comments section on the video tutorial.<br>
Feedback and suggestions are most welcome!
