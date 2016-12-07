# Customisable Cinema 4D Plugin Installer

<table><tr>
  <td><p align="center">01 Welcome</p><img src="https://i.imgur.com/8IsfiOr.png"/></td>
  <td><p align="center">02 EULA</p><img src="https://i.imgur.com/OltXTrd.png"/></td>
  <td><p align="center">03 Features</p><img src="https://i.imgur.com/jDCagZE.png"/></td>
  <td><p align="center">04 Target</p><img src="https://i.imgur.com/4I1GWn9.png"/></td>
</tr><tr>
  <td><p align="center">05 Install</p><img src="https://i.imgur.com/jM9GU4r.png"/></td>
  <td><p align="center">06 End</p><img src="https://i.imgur.com/hX57pCP.png"/></td>
  <td><p align="center">00 About Page</p><img src="https://i.imgur.com/od3FLgX.png"/></td>
</tr></table>

Easily create an installer for your Cinema 4D plugin for Windows and Mac OS.
Replace the banner and icon, update some configuration, build & done.

Check out the [Milestones] page for what's still to do.

[Milestones]: https://github.com/nr-plugins/installer/milestones

## Requirements

- CPython 3.3 or 3.4 (3.5 not supported by PyInstaller)
- PyInstaller 3.3\*
- PyQt5\*\*
- GNU Make\*\*\*

> \* At the time of this writing (2016-12-06), PyInstaller 3.3 is not released
> and must be installed from the development branch using
> `pip install git+https://github.com/pyinstaller/pyinstaller`
>
> \*\* On Windows, it is highly recommended to use an official PyQt5 installer
> from [Riverbank Software](https://www.riverbankcomputing.com/) rather than
> installing it with Pip as it can lead to issues with finding all dependencies
> when building the installer. The official installers can be found on
> [SourceForge](https://sourceforge.net/projects/pyqt/files/PyQt5/).
>
> Also note that the installer is known to put the development tools into
> the wrong directory. If `pyuic5` can not be found, copy it from
> `YourPythonInstall/Libs/site-packages/PyQt5/pyuic5.bat` to the
> `YourPythonInstall/Scripts` folder.
>
> \*\*\* Windows builds of GNU Make can be found [here](http://gnuwin32.sourceforge.net/packages/make.htm).
> The Makefile is known to work with GNU Make 3.8.1

## Configuration & Customisation

The main configuration file is [data/config.json](data/config.json). There
you need to specify the following information:

- Basic installer info, like the generated executable/bundle name and the
  OSX bundle identifier.
- Features that will be displayed in the "Features" page of the installer.
  Note that if no features are configured, the page will not be displayed.
- The files that need to be copied for each feature and where they need to
  be copied to.

#### Text

The strings that are displayed in the dialog are defined in
[data/strings/en.json]. In every string you can use variables in the format
`$varname` or `${varname}`. These variables are defined in the `"__vars__"`
section of the same string file.

#### Colors

In [data/config.json] you can find a `"palette"` field which describes the
colors of window components as RGB values.

```json
  "palette": {
    "background": [40, 40, 40],
    "foreground": [200, 200, 200],
    "alternate_background": [70, 70, 70],
    "button_background": [50, 50, 50],
    "button_foreground": [220, 220, 220]
  }
```

#### Feature Configuration

Note that these variables are also supported in the `"features"` object
in [data/config.json]. The demo configuration contains the following feature
declaration:

```json
  "features": {
    "!plugin": "$plugin",
    "docs": "$documentation",
    "presets": "$presets"
  }
```

On the left side you can see the identifiers. These identifiers are used
in the `"install"` section. On the right side are the names of the features
that are displayed in the installer. In the example above, they reference
variables in the string file. The `!` prefix makes the feature always enabled
and prevents the user from turning it of (used for the "main" feature that
is always required).

#### Install Configuration

Files that are to be installed should be placed into the [data/install]
directory. By default, there's a sample Python plugin, a material preview
preset and a plugin documentation file (respective to the default features).

The `"install"` section lists which files or directoriees are to be copied
where in the Cinema 4D application directory. The variables `$src` and `$c4d`
are available respectively to reference the [data/install] directory and the
installation path (that is usually the Cinema 4D root directory).

```json
  "install": {
    "plugin": {
      "$src/plugin/": "$c4d/plugins/C4DInstaller_ExamplePlugin/"
    },
    "docs": {
      "$src/doc/": "$c4d/plugins/C4DInstaller_ExamplePlugin/doc/"
    },
    "presets": {
      "$src/library/": "$c4d/library/"
    }
  },
  "installed_files_list": "$c4d/plugins/C4DInstaller_ExamplePlugin/installed-files.txt",
  "install_slowdown": null
```

The `"installed_files_list"` is the file that will be created after all files
have been copied. This file lists up all files and directories that have been
created by the installer. Directories are listed at the end of the file in the
order they can be removed from the bottom up.

For testing purposes, you may choose a number in seconds for
`"install_slowdown"`. This is the time that will be waited after each update
to the installation progress to slow down and make it easier to track what's
happening.

#### EULA

The EULA can be in [data/eula.txt] and should be updated before building the
installer. If you don't want to display an EULA, you can delete the file
entirely.

#### Summary

To summarise, these are the steps to configure the installer:

1. Change the installer and bundle name in [data/config.json]
2. Add or remove features from the `"features"` section in [data/config.json]
3. Add the files to be installed to `data/install` and update the `"install"`
   section in [data/config.json]
4. Update the strings in [data/strings/en.json]
5. Test and build the installer

[data/config.json]: data/config.json
[data/strings/en.json]: data/strings/en.json
[data/install]: data/config.json
[data/eula.txt]: data/config.json

## Testing

In order to run the installer for testing purposes, use

    make run

The Makefile supports a `PYTHON` environment version, so if `python` is not
the program where all of the dependencies are installed, you should use this
variable to point to the correct program, eg. `PYTHON=py -3.4` or
`PYTHON=python3`.

## Building the Installer

    make installer

---

<p align="center">Copyright &copy; 2016 &ndash; Niklas Rosenstein</p>
