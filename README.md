# Hypertxt

Hypertxt allows you to view your plain text files in the browser,
with some support for rendering markup languages like Markdown. It
can serve text files in a hierarchy of directories rooted at a
given directory.

## Requirements

You need the Flask web microframework.

    $ [sudo] easy_install flask

## Usage

Start by pointing Hypertxt to your document root (the directory
containing your text files). Optionally, select the port at which
Hypertxt listens for connectios (default=8080).

    $ python hypertxt.py --root <document-root>

Your text files can be viewed at http://localhost:8080/
