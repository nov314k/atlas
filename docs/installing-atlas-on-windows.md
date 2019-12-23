# Installing _Atlas_ on Windows

Perform the following steps in order to install _Atlas_ on Windows.

## Download source code

You must first clone the repository:

```
git clone https://github.com/novakpetrovic/atlas.git
```

## Create a virtual environment

It is best to create and work within a virtual environment. This is especially true if you are evaluating Atlas:

```
python -m venv atlas
cd atlas
Scripts\activate.bat
```

Upgrade to the latest version of `pip` in the virtual environment:

```
python -m pip install --upgrade pip
```

## Install packages

### Install required packages

Commands separated out for clarity:

```
python -m pip install --upgrade PyQt5
python -m pip install --upgrade qscintilla
python -m pip install --upgrade python-dateutil
```

Commands combined into one:

```
pip install --upgrade PyQt5 qscintilla python-dateutil
```

### Install optional packages (used for developing new features)

Commands separated out for clarity:

```
python -m pip install --upgrade google-api-python-client
python -m pip install --upgrade google-auth-httplib2
python -m pip install --upgrade google-auth-oauthlib
```

Commands combined into one:

```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Open the example portfolio to test the installation

Open the example portfolio to test the installation:

```
python atlas/main.py docs/example-portfolio/example.json
```

<p align="center">
<img src="../docs/images/1375061_width_x_height_226x250.png">
</p>

[Return to README](../README.md)
