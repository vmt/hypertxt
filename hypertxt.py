import os
import sys
import optparse
import BaseHTTPServer
import urlparse
import markdown

OutputHTMLHeader = """
<html>
<head>
<title>%(title)s</title>
<style type="text/css">
html {
  background-color: #fff;
  font-size: 100%%;
  padding: 0; margin: 0;
}
body {
  font-family: "Lucida Grande", "Tahoma", "Verdana", "Trebuchet MS",
               "sans-serif";
  font-size: 12px;
  padding: 0; margin: 0;
}
div#header {
  width: 100%%;
  background-color: #eee;
  border-bottom: 1px solid #ccc;
}
span#document-path {
 display: inline-block;
  padding: 5px 5px 5px 10px;
}
div#content {
  width: 100%%;
  padding: 0px;
  margin: 20px 10px 0 20px;
  width: 600px;
  line-height: 16px;
}
</style>
</head>
<body>
  <div id="header">
    <span id="document-path">
      <a href="/%(path)s">%(path)s</a>
    </span>
  </div>
  <div id="content">
"""

OutputHTMLFooter = """
  </div>
</body>
</html>
"""

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    class DocumentNotFound(Exception): pass
    class DocumentInvalid(Exception): pass
    class DocumentNotHandled(Exception): pass

    docindex = 'index.md'
    docroot  = os.path.abspath(os.getcwd())

    def render_document(self, path):
        # - Get the canonical path, enuring symbolic links
        #   are taken and special dirs are resolved.
        # - Check if the Document is indeed rooted under docroot.
        # - Check if the Document exists. 

        print self.docroot

        realpath = os.path.realpath(os.path.join(self.docroot, path))
        print realpath
        if os.path.relpath(realpath, self.docroot) != path:
            raise self.DocumentInvalid()
        if not os.path.exists(realpath):
            raise self.DocumentNotFound()

        if not os.path.isfile(realpath):
            raise self.DocumentNotHandled()

        text = open(realpath, "rt").read()
        if os.path.splitext(realpath)[1] in ('.md', '.markdown'):
            text = markdown.markdown(text)
        else:
            text = "<pre>" + text + "</pre>"

        return text

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
    def do_GET(self):
        u = urlparse.urlsplit(self.path)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        path = u.path.lstrip('/')
        if len(path) == 0:
            path = self.docindex
        body = ''

        try: 
            body = self.render_document(path)
        except self.DocumentInvalid:
            body = "<b>Invalid Document: %s</b>" % path
        except self.DocumentNotFound:
            body = "<b>Document Not Found: %s</b>" % path
        except self.DocumentNotHandled:
            body = "<b>Document Not Handled: %s</b>" % path
        finally:
            self.wfile.write(
                OutputHTMLHeader % { 'title': path,
                                     'path' : path }
                )
            self.wfile.write(body)
            self.wfile.write(OutputHTMLFooter)

if __name__ == '__main__':

    # Command-line options
    optparser = optparse.OptionParser()

    optparser.add_option("--host", dest="host", default="localhost",
                         help="Server HOSTNAME")
    optparser.add_option("--port", dest="port", default=8080,
                         type="int", help="Server PORT")
    optparser.add_option("--root", dest="root", default=os.getcwd(),
                         help="Document root")
    optparser.add_option("--verbose", action="store_true", dest="verbose", 
                         default=False, help="Verbose")

    (options, args) = optparser.parse_args()

    print "Starting server ..."
    print "Host=%s" % options.host
    print "Port=%s" % options.port
    print "Root=%s" % options.root

    RequestHandler.docroot = options.root

    try:
        httpd = BaseHTTPServer.HTTPServer((options.host, options.port), 
                                          RequestHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
