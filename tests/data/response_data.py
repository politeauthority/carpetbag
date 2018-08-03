class Response(object):

    def __init__(self):
        self.status_code = 200
        self.url = 'https://www.example.com/'
        self.text = """
<html>
    <head>
        <title>Here's a title</title>
    </head>
    <body>
    </body>
</html>"""
