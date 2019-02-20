import re
import time
import sys
lineSeparator = java.lang.System.getProperty('line.separator')
appName = sys.argv[0]
AppServers=[]
ActiveNodes=[]

#Function to Stop the Module
def stopApp(cname,node,jvm,appName):
    print "Stopping the Application:", appName, "on", jvm, "of", node, "\n"
    appManager = AdminControl.queryNames('type=ApplicationManager,cell=' + cname + ',node=' + node + ',process=' + jvm + ',*')
    AdminControl.invoke(appManager, 'stopApplication', appName)

#Function to Start the Module    
def startApp(cname,node,jvm,appName):
    appStatus = AdminControl.queryNames('WebSphere:type=Application,name=' + appName + ',process=' + jvm +',*')
    appManager = AdminControl.queryNames('type=ApplicationManager,cell=' + cname + ',node=' + node + ',process=' + jvm + ',*')
    if appStatus == "":
        print "Application:", appName, "is not running on", jvm
        print "So, Starting the Application:", appName, "on", jvm, "of", node, "\n"
        AdminControl.invoke(appManager, 'startApplication', appName)
    else:
        print "Application:", appName, "is already running on", jvm, "\n"

def main():
    cells = AdminConfig.list('Cell').split('\n')
    for cell in cells:
        nodes = AdminConfig.list('Node', cell).split()
        for node in nodes:
            cname = AdminConfig.showAttribute(cell, 'name')
            nname = AdminConfig.showAttribute(node, 'name')
            if re.findall(r"\bDev_Node",nname):
                ActiveNodes.append(nname)
                servs = AdminControl.queryNames('type=Server,cell=' + cname +',node=' + nname + ',*').split()
                for server in servs:
                    sname = AdminControl.getAttribute(server, 'name')
                    if re.findall(r"\bDev_App",sname):
                        AppServers.append(sname)
    for jvm,node in zip(AppServers,ActiveNodes):
        stopApp(cname,node,jvm,appName)
    print "sleeping... for 2 mins"
    time.sleep(120)
    #Zipping the JVM and Node Name 
    for jvm,node in zip(AppServers,ActiveNodes):
        startApp(cname,node,jvm,appName)

if __name__ == "__main__":
    main()