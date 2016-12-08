import re
from datetime import datetime

month_dict={
    'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'
}

def pubdate_to_datetime(pubdate):
    try:
        date_arr=re.split(r'\s*[,:\s+]\s*',pubdate)
        date_str='%s/%2s/%2s  %s:%s:%s' %(date_arr[3],month_dict[date_arr[2]],date_arr[1],date_arr[4],date_arr[5],date_arr[6])
        date_time=datetime.strptime(date_str,'%Y/%m/%d  %H:%M:%S')
        return date_time
    except:
        return None
