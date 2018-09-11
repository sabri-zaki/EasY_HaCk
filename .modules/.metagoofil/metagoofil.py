from discovery import googlesearch
from extractors import *
import urllib
import os
import downloader
import processor
import sys
import getopt
import warnings
import htmlExport

warnings.filterwarnings("ignore") # To prevent errors from hachoir deprecated functions, need to fix.

print "  /\/\   ___| |_ __ _  __ _  ___   "
print " /    \ / _ \ __/ _` |/ _` |/ _ \   "
print "/ /\/\ \  __/ || (_| | (_| | (_) | "
print "\/    \/\___|\__\__,_|\__, |\___/ File V 2.3 "
print "                      |___/                      "
print " "
print "[-] Metagoofil Ver 2.3  "
print "[-] Developed by sabri zaki "
print "[-] Alpha-Team DZ [EasY_HaCk]   "
print "[-] www.facebook.com/sabri.zaki.31 "
print " \033[94m\n\n"       

def usage():
    print "\n Usage: metagoofil options\n"
    print "         -d: domain to search"
    print "         -t: filetype to download (pdf,doc,xls,ppt,odp,ods,docx,xlsx,pptx)"
    print "         -l: limit of results to search (default 200)"
    print "         -h: work with documents in directory (use \"yes\" for local analysis)"
    print "         -n: limit of files to download"
    print "         -o: working directory (location to save downloaded files)"
    print "         -f: output file\n"
    print " Examples:"
    print "  metagoofil.py -d apple.com -t doc,pdf -l 200 -n 50 -o applefiles -f results.html"
    print "  metagoofil.py -h yes -o applefiles -f results.html (local dir analysis)\n"
    sys.exit()


global limit, start, password, all, localanalysis, dir, failedfiles
limit = 100
start = 0
password = ""
all = []
dir = "test"
def doprocess(argv):
    filelimit = 50
    word = "local"
    localanalysis = "no"
    failedfiles = []
    emails = []
    if len(sys.argv) < 3:
        usage()
    try:
        opts, args = getopt.getopt(argv, "l:d:f:h:n:t:o:")
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt == '-d':
            word = arg
        elif opt == '-t':
            filetypes = []
            if arg.count(",") != 0:
                filetypes = arg.split(",")
            else:
                filetypes.append(arg)
                print filetypes
        elif opt == '-l':
            limit = int(arg)
        elif opt == '-h':
            localanalysis = arg
        elif opt == '-n':
            filelimit = int(arg)
        elif opt == '-o':
            dir = arg
        elif opt == '-f':
            outhtml = arg
    if os.path.exists(dir):
        pass
    else:
        os.mkdir(dir)
    if localanalysis == "no":
        print "\n[-] Starting online search..."
        for filetype in filetypes:
            print "\n[-] Searching for "+ filetype + " files, with a limit of " + str(limit)
            search = googlesearch.search_google(word, limit, start, filetype)
            search.process_files()
            files = search.get_files()
            print "Results: " + str(len(files)) + " files found"
            print "Starting to download " + str(filelimit) + " of them:"
            print "----------------------------------------\n"
            counter = 1
            for x in files:
                if counter <= filelimit:
                    print "[" + str(counter) + "/" + str(filelimit) + "] " + x
                    getfile = downloader.downloader(x, dir)
                    getfile.down()
                    filename = getfile.name()
                    if filename != "":
                        if filetype == "pdf":
                            test = metadataPDF.metapdf(dir + "/" + filename, password)
                        elif filetype == "doc" or filetype == "ppt" or filetype == "xls":
                            test = metadataMSOffice.metaMs2k(dir + "/" + filename)
                            if os.name == "posix":
                                testex = metadataExtractor.metaExtractor(dir + "/" + filename)
                        elif filetype == "docx" or filetype == "pptx" or filetype == "xlsx":
                            test = metadataMSOfficeXML.metaInfoMS(dir + "/" + filename)
                        res = test.getData()
                        if res == "ok":
                            raw = test.getRaw()
                            users = test.getUsers()
                            paths = test.getPaths()
                            soft = test.getSoftware()
                            email = []
                            if filetype == "pdf" or filetype == "docx":
                                res = test.getTexts()
                                if res == "ok":
                                    email = test.getEmails()
                                    for em in email:
                                        emails.append(em)
                                else:
                                    email = []
                                    failedfiles.append(x + ":" + str(res))
                            respack=[x, users, paths, soft, raw, email]
                            all.append(respack)
                        else:
                            failedfiles.append(x + ":" + str(res))
                            print "\t [x] Error in the parsing process" #A error in the parsing process
                    else:
                        pass
                counter += 1
    else:
        print "[-] Starting local analysis in directory " + dir
        dirList = os.listdir(dir)
        print dirList
        for filename in dirList:
            if filename != "":
                filetype = str(filename.split(".")[-1])
                if filetype == "pdf":
                    test = metadataPDF.metapdf(dir + "/" + filename, password)
                elif filetype == "doc" or filetype == "ppt" or filetype == "xls":
                    print "doc"
                    test = metadataMSOffice.metaMs2k(dir + "/" + filename)
                    if os.name == "posix":
                        testex = metadataExtractor.metaExtractor(dir + "/" + filename)
                elif filetype == "docx" or filetype == "pptx" or filetype == "xlsx":
                    test = metadataMSOfficeXML.metaInfoMS(dir + "/" + filename)
                res = test.getData()
                if res == "ok":
                    raw = test.getRaw()
                    users = test.getUsers()
                    paths = test.getPaths()
                    soft = test.getSoftware()
                    if (filetype == "doc" or filetype == "xls" or filetype == "ppt") and os.name=="posix":
                        testex.runExtract()
                        testex.getData()
                        paths.extend(testex.getPaths())
                        respack = [filename, users, paths, soft, raw, email]
                        all.append(respack)
                    else:
                        failedfiles.append(filename + ":" + str(res))
                        print "[x] Error in the parsing process"  # A error in the parsing process

                    if filetype == "docx" or filetype == "pdf":
                        res = test.getTexts()
                        if res == "ok":
                            email = test.getEmails()
                            for x in email:
                                emails.append(x)
                        else:
                            failedfiles(filename + ":" + str(res))
                    else:
                        print "pass"
            else:
                pass
    print "processing"
    proc = processor.processor(all)
    userlist = proc.sort_users()
    softlist = proc.sort_software()
    pathlist = proc.sort_paths()
    try:
        html = htmlExport.htmlExport(userlist, softlist, pathlist, all, outhtml, dir, failedfiles, word, emails)
        save = html.writehtml()
    except Exception, e:
        print e
        print "Error creating the file"
    print "\n[+] List of users found:"
    print "--------------------------"
    for x in userlist:
        print x
    print "\n[+] List of software found:"
    print "-----------------------------"
    for x in softlist:
        print x
    print "\n[+] List of paths and servers found:"
    print "---------------------------------------"
    for x in pathlist:
        print x
    print "\n[+] List of e-mails found:"
    print "----------------------------"
    for x in emails:
        print x
    #print "\n[+] List of errors:"
    #print "---------------------"
    #for x in failedfiles:
    #   print x

if __name__ == "__main__":
    try: 
    	doprocess(sys.argv[1:])
    except KeyboardInterrupt:
        print "Process interrupted by user."
    except:
        sys.exit()
