# Customisable Cinema 4D Plugin Installer

<table><tr>
  <td><img src="https://i.imgur.com/8IsfiOr.png"/></td>
  <td><img src="https://i.imgur.com/OltXTrd.png"/></td>
  <td><img src="https://i.imgur.com/jDCagZE.png"/></td>
  <td><img src="https://i.imgur.com/4I1GWn9.png"/></td>
</tr><tr>
  <td><img src="https://i.imgur.com/jM9GU4r.png"/></td>
  <td><img src="https://i.imgur.com/hX57pCP.png"/></td>
  <td><img src="https://i.imgur.com/od3FLgX.png"/></td>
  <td><img src="https://i.imgur.com/2UCFRNX.png"/></td>
</tr></table>

Easily create an installer for your Cinema 4D plugin for Windows and Mac OS.
Replace the banner and icon, update some configuration, build & done.

Check out the [Milestones] page for what's still to do.

[Milestones]: https://github.com/nr-plugins/installer/milestones

## Features

- [x] Very customisable
- [x] Automatically finds available Cinema 4D installations on the system
- [x] Supports installing dependencies from redistributable installers
- [x] Optional Uninstaller

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
    "button_foreground": [220, 220, 220],
    "button_disabled_background": [70, 70, 70],
    "button_disabled_foreground": [160, 160, 160]
  }
```

#### Readme after Installation

```json
  "readme": {
    "enabled": true,
    "file": "data/readme.pdf"
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
where in the Cinema 4D application directory. Available variables:

- `$src` for the [data/install] directory
- `$c4d` for the C4D target installation directory (note that theoretically
  this could also be an arbitrary directory, depending on what the user
  chose as target installation path)
- `$systemappdir` for the system application folder, this is either `C:\Program Files`
  on Windows or `/Applications` on Mac OS. Some plugins might need to install
  stuff there.

```json
  "install": {
    "slowdown": 0.5,
    "copyfiles": {
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
    "dependencies": [
    ]
  }
```

For testing purposes, you may choose a number in seconds for `"slowdown"`.
This is the time that will be waited after each update to the installation
progress to slow down and make it easier to track what's happening.

The `"dependencies"` section is used to specify additional installers that
need to be installed for the plugin to function. Variable substition is
supported in the `"name"`, `"file"` and `"args"` fields. The fields
`"returncode"`, `"args"` and `"features"` are optional. Valid values for
`"platform"` are `"windows"` and `"osx"`. **Example:**

> In the `"features"` field, you must list the IDs of the features that cause
> this dependency to be installed. In the example below, the dependency will
> only be installed if the `plugin` feature is selected to be installed by the
> user.

```json
    "dependencies": [
      {
        "name": "MSVC++ 2015 Redistributable (x64) - 14.0.23026",
        "platform": "windows",
        "features": ["plugin"],
        "file": "$src/redist/windows/vc_redist-2015-14.0.23026-x64.exe",
        "args": ["/install"],
        "returncodes": [0, 1638]
      }
    ]
```

#### Uninstaller

The default configuration for the uninstaller is this:

```json
  "uninstaller": {
    "enabled": true,
    "target_directory": "$c4d/plugins/C4DInstaller_ExamplePlugin/",
    "name": "uninstall",
    "bundle_identifier": "com.niklasrosenstein.c4dinstaller_uninstaller"
  },
```

You can choose to disable the uninstaller. The uninstaller will be placed
into the directory you specify with `"target_directory"`. In the same directory
a file will be created called `${name}.data` which contains all the names of
the files that have been installed, so that the installer knows what to
uninstall.

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

In order to run the installer or uninstaller for testing purposes, use

    make run-installer
    make run-uninstaller

The Makefile supports a `PYTHON` environment version, so if `python` is not
the program where all of the dependencies are installed, you should use this
variable to point to the correct program, eg. `PYTHON=py -3.4` or
`PYTHON=python3`.

## Building the Installer

It is important to build the uninstaller *before* the installer.

    make uninstaller
    make installer

## Installer admin privileges

On Windows, the installer is built with UAC enabled. Note that there is
currently nothing implemented to have `make run-installer` run as administrator.

On Mac OS, the `/usr/bin/osascript` workaround is used to ask the user for
elevated privileges and then execute the installer in that environment.

---

<p align="center">Copyright &copy; 2016 &ndash; Niklas Rosenstein</p>
