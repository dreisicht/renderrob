# Render Rob

![ ](img/readme_pics/renderrob_deck_01.png)

Render Rob is an Google Spreadsheet based Render manager for Blender. It gives you the possiblilty to easily manage your jobs, and change the settings from the sheet for better overview. No need for command line fiddling anymore!

![](img/readme_pics/screenshot.jpg)

## Setup

### Spreadsheet

1. Open this Spreadsheet:
https://docs.google.com/spreadsheets/d/1ec6AT0q2bhoBhWivzLhM-wXOfM2kwrOK1VIMKbTqRrU/edit?usp=sharing

2. Make a copy into your Drive of the sheet

![Text](img/readme_pics/Anmerkung%202020-04-26%20101650.jpg "Descrp")


1. Name it `Render Rob`. Correct naming is important!

![Text](img/readme_pics/Anmerkung%202020-04-26%20101720.jpg "Descrp")

### Setting up Google api

1. Open up https://console.developers.google.com/, agree to terms and conditions and click on `Agree and continue`

![Text](img/readme_pics/Anmerkung%202020-04-26%20102222.jpg "Descrp")

2. Click on create project


![Text](img/readme_pics/Anmerkung%202020-04-26%20125300.jpg "Descrp")

1. Name the project e.g. Render Rob and click on create

![Text](img/readme_pics/Anmerkung%202020-04-26%20102359.jpg "Descrp")

4. Search for **Google Drive API** and enable it

![Text](img/readme_pics/Anmerkung%202020-04-26%20125343.jpg "Descrp")
![Text](img/readme_pics/Anmerkung%202020-04-26%20125407.jpg "Descrp")
<!-- ![Text](img/readme_pics/Anmerkung%202020-04-26%20102553.jpg "Descrp") -->

1. Same for **Google Sheets API**

![Text](img/readme_pics/Anmerkung%202020-04-26%20102550.jpg "Descrp")
![Text](img/readme_pics/Anmerkung%202020-04-26%20102636.jpg "Descrp")

1. Click on Create Credentials

![Text](img/readme_pics/Anmerkung%202020-04-26%20125536.jpg "Descrp")

1. fill out the form and click on `What credentials do I need?`

![Text](img/readme_pics/Anmerkung%202020-04-26%20102827.jpg "Descrp")

1. continue filling out

![Text](img/readme_pics/Anmerkung%202020-04-26%20102856.jpg "Descrp")

1. save the json file you get in the `Render Rob\Key` Folder

![Text](img/readme_pics/Anmerkung%202020-04-26%20102919.jpg "Descrp")

1. Copy the E-Mail Address from the json File and share the Spreadsheet with this mail

![Text](img/readme_pics/Anmerkung%202020-04-26%20104113.jpg "Descrp")


### Filling the Spreadsheet

After setting that up, fill in the global settings in the Sheet. The Blender Path and Render Path is mandatory, the rest is optional.

![Text](img/readme_pics/Anmerkung%202020-04-26%20134758.jpg)

Now you only have to paste your attributes of your job to be rendered, and run `renderrob.exe`!

## Features

Feature list google doc:

| Property | Usage |
|--- |:---|
| active | Activates or deactivates job |
| .blend file path | Path of blend file. Absolute path, aswell as relative path to file folder in globals is possible |
| camera | Name of camera to be activated, optional |
| start frame | First frame to be rendered|
| end frame | Last frame to be rendered|
| X res | Horizontal resolution |
| Y res | Vertical resolution|
| samples | Number of cycles or eevee passes|
| file format | Output file format. Exr refers to multilayer exr|
| cycles (eevee) | If activated, cycles is used, otherwise eevee|
| cpu | Usage of cpu for rendering |
| gpu | Usage of gpu for rendering |
| motion blur | Usage of Motion blur |
| read only | If activated, already rendered images don't get overwritten |
| place-holder | Creating placeholders of images being rendered |
| high-quality | If deactivated, preview settings from globals are used|
| animation denoise | Usage of Post-Process Animation Denoising|
| denoise | Usage of Image-Denoising|
| comments | Put your own comments of the shot here|

## Further explanations

- If you want to abort all renders, you have to close all three command-line windows.
- The reason motion blur is in Render Rob, is that I often experienced situations where motion blur had artefacts, so I needed few frames without it.
- Column t is necessary. Please do not delete it.
- Column a is a help for being able to select cells easier.
- If read only is enabled, a new folder with a new version number is created and used as render output.
- Jobs get rendered in the order, the are shown in the list. You can reorder them by drag-and-drop. Therefore select the line and drag it on the left side up or down.
- Border rendering gets disabled, if high quality is active.
- Currently the rendering of multiple scenes and view layers is not supported. You will get a warning and it will only render the first scene and the first view layer.
- You can put your own blender commands in the file called `rr_user_commands.py`. An example for this would be the activation of an addon.
- If you disable cycles (and by that enbale eevee), the irrelevant settings get disabled.

## Warnings in the sheet

If a property in the sheet gets marked yellow, this means, that a possible error is found. These are just warnings, so you still are able to start the job. In some cases it will work, in some it won't.
Following things are being looked at:

- Double occurences of jobs
- No render device selected
- Both devices active, but no read only
- Both devices active, but no placeholders
- High quality animation, but no animation denoising
- Animation denoising, but exr is not selected
- Single frame rendering (start and end frame have the same value), but animation denoising is activated
- Single frame in high quality is being rendered, but Denoising is deactivated


