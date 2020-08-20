import sys
from xml.etree import ElementTree
from datetime import datetime
import requests

def getVideoList(url):
	returnTuple = []
	response = requests.get(url)
	data = response.content
	data = data.decode().replace('\n', '')
	names = []
	dates = []
	urls = []
	stats = []
	ratings = []
	author = ""

	# each hash represents 2 % of the progress

	tree=ElementTree.fromstring(data)
	for node in tree.findall("{http://www.w3.org/2005/Atom}title"):
		author = node.text
	for entry in tree.findall("{http://www.w3.org/2005/Atom}entry"):
		for link in entry.findall("{http://www.w3.org/2005/Atom}link"):
			urls.append(link.attrib.get("href"))
		for date in entry.findall("{http://www.w3.org/2005/Atom}published"):
			dates.append(date.text)
		for name in entry.findall("{http://www.w3.org/2005/Atom}title"):
			names.append(name.text)
		for group in entry.findall("{http://search.yahoo.com/mrss/}group"):
			for comm in group.findall("{http://search.yahoo.com/mrss/}community"):
				for stat in comm.findall("{http://search.yahoo.com/mrss/}statistics"):
					stats.append(stat.attrib.get("views"))
				for rating in comm.findall("{http://search.yahoo.com/mrss/}starRating"):
					ratings.append(rating.attrib.get("average"))
	i = 0
	for date in dates:
		returnTuple.append((date, names[i], urls[i], author, stats[i], ratings[i]))
		i+=1
	return returnTuple
	

def main(argv):
	names = []
	urls = []
	videoInfo = []
	with open(argv[1], "r") as f:
		print("Opened {} file".format(argv[1]))
		tree=ElementTree.parse(f)
	for node in tree.findall(".//outline"):
		names.append(node.attrib.get("text"))
		urls.append(node.attrib.get("xmlUrl"))
	names.pop(0)
	urls.pop(0)

	# setting up toolbar [-------------------------------------]
	i = 0.0
	toolbar_width = 50
	print("----------------Start-----------------\n")
	sys.stdout.write("{}".format(("-")*toolbar_width))
	sys.stdout.flush()
	video_count = urls.__len__()

	for url in urls:
		tmpTuple = getVideoList(url)
		for tup in tmpTuple:
			videoInfo.append(tup)
		# Progress Bar #
		sys.stdout.write("\r") # return to start of line
		sys.stdout.flush()
		sys.stdout.write("[")#Overwrite over the existing text from the start
		sys.stdout.write("#"*(int(i)+1))# number of # denotes the progress completed
		sys.stdout.write("-"*(50-int(i)))
		sys.stdout.write(f" {int(i*video_count/toolbar_width)}/{video_count}     ")
		sys.stdout.flush()
		i += toolbar_width/video_count
	print("\n----------------Done------------------")

	videoInfo = sorted(videoInfo, key=lambda videoInfo: videoInfo[0])
	videoInfo = videoInfo[::-1]
	with open(argv[2] if argv.__len__()>2 else "sublist.html", "w") as fhtml:
		fhtml.write("<html>\n")
		fhtml.write("<head>\n")
		fhtml.write("<title>YouTube Subscription Feed (from: {})</title>\n".format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
		fhtml.write("</head>\n")
		fhtml.write("<body>\n")
		fhtml.write("<h1>YouTube Subscription Feed (from: {})</h1>\n".format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
		for video in videoInfo:
			fhtml.write(f"<h2><a href={video[2]}>{video[1]}</a></h2>\n")
			fhtml.write(f"<p>Author: {video[3]}</p>\n")
			fhtml.write(f"<p>{video[0]}</p>\n")
			fhtml.write(f"<p>Views: {video[4]} Rating: {video[5]}</p>\n")
		fhtml.write("\n")
		fhtml.write("</body>\n")
		fhtml.write("</html>\n")
	

if __name__ == "__main__":
	main(sys.argv)
