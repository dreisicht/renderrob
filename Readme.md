# Render Rob

[![LinuxTestAndBuild](https://github.com/dreisicht/renderrob/actions/workflows/linux_test_and_build.yaml/badge.svg)](https://github.com/dreisicht/renderrob/actions/workflows/linux_test_and_build.yaml)
[![WindowsMacBuild](https://github.com/dreisicht/renderrob/actions/workflows/windows_mac_build.yaml/badge.svg)](https://github.com/dreisicht/renderrob/actions/workflows/windows_mac_build.yaml)

![ ](img/renderrob_deck.jpg)

**Render Rob is a standalone Render Manager built with the goal to make rendering multiple Blender files as easy as possible. No need for command line fiddling anymore!**

## Why should I use it?

Save time managing your render jobs!

## Who is it for?

Individuals and small teams, who don't want to render with a render farm, but still want to manage their render jobs in a simple way.

## Features

- Overview of jobs and settings in a table.
- You can render a quick preview, before spending hours on your final render.
- Only one click needed to start rendering your jobs.
- Warnings for implausible render settings directly in the table.
- Automatic organizing of render output folder.
- Cross platform compatible.

![screenshot](img/documentation/docu.svg)

<!-- <video width="100%" controls>
  <source src="https://dreisicht.net/video/renderrob_v3.mp4" type="video/mp4">
Your browser does not support the video tag.
</video> -->

## Support

If you like the product and would like to support me, consider buying it on [Gumroad](https://gum.co/JXBgO) or [Blendermarket](https://blendermarket.com/products/render-rob). Thanks a lot!

Render Rob is developed by the biggest effort possible, and every effort has been made that no harm should happen to you computer and files. Still Render Rob is not responsible for any harm and lost images. By downloading this product you consent to this.

## Good to know

### Render output

- If you want to render a still, enter a frame number.
- For rendering an animation enter both start and end frame, or leave the start and end frame empty.
- If read only is enabled, a new folder with a new version number is created and used as render output.
- The Folder and frame name consists of `filename-camera-Scene-viewlayer-quality-version`
- Empty folders of failed renders get cleaned up.
<!-- TODO: Verify this. -->
- Render Rob never overwrites images. If you deactivate `overwrite`, it creates a new folder for output. If new version is not activated, it continues in the folder with the highest version number and skips already rendered images. So if you want to re-render some images, delete them, and then render the job with `overwrite` activated.

### Rendering

- Border rendering gets disabled, if high quality is active. Otherwise it remains enabled.
- You can only render one scene in one job. If you want to render a second scene just duplicate the job.

## Developer area

Python version required due to bpy: **3.11**

Install QtDesigner:

```
pyqt6-tools installuic
```

Start QtDesigner:

```
pyqt6-tools designer
```

Convert protos:

```
protoc --proto_path=protos/ --python_out=protos/ protos/state.proto
protoc --proto_path=protos/ --python_out=protos/ protos/cache.proto
```

Create .ico file

```
magick.exe convert icon-16.png icon-20.png icon-24.png icon-32.png icon-40.png icon-48.png icon-64.png icon-256.png icon.ico
```

Create venv

```
python -m venv ./venv/
```

Deploy

```
.\venv\Scripts\activate
pyside6-deploy -c build\pysidedeploy_win.spec
```

Remove stale origin branches

```
git remote prune origin
```

Manual installation and signing on Mac

```
pyside6-deploy -c build/pysidedeploy_mac.spec --force --verbose --keep-deployment-files
codesign -s "Peter Baintner" -f --timestamp -i "com.dreisicht.renderrob" --deep RenderRob.app
```
