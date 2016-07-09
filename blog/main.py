import os
import jinja2
import webapp2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("postdetail.html", blog = self)

class MainPage(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * from Blog order by created desc limit 10")
        self.render("home.html", blogs = blogs)

class Newpost(Handler):
    def render_front(self, subject="", content="", error=""):
        self.render("newpost.html", subject=subject, content=content, error = error, blogs = blogs)

    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            b = Blog(subject = subject, content = content)
            b.put()
            self.redirect('/blog/%s' % str(b.key().id()))
        else:
            error = "both of them must implement"
            self.render_front(subject, content, error = error)

class Postdetail(Handler):
    def get(self, propertyId):
        key = db.Key.from_path('Blog', int(propertyId))
        blog = db.get(key)

        if not blog:
            self.error(404)
            return

        self.render("permalink.html", blog = blog)

app = webapp2.WSGIApplication([('/blog/?', MainPage),
                               ('/blog/newpost', Newpost),
                               ('/blog/([0-9]+)', Postdetail)], debug = True)
