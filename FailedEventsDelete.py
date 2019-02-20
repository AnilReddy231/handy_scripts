#Python script to delete failed events in Websphere, which are older than a specific date

import com.ibm.wbiserver.manualrecovery.QueryFilters

# lookup the failed event manager
objstr=AdminControl.completeObjectName('WebSphere:*,type=FailedEventManager')
obj=AdminControl.makeObjectName(objstr)

# count the overall number of failed events
fecount=AdminControl.invoke(objstr,"getFailedEventCount")
print "Before discarding failed events"
print fecount


QueryFilter=com.ibm.wbiserver.manualrecovery.QueryFilters() 
QueryFilter.setFilterArray('EVENT_TYPE', ['SCA','JMS','BPC','MQ']) 
dateFilter=java.util.Date("10/30/2018"); 
QueryFilter.setFilter('END_TIME', dateFilter ) 
fecount1=int(fecount)
loop=1
while(loop):
    fecount1=AdminControl.invoke(objstr,"getFailedEventCount")
    # get 100 failed events
    msglist =  AdminControl.invoke_jmx(obj, 'queryFailedEvents',[QueryFilter, 0, 1000],['com.ibm.wbiserver.manualrecovery.QueryFilters', 'int', 'int']) 
    # discard 1000 events in single batch run
    print "Discarding 1000 failed events"
    AdminControl.invoke_jmx(obj,'discardFailedEvents', [msglist],['java.util.List'])
    fecount2=AdminControl.invoke(objstr,"getFailedEventCount")
    if fecount1 == fecount2:
        print "After discarding failed events, the number of failed events:" 
        print fecount1
        loop=0
