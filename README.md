# Hypertxt

Hypertxt allows you to view your plain text files in your browser,
with some support for rendering markup languages like Markdown. It
serves all text files in a hierarchy of directories, rooted at a
given directory, at startup.

    $ python hypertxt.py --root <document-root>

Your notes should be available at http://localhost:4567/

## Requirements

You need the Flask web microframework.

    $ [sudo] easy_install flask
