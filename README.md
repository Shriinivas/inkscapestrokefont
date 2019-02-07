# Inkscape Extensions to Create Custom Stroke Fonts and Render Text Using Them
The extensions provided here extend the functionality of the Hershey Text Effect
(Copyright 2011, Windell H. Oskay, www.evilmadscientist.com) to allow the users
to create their own fonts (including non-english ones) and render text using them. 

# Installation
Download inkscapestrokefont.zip and extract all its contents in the Inkscape user extension folder. 
The extension folder can be found from the System option in Edit->Preference dialog. <br>
You will need to restart Inkscape.

# Usage
After installation, the extensions appear under a new menu 'Custom Stroke Font' under Extensions.<br>
To render a text string using the custom stroke fonts, use the Render Text extension. This is similar to Hershey Text
with some enhancements like rendering multiline text.<br>
The extensions come with 2 pre-designed custom fonts.

To create your own font you need to first create a template invoking 'Create Font Design Template' extension.
Then design the fonts with reference to the guides in the template. Each designed glyph should be a single SVG path 
(if there are multiple segments they need to be combined in a single path). The path should have the XML ID same as the 
character text. So A glyph representing A should have its ID set to 'A' (without quotes). <br><br>
After completing the design the 'Generate Font Data' extension needs to be invoked to store the path data of the 
glyphs. The glyphs are stored in an XML file (customstrokefontdata.xml). If the font name specified exists the new glyphs are added to it (or replaced
if there exist any with the same IDs), if not a new font with the given name is created. <br>
Glyphs can be designed incrementally and can have different templates. <br><br>

Please refer to the SVGs in the fontsvg folder for sample font design. The two bundled  fonts use the same SVGs to 
generate the font data. <br><br>

The Synchronize Font List extension should be used to synchronize the XML (if it has been changed externally)<br>

<b>Video Tutorial:</b> Detailed introduction to the tools can be found at: https://youtu.be/iCsnYlVjWA0

# Credits
The new stroke fonts are derived from: Square Grotesk and Pinyon Script available under Open Font License on https://fontlibrary.org/<br>

# Limitations
With the non-english characters, the Generate Font Data extension may produce an error. The work-around is to save the file,
re-open it and generate the data once again.<br>
Currently there is no user interface for deleting the fonts. This can be done manually by editing the XML and removing the font element.<br><br>
The tools are in alpha stage, so please exercise caution while using them. <br>
You may report the issues and defects on the Issues page here or in the comments section on the video tutorial.<br>
Feedback and suggestions are most welcome!
