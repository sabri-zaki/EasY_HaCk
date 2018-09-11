import urllib, os, sys

class downloader():
    def __init__(self, url, dir):
        self.url = url
        self.dir = dir
        self.filename = str(url.split("/")[-1])

#       def dlProgress(count, blockSize, totalSize):
#               percent = int(count*blockSize*100/totalSize)
#               sys.stdout.write("\r" +"test" + "...%d%%" % percent)
#               sys.stdout.flush()

    def down(self):
        if os.path.exists(self.dir + "/" + self.filename):
            pass
        else:
            try:
                urllib.urlretrieve(self.url, self.dir + "/" + self.filename)
            except:
                print "\t [x] Error downloading " + self.url
                self.filename = ""

    def name(self):
        return self.filename
