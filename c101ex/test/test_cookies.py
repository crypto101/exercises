from c101ex import cookies
from twisted.trial.unittest import SynchronousTestCase
from twisted.web.template import flattenString


class IndexTemplateTests(SynchronousTestCase):
    def setUp(self):
        self.body = None


    def _render(self, name, isAdmin):
        template = cookies.IndexTemplate(name, isAdmin)
        d = flattenString(None, template)
        self.body = self.successResultOf(d).lower()


    def assertNameEquals(self, name):
        self.assertIn("you are {name}".format(name=name), self.body)


    def assertIsAdministrator(self):
        self.assertIn("you are an administrator", self.body)


    def assertIsntAdministrator(self):
        self.assertIn("you are not an administrator", self.body)


    def hasForm(self):
        return "form" in self.body


    def test_unregistered(self):
        """An unregistered user is told they are unregistered and that they
        are not an administrator. There is a form for them to register.

        """
        self._render(None, False)
        self.assertNameEquals("unregistered")
        self.assertIsntAdministrator()
        self.assertTrue(self.hasForm())


    def test_user(self):
        """A user is greeted by their name and a notice that they are not an
        administrator. The registration form is no longer displayed.

        """
        self._render("lvh", False)
        self.assertNameEquals("lvh")
        self.assertIsntAdministrator()
        self.assertFalse(self.hasForm())


    def test_administrator(self):
        """An administrator is greeted by their name and a notice that they
        are an administrator. The registration form is no longer
        displayed.

        """
        self._render("ewa", True)
        self.assertNameEquals("ewa")
        self.assertIsAdministrator()
        self.assertFalse(self.hasForm())


class ResourceTests(SynchronousTestCase):
    def setUp(self):
        self.resource = cookies.Index(None)


    def test_isLeaf(self):
        """The resource is a leaf.

        """
        self.assertTrue(self.resource.isLeaf)


    def test_siteTracebacksDisabled(self):
        """The site has tracebacks disabled.

        """
        site = cookies.makeSite(None)
        self.assertFalse(site.displayTracebacks)


    def test_endToEnd(self):
        """Users start out being not registered. Then, they can register,
        which sets a cookie with their name (with non-ASCII letters
        removed). They can no longer register again after that.

        """
        request = FakeRequest()
        self.resource.render_GET(request)
        self.assertTrue(request.finished)
        self.assertEqual(request.cookies, {})

        request = FakeRequest(args={"name": ["St=ring&  Tr=ep$an#at!ion="]})
        self.resource.render_POST(request)

        self.assertTrue(request.finished)
        self.assertIn("StringTrepanation", request.body)
        self.assertIn("not an administrator", request.body)
        self.assertNotIn("form", request.body)

        rawCookie = request.cookies[self.resource.cookieName]
        cookie = self.resource._decryptCookie(rawCookie)
        data = self.resource._parseCookie(cookie)
        self.assertEqual(data["name"], "StringTrepanation")


    def test_renderNotAdmin(self):
        """Tries to render the template for a use that is not an
        administrator.

        Verifies that the registration form isn't sent, and that the
        exercise is not solved.

        """
        request = FakeRequest()

        self._solvedRequest = None
        self.resource.solveAndNotify = self._solveAndNotify

        rawCookie = self.resource._encodeCookie({"name": "lvh"})
        cookie = self.resource._encryptCookie(rawCookie)
        request.addCookie(self.resource.cookieName, cookie)

        self.resource.render_GET(request)
        self.assertTrue(request.finished)
        self.assertNotIn("you are an administrator", request.body)
        self.assertNotIn("form", request.body)

        self.assertIdentical(self._solvedRequest, None)


    def test_renderAdmin(self):
        """Tries to render the template for a use that is an administrator.

        Verifies that the registration form isn't sent, the welcome
        message says that the user is an administrator, and that the
        user has been notified of success.

        """
        request = FakeRequest()

        self._solvedRequest = None
        self.resource.solveAndNotify = self._solveAndNotify

        rawCookie = self.resource._encodeCookie({"name": "lvh", "admin": "1"})
        cookie = self.resource._encryptCookie(rawCookie)
        request.addCookie(self.resource.cookieName, cookie)

        self.resource.render_GET(request)
        self.assertTrue(request.finished)
        self.assertIn("you are an administrator", request.body)
        self.assertNotIn("form", request.body)

        self.assertIdentical(self._solvedRequest, request)


    def _solveAndNotify(self, request):
        """Fake solveAndNotify implementation that just remembers the request.

        """
        self._solvedRequest = request



class FakeRequest(object):
    def __init__(self, args=None):
        self.args = args
        self.cookies = {}
        self.finished = False
        self.body = ""


    def getCookie(self, key):
        return self.cookies.get(key)


    def addCookie(self, key, value):
        self.cookies[key] = value


    def write(self, data):
        assert not self.finished
        self.body += data


    def finish(self):
        self.finished = True
