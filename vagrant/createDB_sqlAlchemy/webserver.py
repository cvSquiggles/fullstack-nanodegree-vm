from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("/hello"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><h1>Klargh!</h1><body>Hello!</body></html>"
            output += '''
            <form method='POST' enctype='multipart/form-data' action='/hello'>
            <h2>What would you like me to say?</h2>
            <input name='message' type='text'>
            <input type='submit' value='Submitto'> 
            </form>'''
            self.wfile.write(output)
            print(output)
            return
        elif self.path.endswith("/hola"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><h1>Klargh!</h1><body>&#161Hola, mi amigos!<a href='/hello'>Back to hello</a></body></html>"
            output += '''
            <form method='POST' enctype='multipart/form-data' action='/hello'>
            <h2>What would you like me to say?</h2>
            <input name='message' type='text'>
            <input type='submit' value='Submitto'> 
            </form>'''
            self.wfile.write(output)
            print(output)
            return
        elif self.path.endswith("/restaurants"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            #Make connection to db file through SQLAlchemy
            engine = create_engine('sqlite:///restaurantmenu.db')

            Base.metadata.bind = engine

            DBSession = sessionmaker(bind = engine)

            session = DBSession()

            #Pull all the restaurant names and set them equal to a variable as a list
            allRestaurants = session.query(Restaurant).all()

            output = ""
            output += "<html><h1>Here's a list of all the restaurants!</h1><body>"
            for i in allRestaurants:
                output += ("{}</br>".format(i.name))
                output += ("<a href='/restaurants?={}'>Edit</a> | <a href='/restaurants?={}'>Delete</a> </br></br>".format(i.name, i.name))
            output += "</body></html>"
            self.wfile.write(output)

            print(output)

        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
            if ctype == 'multipart/form-data':
                fields=cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')

            output = ""
            output += "<html><body>"
            output += " <h2> alright...</h2>"
            output += "<h1> {} </h1>".format(messagecontent[0])

            output += '''
            <form method='POST' enctype='multipart/form-data' action='/hello'>
            <h2>What would you like me to say?</h2>
            <input name='message' type='text'>
            <input type='submit' value='Submitto'> 
            </form>'''
            output += "</body></html>"
            self.wfile.write(output)

            print(output)
        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web Server running on port {}".format(port))
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()