import os
import sys
import optparse
import flask
import markdown

Docroot = None
app = flask.Flask(__name__)


class Hyperdir:

    def __init__(self, hyperpath):
        assert hyperpath.isdir
        self.hyperpath = hyperpath
        self.name = self.hyperpath.name

    def GET(self):
        # get index files, if any
        hypertxt = None
        for index in ( "index.txt", "index.md", "INDEX" ):
            if self.hyperpath.contains("index.md"):
                hypertxt = Hypertxt(self.hyperpath.join("index.md"))
                break
        return flask.render_template("hyperdir.html", hyperdir=self,
                                                      hypertxt=hypertxt)

class Hypertxt:

    def __init__(self, hyperpath):
        assert not hyperpath.isdir
        self.hyperpath = hyperpath
        self.name      = self.hyperpath.name
        self.ext       = self.hyperpath.ext
        self.raw       = self.hyperpath.read()
        self.text      = self.render(self.ext, self.raw)

    def render(self, ext, raw):
        return getattr(self, "render_" + ext, self.render_txt)(raw)

    def render_txt(self, text):
        return text

    def render_md(self, text):
        return markdown.markdown(text)

    def GET(self):
        return flask.render_template("hypertxt.html", hypertxt=self)


class Hyperpath:

    class DoesNotExist(Exception): pass
    class AccessDenied(Exception): pass

    def __init__(self, path, root, name=None):
        from os.path import exists, isabs, isdir, realpath, relpath, join
        from os.path import basename, splitext
        assert isabs(root) and not isabs(path)

        self.root     = root
        self.path     = path
        self.realpath = realpath(join(root, path))
        self.relpath  = relpath(self.realpath, root)
    
        if not exists(self.realpath):
            raise self.DoesNotExist(self.realpath)
        if not self.realpath.startswith(self.root):
            raise self.AccessDenied()

        self.isdir = isdir(self.realpath)
        self.name  = name if name else basename(self.path)
        self.ext   = splitext(self.realpath)[1][1:] if not self.isdir else None

    def join(self, *path):
        return Hyperpath(path=os.path.join(self.path, *path),
                         root=self.root)

    def ls(self):
        if not self.isdir:
            raise AttributeError("Cannot ls a file")
        return [ self.join(p) for p in os.listdir(self.realpath) ]

    def read(self):
        if self.isdir:
            raise AttributeError("Cannot read a directory")
        with open(self.realpath, "rt") as f:
            return f.read()

    def rootpath(self):
        return Hyperpath(path=".", root=self.root, name="main")

    def contains(self, item, isdir=False):
        p = os.path.join(self.realpath, item)
        return os.path.exists(p) and ( not isdir or os.path.isdir(p) )

    def breadcrumbs(self):
        crumbs = [self.rootpath()]
        def pathsplit(p):
            h, t = os.path.split(p)
            if t:
                if h:
                    pathsplit(h)
                assert t != "/"
                crumbs.append(crumbs[-1].join(t))
            else:
                assert not h
        pathsplit(self.relpath.lstrip("/").rstrip("/"))
        return crumbs   

    @classmethod
    def handler(cls, path, root, name=None):
        hyperpath = cls(path, root, name)
        if hyperpath.isdir:
            return Hyperdir(hyperpath)
        else:
            return Hypertxt(hyperpath)

@app.route("/<path:path>")
def hypertxt_get(path):
    try:
        return Hyperpath.handler(path, Docroot).GET()
    except Hyperpath.DoesNotExist:
        flask.abort(404)
    except Hyperpath.AccessDenied:
        flask.abort(401)

@app.route("/")
def hypertxt_main():
    return Hyperpath.handler(".", Docroot, name="Main").GET()


if __name__ == "__main__":
    optparser = optparse.OptionParser()
    optparser.add_option("--host", dest="host", default="localhost",
                         help="Server HOSTNAME")
    optparser.add_option("--port", dest="port", default="8080",
                         help="Server PORT")
    optparser.add_option("--root", dest="root", default=os.getcwd(),
                         help="Document root")
    optparser.add_option("--verbose", action="store_true", dest="verbose", 
                         default=False, help="Verbose")
    (options, args) = optparser.parse_args()
    
    Docroot = os.path.realpath(options.root)
    app.debug = True
    app.run('localhost')
