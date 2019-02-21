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
To render a text string using the custom stroke fonts, use the Render Text extension. There are a number of options to taylor the rendering. <br>
To have an aligned text, create rectangle(s) and select it (them) before invoking the render text tool. Now check the 'Flow Text in Boxes' and select one of the alignment options.<br>
It's possible to render an entire text file in stroke font with the 'Render text from file' option. For large files, however, it might take considerable time for rendering. The resulting file size may also become quite large, since path of every letter is stored separately.<br>
The extensions come with 2 pre-designed custom fonts.<br><br>
<b>Designing New Fonts<br> </b>
To create your own font you need to first create a template invoking 'Create Font Design Template' extension.
Then design the fonts with reference to the guides in the template. Each designed glyph should be a single SVG path 
(if there are multiple segments they need to be combined in a single path). The path should have the XML ID same as the 
character text. So A glyph representing A should have its ID set to 'A' (without quotes). <br><br>
After completing the design the 'Generate Font Data' extension needs to be invoked to store the path data of the 
glyphs. The glyphs of a font are stored in an XML file in strokefontdata subfolder within the user extensions folder. The name of the file is the same as the font name, so the font names have all the restrictions that are applicable to file names. If the xml for the given font exists, the glyphs are added to it (or replaced if there exist any with the same IDs), if not a new xml file is created. <br>
Glyphs can be designed incrementally and can have different templates. <br><br>
<b>Sample Font Files<br></b>
Please refer to the SVGs in the fontsvg folder for sample font design. The two bundled  fonts use the same SVGs to 
generate the font data. <br><br>

The Synchronize Font List extension should be used to synchronize the font list with the list of font data files (if the folder contents are changed externally)<br>

<b>Video Tutorials<br></b> 
Detailed introduction: https://youtu.be/iCsnYlVjWA0 <br>
Enhancements Overview: https://youtu.be/-7BjfxpUAfU <br>

# Credits
The new stroke fonts are derived from: Square Grotesk and Pinyon Script available under Open Font License on https://fontlibrary.org/<br>

# Limitations
With the non-english characters, the Generate Font Data extension may produce an error. The work-around is: save the file,
re-open it and generate the data once again.<br>
If you are using windows, there could be problems rendering non-english characters (like ö or ß). A work-around is to create a text file with the text containing these characters and render the text using, 'Render from file' option. <br>
Currently there is no user interface for deleting or renaming the fonts. This can be done manually by deleteting or renaming the xml file in the strokefontdata folder followed by synchronization of the font list<br><br>
The tools are in alpha stage, so please exercise caution while using them. <br>
You may report the issues and defects on the Issues page here or in the comments section on the video tutorial.<br>
Feedback and suggestions are most welcome!
