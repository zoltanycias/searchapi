README
=======

___ DESCRIPTION ___
Search Engine made in python language. Prepared to implement fuzzy search for unaccent and case-insensitive searches (with lower score on match).


___ INSTALLATION ___

Go to the project root:

$ python3 -m venv myenv
$ . venv/bin/activate
$ pip3 install Whoosh
$ pip3 install Flask
$ python3 apy.py


___ USAGE ___
Copy the text files into "files" folder, which is in the project folder

Run python3 api.py

Open link in web browser

http://127.0.0.1:5000/search?q=lorem,ipsum
