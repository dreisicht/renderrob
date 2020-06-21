# Documentation

## Good to know

##### Usage

- If you want to abort all renders, you have to close all three command-line windows.
- To stop the jobs, first close the Render Rob main window.
- The reason motion blur is in Render Rob, is that if you get motion blur artifacts, you can easily re-render those frames without motion blur
- You can run your own Python commands by adding them to the file `rr_user_comands.py` located in the folder `user`.

##### Sheet

- Column a is a help for being able to select cells easier.
- Column t is necessary. Please do not delete it.
- For better overview, usually all settings in the sheet are checked (apart from the last one, denoising).
- If you disable Cycles (and by that enable Eevee), the irrelevant settings get disabled.
- Separate View Layers and add-ons with a comma (space is optional)
- If you want to render a still image, fill start frame with the frame you want to render and leave end frame blank.
- If you don't provide start frame and end frame the, Render Rob will render an animation with the start and end set in the Blender file.
- If you want to use multiple Sheets you can configure your sheet name in the file `util/sheetname.ini`
- If you only want to denoise your shot, deactivate both CPU and GPU and activate Animation Denoising.

##### Render output

- If read only is enabled, a new folder with a new version number is created and used as render output.
- The Folder and frame name consists of `filename-camera-Scene-viewlayer-quality-version`
- Empty folders of failed renders get deleted in the end
- Render Rob never overwrites images. If you activate `new version`, he creates a new folder for output. If new version is not activated, he continues in the folder with the highest version number and skips already rendered images. So if you want to re-render some images, delete them, and then render the job with `new version` deactivated.

##### Rendering

- Border rendering gets disabled, if high quality is active. Otherwise it remains enabled.
- Random seed is enabled, if Animation Denoising is enabled.
- Jobs get rendered in the order, they are shown in the list. You can reorder them by drag-and-drop. Therefore select the line and drag it on the left side up or down.
- CPU renders on n-1 cores to not bottleneck GPU render
- You can only render one scene in one job. If you want to render a second scene just create another job
- If no Scene is given, Render Rob renders the last active Scene.
- If no View Layer is given, Render Rob renders every View Layer.
- If Animation Denoising is activated, compositing is deactivated.

##### Errors

- If Render Rob cannot find the sheet, maybe it's not shared with the API mail address.
- If you experience other errors, don't hesitate do drop me a message!

## Warnings in the sheet

If a property in the sheet gets marked yellow, this means, that a possible error is found. These are just warnings, so you still are able to start the job. In some cases it will work, in some it won't.

Following things are the most important ones being looked at:

- Double occurrences of jobs
- No render device selected
- High quality animation, but no Animation Denoising
- Animation Denoising, but exr is not selected
- Single frame rendering (start and end frame have the same value), but Animation Denoising is activated
- Single frame in high quality is being rendered, but Denoising is deactivated
- Single frame being rendered, but both CPU and GPU are selected

## Setup

**ATTENTION! If you don't want to setup the Google spread API, you can download the sheet as an xlsx and put it next to the .exe** 

Click on the chapter to open it:

<details>
<summary>1. Usage of Render Rob without API setup </summary>
If you don't want to setup your Google API, you can also work with downloaded .xlsx files.
Here you have two options. You either copy the sheet into your Google Drive, or you download the sheet straightaway as an .xlsx file and manipulate if offline.

1. Open this spreadsheet:
https://docs.google.com/spreadsheets/d/1Hc74LRRvTiekuYtiTYaZGC9qCOjnf9SiAurZwmgZjUQ/edit?usp=sharing

1. Copy the sheet into your Drive.

![Text](img/readme_pics/Anmerkung%202020-04-26%20101650.jpg "Sheet")


1. Name it e.g. `Render Rob`.

![Text](img/readme_pics/Anmerkung%202020-04-26%20101720.jpg "Sheet")

3. Download the sheet as .xlsx

![Text](img/readme_pics/Anmerkung%202020-05-20%20090653.jpg "Sheet")

4. Place it next to the RenderRob.exe

![Text](img/readme_pics/Anmerkung%202020-05-20%20091309.jpg "Sheet")

</details>

<details>
<summary>2. Setting up Google API</summary>

<!-- ### Setting up Google api -->

1. Open up https://console.developers.google.com, agree to terms and conditions and click on `Agree and continue`

