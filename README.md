# C4D installer

This repository provides a customizable installer for Cinema 4D plugins based
on CPython 3, PyInstaller and PyQt5. It is licensed under GPL to abide the
PyQt5 license requirements.

![Installer Screenshots](http://i.imgur.com/O2sHbqn.jpg)

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

## Configuration

*Todo*

The installer is configured using the [`config.json`](config.json) file.

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
