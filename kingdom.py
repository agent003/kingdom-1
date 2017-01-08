import requests
import time
from slacker import Slacker
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config.ini')
slacker_token = config.get('Slacker','token')
slack = Slacker(slacker_token)
pinged_ip = config.get('URL','value1')


def get_status():
    s_code = 0
    try:
        response = requests.get(pinged_ip)
    except:
        s_code = 111
    if(s_code == 0):
        s_code = response.status_code
    return s_code


def ping_loop_up(frequency,begin_timer,runtime,option):
    time_begin = time.time()
    msg_counter = 0
    while(True):
        status_code = get_status()
        if(time.time() > begin_timer+runtime and option != 'Y' and option !='y'):
            print 'Time Limit Exceeded'
            print 'Last Checked Status:'+str(status_code)
            exit(0)
        if(status_code == 200):
            if(msg_counter == 0):
                print 'Site is Up'
                msg_counter += 1
            pass
        elif(status_code == 111):
            print 'Site is down'
            up_time = time.time() - time_begin
            return up_time
        time.sleep(frequency)

def ping_loop_down(frequency,begin_timer,runtime,option):
    time_begin = time.time()
    msg_counter = 0
    while(True):
        status_code = get_status()
        if(time.time() > begin_timer+runtime and option != 'Y' and option !='y'):
            print 'Time Limit Exceeded'
            print 'Last Checked Status:'+str(status_code)
            exit(0)
        if(status_code == 111):
            if(msg_counter == 0):
                print 'Going in loop. Waiting For site to be fixed'
                msg_counter += 1
            pass
        elif(status_code == 200):
            print 'Site is fixed'
            down_time = time.time() - time_begin
            return down_time
        time.sleep(frequency)

def in_seconds(data):
    seconds = 0
    temp1 = list(data.split(':'))
    seconds += int(temp1[0])*60*60 + int(temp1[1])*60 + int(temp1[0])
    return seconds

def site_down_manager(status,user):
    message = 'site manager:site is '+ status   
    slack.chat.post_message(user, message)   
def main():
    runtime = 0
    begin_timer = 0
    #print '***********Configure Kingdom****************'
    
    frequency_up = in_seconds(config.get('Time','frequency_uptime'))
    frequency_down = in_seconds(config.get('Time','frequency_downtime'))
    option = config.get('Time','run_to_infinity')
    user = config.get('Slacker','developer_id')
    if(option == 'N' or option == 'n'):
        runtime = in_seconds(config.get('Time','runtime'))
        begin_timer = time.time()
    while(True):
        if(get_status() == 200):
            up_time = ping_loop_up(frequency_up,begin_timer,runtime,option)
            print 'Uptime recorded in kingdom app :' + str(up_time) + ' Seconds'
            site_down_manager('down',user)
        if(get_status() == 111):
            down_time = ping_loop_down(frequency_down,begin_timer,runtime,option)
            print 'Downtime recorded in kingdom app :' + str(down_time) + ' Seconds'
            site_down_manager('up',user)  


main()
