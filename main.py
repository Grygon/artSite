#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, url_for, render_template, send_from_directory, request
from fileAccess import APP_STATIC
import os
from time import gmtime, asctime
from csv import writer, reader

app = Flask(__name__)

# For testing purposes
test_images = ["http://placehold.it/1266x1800","http://placehold.it/633x900","http://placehold.it/633x900","http://placehold.it/633x900","http://placehold.it/633x900"]

# Log all requests in csv file. Yes csv. Yes I'm a horrible person
@app.before_request
def log_request():
	ignore = ["static","log","robots.txt","favicon.ico"]
	if request.path.split('/')[1] not in ignore:
		with open(os.path.join(APP_STATIC,"log.csv"),"a",newline="\n") as f:
			print(request.path.split('/')[1])
			w = writer(f)
			w.writerow([str(asctime(gmtime())),str(request.url),str(request.remote_addr)])


@app.route('/log')
def logs():
	with open(os.path.join(APP_STATIC,"log.csv")) as f:
		r = reader(f)
		log = ""
		for row in r:
			log = log + ",".join(row) + "<br>"
		return log

# No crawling pls
@app.route('/robots.txt')
def robots():
	return """User-agent: * <br>
		Disallow: /"""

# Index lands on letter of intent
@app.route('/')
def hello():
	return text('letter')

@app.route('/portfolio')
def portfolio():
	return send_from_directory("static",filename="portfolio.pdf")

# Creates a simple page with text in the "content" space. Reads from static/text/<page>.txt
@app.route("/text/<page>")
def text(page):
	with open(os.path.join(APP_STATIC, 'text/' + page + '.txt'), mode='r',errors='replace',encoding='utf-8') as file:
		data=file.read()
	return render_template("text.html", page=page, data=data)

# The full template has the ability to load both text and images.
# Reads from the relevant folder (static/full/<page>) for .txt files and folders of images.
# Reads text from .txts and creates lists of links for folders of images, then passes all that to the template.
# Images create a modal box on click for viewing of their full size
@app.route("/full/<page>")
def full(page):
	listing = []
	data = []
	path = os.path.join(APP_STATIC, 'full/' + page)

	# Lists everything in the directory
	for f in os.listdir(path):
		listing.append(f)
	listing = sorted(listing)

	for f in listing:
		# Splits for .txt or folders
		if f[-4:] == '.txt': 
			# Read text from document
			with open(os.path.join(path, f), 'r') as file:
				data.append(file.read())
		else:
			# Read all images in folder
			files = os.listdir(os.path.join(path,f))
			files = sorted(files)
			images = []
			# Generate links for each image
			for i in files:
				images.append(url_for("static",filename="full/%s/%s/%s" % (page, f, i)))
			data.append(images)


	return render_template("full.html", page=page, data=data)

# Generate a comic page, which has a main viewer, forward/back buttons and a number of small icons for pages.
# Loads up images from the relevant folder (static/comics/<page>) and passes them into the template
@app.route("/comics/<page>/<num>")
@app.route("/comics/<page>")
def comics(page, num=1):
	# Page index
	num = int(num)
	# Read all images
	path = os.path.join(APP_STATIC, 'comics/' + page )
	# Creates links for each image
	images = [url_for("static",filename="comics/" + page + "/" + f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
	images = sorted(images)
	return render_template("comics.html", page=page, images=images, num=num)

# Special case for the sequential page, since it's unique. Two icons that direct to the comics. 
# Could be abstracted into a "directory" style page if needed, but it's not
@app.route("/sequential")
def listing():
	# Hard coded links for each image. Could abstract w/ some cooperation from comics and maybe a helper function to load
	# images from static. But unneeded for this project.
	comic1Icon = url_for("static",filename="comics/comic1/" + sorted(os.listdir(os.path.join(APP_STATIC, 'comics/comic1' )))[0])
	comic2Icon = url_for("static",filename="comics/comic2/" + sorted(os.listdir(os.path.join(APP_STATIC, 'comics/comic2' )))[0])
	return render_template("sequential.html", icon1=comic1Icon, icon2=comic2Icon, page="sequential")

if __name__ == "__main__":
    app.run()
