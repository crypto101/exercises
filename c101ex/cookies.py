"""
A website that uses cookies to determine admin status. Poorly.
"""
from functools import partial
from merlyn.multiplexing import addToStore
from string import ascii_letters
from twisted.web import resource, server, template


class Index(resource.Resource):
    isLeaf = True
    cookieName = "soylentgreen"

    def render_GET(self, request):
        """
        Greets the user appropriately.
        """
        rawCookie = request.getCookie(self.cookieName)
        if rawCookie is None:
            name, isAdmin = None, False
        else:
            cookie = self._decryptCookie(rawCookie)
            contents = self._parseCookie(cookie)
            name = contents.get("name")
            isAdmin = contents.get("admin") == "1"

        return self._render(request, name, isAdmin)


    def render_POST(self, request):
        """
        Registers a user, setting their cookie.
        """
        name, = request.args.get("name")
        name = "".join(x if x in ascii_letters else "" for x in name)

        rawCookie = self._encodeCookie({"name": name})
        cookie = self._encryptCookie(rawCookie)
        request.addCookie(self.cookieName, cookie)

        return self._render(request, name, False)


    def _render(self, request, name, isAdmin):
        indexTemplate = IndexTemplate(name, isAdmin)
        return template.renderElement(request, indexTemplate)


    def _encryptCookie(self, value):
        """Encrypts a string cookie.

        """
        return value.encode("rot13")


    def _decryptCookie(self, value):
        """Decrypts a string cookie.

        """
        return value.decode("rot13")


    def _encodeCookie(self, values):
        """Encodes a dictionary of values as a string.

        """
        pairs = ("{0}={1}".format(k, v) for k, v in values.iteritems())
        return "&".join(pairs)


    def _parseCookie(self, rawCookie):
        """Parses a decrypted cookie string into a dictionary.

        """
        return dict(pair.split("=") for pair in rawCookie.split("&"))



templateString = """
<html xmlns:t="http://twistedmatrix.com/ns/twisted.web.template/0.1">
  <body>
    <h1>A website</h1>
    <p t:render="message" />
    <form t:render="registrationForm" method="POST" />
  </body>
</html>
"""



class IndexTemplate(template.Element):
    loader = template.XMLString(templateString)

    def __init__(self, name, isAdmin):
        self.name = name
        self.isAdmin = isAdmin


    @template.renderer
    def message(self, request, tag):
        message = "You are {name} and you are {status}."

        if self.name is None:
            name = "unregistered"
        else:
            name = self.name

        if self.isAdmin:
            status = "an administrator. Yay! Congratulations! You did it"
        else:
            status = "not an administrator"

        return tag(message.format(name=name, status=status))


    @template.renderer
    def registrationForm(self, request, tag):
        if self.name is not None:  # Already registered
            return []

        label = template.tags.label("Name:")
        name = template.tags.input(type="text", name="name", id="name")
        submit = template.tags.input(type="submit")
        return tag(label, name, submit)



site = server.Site(Index())
site.displayTracebacks = False

addToStore = partial(addToStore,
                     identifier="rot13-cookies-site",
                     name="c101ex.cookies.site")
