# Installing _Atlas_ on Ubuntu

Perform the following steps in order to install _Atlas_ on Ubuntu.

## Download source code

You must first clone the repository:

```
git clone https://github.com/nov314k/atlas.git
```

## Create a virtual environment

It is best to create and work within a virtual environment, and this is especially true if you are evaluating _Atlas_.
Although it's completely optional, it might be tidier to keep the virtual environment files in a separate `venv` folder:

```
cd atlas
python3 -m venv venv
source venv/bin/activate
```

Note that, inside the virtual environment, `python` (without number 3) refers to `python3` (which was used to create the
virtual environment).

Upgrade to the latest version of `pip` in the virtual environment:

```
python -m pip install --upgrade pip
```

## Install packages

### Install required packages

TBD

### Install optional packages (used for developing new features)

TBD

## Open the example portfolio to test the installation

Open the example portfolio to test the installation:

```
python atlas/main.py docs/example-portfolio/example.json
```

<p align="center">
<img src="../docs/images/1375061_width_x_height_226x250.png">
</p>

[Return to README](../README.md)
