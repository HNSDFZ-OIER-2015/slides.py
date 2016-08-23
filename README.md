# slides.py
Translate your markdown slides to PDF.

## Requirements
* Python 3 (>= 3.4)
* wkhtmltopdf (>= 0.12.3 with patched Qt)
* pdftk (>= 2.01)
* Python Markdown
* Beautiful Soup 4

For `wkhtmltopdf`, you can download it from its website.

For pdftk, on Linux:

```shell
sudo apt-get install pdftk
```

For Python 3 requirements, use `pip3`:

```shell
sudo pip3 install markdown
sudo pip3 install bs4
```

## Usage
Change your working directory to the father of your slides folder.

Assume your sildes name is "example", run:

```shell
slides.py example
```

`slides.py` will find `example/example.json`. If found, `slides.py` will start compiling slides.

## Example
See `example/`.

Use `slides.py` to compile it, `output.pdf` will be generated in the `example` folder.

Have fun!
