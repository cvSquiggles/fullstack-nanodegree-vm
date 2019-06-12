from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#Make connection to db file through SQLAlchemy
engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

session = DBSession()

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

            #Pull all the restaurant names and set them equal to a variable as a list
            allRestaurants = session.query(Restaurant).all()

            output = ""
            output += "<html><h1>Here's a list of all the restaurants!</h1><body>"
            output += "<a href='/restaurants/new'>Add new restaurant</a></br></br>"
            for i in allRestaurants:
                output += ("{}</br>".format(i.name))
                output += ("<a href='/restaurants/{}/edit'>Edit</a> ".format(i.id))
                output += ("| <a href='/restaurants/{}/delete'>Delete</a> </br></br>".format(i.id))
            output += "</body></html>"
            self.wfile.write(output)

            print(output)
            return

        elif self.path.endswith("/edit"):
            restaurantIDPath = self.path.split("/")[2]
            myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
            if myRestaurantQuery != []:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += ("<html><h1>Change {}'s name:</h1><body>".format(myRestaurantQuery.name))
                output += ('''
                <form method='POST' enctype='multipart/form-data' action='/restaurants/{}/edit'>
                <input name='newRestName' type='text' placeholder='{}'>
                <input type='submit' value='Change'>
                </form>'''.format(restaurantIDPath, myRestaurantQuery.name))
                output += "</body></html>"
                self.wfile.write(output)

                print(output)
                return

        elif self.path.endswith("/delete"):
            restaurantIDPath = self.path.split("/")[2]
            myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
            if myRestaurantQuery != []:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += ("<html><h1>Do you want to remove {} from the list?</h1><body>".format(myRestaurantQuery.name))
                output += ('''
                <form method='POST' enctype='multipart/form-data' action='/restaurants/{}/delete'>
                <input type='submit' value='Delete'>
                </form>'''.format(restaurantIDPath))
                output += "</body></html>"
                self.wfile.write(output)

                print(output)
                return

        elif self.path.endswith("/restaurants/new"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            output = ""
            output += "<html><h1>Make a new restaurant:</h1><body>"
            output += '''
            <form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
            <input name='restName' type='text' placeholder='New Restaurant Name'>
            <input type='submit' value='Create'>
            </form>'''
            output += "</body></html>"
            self.wfile.write(output)

            print(output)
            return

        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                restaurantIDPath = self.path.split("/")[2]

                restToDelete = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                if restToDelete != []:
                    session.delete(restToDelete)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newRestName')
                restaurantIDPath = self.path.split("/")[2]

                restToChange = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                if restToChange != []:
                    restToChange.name = messagecontent[0]

                    session.add(restToChange)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('restName')

                newRestaurant = Restaurant(name = messagecontent[0])
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            #ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
            #if ctype == 'multipart/form-data':
            #    fields=cgi.parse_multipart(self.rfile, pdict)
            #    messagecontent = fields.get('message')

            #    output = ""
            #    output += "<html><body>"
            #    output += " <h2> alright...</h2>"
            #    output += "<h1> {} </h1>".format(messagecontent[0])

            #    output += '''
            #    <form method='POST' enctype='multipart/form-data' action='/hello'>
            #    <h2>What would you like me to say?</h2>
            #    <input name='message' type='text'>
            #    <input type='submit' value='Submitto'> 
            #    </form>'''
            #    output += "</body></html>"
            #    self.wfile.write(output)

            #    print(output)

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