![Text](img/readme_pics/Anmerkung%202020-04-26%20102222.jpg "Terms and Service")

2. Click on create project


![Text](img/readme_pics/Anmerkung%202020-04-26%20125300.jpg "Dashboard")

3. Name the project e.g. Render Rob and click on create

![Text](img/readme_pics/Anmerkung%202020-04-26%20102359.jpg "Create Project")

4. Search for **Google Drive API** and enable it

![Text](img/readme_pics/Anmerkung%202020-04-26%20125343.jpg "Search API")
![Text](img/readme_pics/Anmerkung%202020-04-26%20125407.jpg "Drive API")
<!-- ![Text](img/readme_pics/Anmerkung%202020-04-26%20102553.jpg "Descrp") -->

5. Same for **Google Sheets API**

![Text](img/readme_pics/Anmerkung%202020-04-26%20102550.jpg "Search API")
![Text](img/readme_pics/Anmerkung%202020-04-26%20102636.jpg "Sheet API")

6. Click on Create Credentials

![Text](img/readme_pics/Anmerkung%202020-04-26%20125536.jpg "Credentials")

7. fill out the form and click on `What credentials do I need?`

![Text](img/readme_pics/Anmerkung%202020-04-26%20102827.jpg "Credentials")

8. continue filling out

![Text](img/readme_pics/Anmerkung%202020-04-26%20102856.jpg "Credentials")

9. save the json file you get in the `Render Rob\Key` Folder

![Text](img/readme_pics/Anmerkung%202020-04-26%20102919.jpg "Credentials")
</details>

<!-- ### Spreadsheet -->

<details>
<summary>3. Spreadsheet setup </summary>

1. Open this spreadsheet:
https://docs.google.com/spreadsheets/d/1Hc74LRRvTiekuYtiTYaZGC9qCOjnf9SiAurZwmgZjUQ/edit?usp=sharing

1. Copy the sheet into your Drive.

![Text](img/readme_pics/Anmerkung%202020-04-26%20101650.jpg "Sheet")


3. Name it `Render Rob`. If you name it different, you will have to add the name to the `sheetname.ini` located in the `user` folder.

![Text](img/readme_pics/Anmerkung%202020-04-26%20101720.jpg "Sheet")

4. Copy the e-mail address from step 8 (it's called Service account ID there) and share the sheet with the mail!

![Text](img/readme_pics/Anmerkung%202020-04-26%20104113.jpg "Sheet")
</details>


<!-- ### Filling the spreadsheet -->

<details>
<summary>4. Filling the spreadsheet </summary>

After setting that up, fill in the global settings in the Sheet. The Blender Path and Render Path is mandatory, the rest is optional.

![Text](img/readme_pics/Anmerkung%202020-04-26%20134758.jpg)

Now you only have to paste your attributes of your job to be rendered, and run `renderrob.exe`!

</details>



## Properties

Property list of the spreadsheet

| Property | Mandatory |Usage |
|--- |:---|:---|
| active | ✅ | Activates or deactivates job |
| .blend file path | ✅ | Absolute path to blend file, or relative path to the "path to blender files folder" given under globals |
| camera | | Name of camera to be activated, optional |
| start frame | | First frame to be rendered. It is recommended to give this information, so Render Rob can check if all the frames are rendered|
| end frame | | Last frame to be rendered. It is recommended to give this information, so Render Rob can check if all the frames are rendered|
| X res | | Horizontal resolution |
| Y res | | Vertical resolution|
| samples | | Number of Cycles or Eevee passes|
| file format | ✅ | Output file format. Exr refers to multilayer exr|
| Cycles (Eevee) | ✅ | If activated, Cycles is used, otherwise Eevee|
| CPU | ✅ | Usage of CPU for rendering |
| GPU | ✅ | Usage of GPU for rendering |
| motion blur | ✅ | Usage of Motion blur |
| new version | ✅ | If activated, a new folder gets created. Otherwise the job gets  |
| high-quality | ✅ | If deactivated, preview settings from globals are used|
| animation denoise | ✅ | Usage of post-process animation denoising|
| denoise | ✅ | Usage of image-denoising|
| scene | | Add name of scene to render. Only one is allowed here. Optional.|
| view layer | | Add name of view layer to render. Only one is allowed here. Optional.|
| comments | | Put your own comments of the shot here|

