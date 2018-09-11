from lib import markup
from lib import graphs

class htmlExport():
    def __init__(self,users,softs,paths,allinfo,fname,dirs,failed,domain,emails):
        self.users=users
        self.softs=softs
        self.paths=paths
        self.allinfo=allinfo
        self.fname=fname
        self.dir=dirs
        self.failed=failed
        self.style=""
        self.domain=domain
        self.emails=emails

    def styler(self):
        a="""<style type='text/css'>body {
     background: #e1e5e4  top no-repeat;
 }

h1 { font-family: times, Times New Roman, times-roman, georgia, serif;
    color: #680000;
    margin: 0;
    padding: 0px 0px 6px 0px;
    font-size: 51px;
    line-height: 44px;
    letter-spacing: -2px;
    font-weight: bold;
}

h3 { font-family: times, Times New Roman, times-roman, georgia, serif;
    color: #444;
    margin: 0;
    padding: 0px 0px 6px 0px;
    font-size: 30px;
    line-height: 44px;
    letter-spacing: -2px;
    font-weight: bold;
}

li { font-family: times, Times New Roman, times-roman, georgia, serif;
    color: #444;
    margin: 0;
    padding: 0px 0px 6px 0px;
    font-size: 15px;
    line-height: 15px;
    letter-spacing: 0.4px;

}

h2{
font-family: times, Times New Roman, times-roman, georgia, serif;
        font-size: 48px;
        line-height: 40px;
        letter-spacing: -1px;
        color: #680000 ;
        margin: 0 0 0 0;
        padding: 0 0 0 0;
        font-weight: 100;

}

pre {
overflow: auto;
padding-left: 15px;
padding-right: 15px;
font-size: 11px;
line-height: 15px;
margin-top: 10px;
width: 93%;
display: block;
background-color: #eeeeee;
color: #000000;
max-height: 300px;
}
</style>
        """
        self.style=a

    def writehtml(self):
        page = markup.page()
        page.title("Metagoofil results")
        page.html()
        self.styler()
        page.head(self.style)
        page.head.close()
        page.body()
        page.h2("Metagoofil results")
        page.h3("Results for: " + self.domain)
        graph = graphs.BarGraph('vBar')
	try:
        	graph.values = [len(self.users),len(self.softs),len(self.emails),len(self.paths)]
		graph.labels = ["Usernames","Software","Emails","Paths/Servers"]
		graph.showValues = 1
        	page.body(graph.create())
	except:
		print "graph"
	try:
		page.h3("User names found:")
		page.ul( class_="userslist")
		page.li( self.users, class_="useritem")
		page.ul.close( )
		page.h3("Software versions found:")
	except:
		print "user"
        try:
		page.ul( class_="softlist")
		page.li(self.softs, class_="softitem")
		page.ul.close( )
	except:
		print "email"
	page.h3("E-mails found:")
        if self.emails!=[]:
            page.ul( class_="emailslist")
            page.li(self.emails, class_="emailitem")
            page.ul.close( )
        else:
            page.p("0 results")
        page.h3("Servers and paths found:")
        if self.paths!=[]:
            page.ul( class_="pathslist")
            page.li(self.paths, class_="pathitem")
            page.ul.close( )
        else:
            page.p("0 results")
        page.h3("Files analyzed:")
        page.ul( class_="files")
        for x in self.allinfo:
            page.li(x[0], class_="file")
        page.ul.close()
        page.h2("Files and metadata found:")
        for x in self.allinfo:
            page.h3(x[0])
            page.a("Local copy", class_="link", href=self.dir+"/"+x[0])
            page.pre(x[1])
            page.pre(x[2])
            page.pre(x[3])
            page.pre(x[5])
            page.pre.close()
        page.h2("Failed extractions and reasons")
        for x in self.failed:
            page.pre(x)
        page.body.close()
        page.html.close()
        file = open(self.fname,'w')
        for x in page.content:
            try:
                file.write(x)
            except:
                #print "Exception" +  x # send to logs
                pass
        file.close
        return "ok"
