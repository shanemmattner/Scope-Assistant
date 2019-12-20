import visa as vs
import sys
from time import sleep
import numpy as np
"""
{} - optional parameters
 | - seperate multiple parameters
[] - Contents in [] can be omitted
<> - content must be replaced with an effective value
"""




class RIGOL_DS1104Z(): 
        #define class object attributes
    description='class for using the RIGOL DS1104Z scope'
    
    def __init__(self,scopeName='',scope='', memDepth = 600000, sampleRate = 1, numSamples = 0):
        self.scopeName = scopeName  
        self.scope = scope
        
    def get_USB_port(self):
        #instantiate ResourceManager from pyVISA
        rm = vs.ResourceManager('@py')
        #return a list of resources to an array
        available=rm.list_resources()
        #usually the oscilloscope will be the 0th element of the available array
        self.scopeName=available[1]
        #open the oscilloscope, timeout of 5sec, 
        self.scope=rm.open_resource(self.scopeName, timeout=5000, chunk_size=1024000)
          
    def initialize_scope(self,format_type = 'ASC', mode = 'RAW', memDepth = 1200000, channel = 1):
        #get the USB port and name of scope. Open the scope to transmission
        self.get_USB_port()
        #set the format
        self.stop()
        self.wave_format_set(format_type)
        #set the mode
        self.wave_mode_set(mode)
        #to adjust the # of points recorded (depth) we need to have the scope in
        #   Run mode and then change the depth
        self.run()
        #set the memory depth
        self.acquire_depth_set(memDepth)
        self.stop()
        #set the termination
        self.scope.read_termination='\n'
        self.initialize_channel(channel)
    
    def initialize_channel(self,channel = 1):
        self.channel_display_on(channel)
    
    def deinitialize_channel(self, channel):
        self.channel_display_off()
        self.wave_source_get()
    
    '''  COMMAND SYSTEM'''
    def autoscale(self):
        self.scope.write(':AUT')
    
    def clear(self):
        self.scope.write(':CLE')
    
    def run(self):
        self.scope.write(':RUN')
        
    def stop(self):
        self.scope.write(':STOP')
    
    def single(self):
        self.scope.write(':SING')
    
    def Tforce(self):
        self.scope.write(':TFOR')

    '''ACQUIRE COMMANDS '''
    def acquire_averages_get(self):
        return self.scope.query(':ACQ:AVER?')
        
    def acquire_averages_set(self,num):
        self.scope.write(':ACQ:AVER '+str(num))
    
    def acquire_depth_get(self):
        return self.scope.query(':ACQ:MDEP?')
        
    def acquire_depth_set(self,num):
        self.scope.write(':ACQ:MDEP '+ str(num))
        
    def acquire_type_get(self):
        return self.scope.query(':ACQ:TYPE?')
    #NORMal, AVERages, PEAK, HRESolution
    def acquire_type_set(self,mode):
        self.scope.write(':ACQ:TYPE '+str(mode))
        
    def acquire_srate_get(self):
        return float(self.scope.query(':ACQ:SRATe?'))


    '''CALIBRATE COMMANDS'''
    #start calibration
    def start_cal(self):
        self.scope.write(':CAL:STAR')
    #stop calibration
    def quit_cal(self):
        self.scope.write(':CAL:QUIT')
        
    '''CHANNEL COMMANDS'''
    def channel_BWlimit_get(self,channel):
        return self.scope.write(':CHAN' + channel + ':BWL?')
   
    def channel_BWlimit_set(self,channel,lim):
        return self.scope.write(':CHAN' + channel + ':BWL ' + str(lim) + 'M')

    def channel_coupling_get(self,channel):
        return self.scope.write(':CHAN' + channel + ':COUP?')

    def channel_coupling_set(self,channel):
        return self.scope.write(':CHAN' + channel + ':COUP?')
        
    def channel_display_get(self,channel):
        return self.scope.write(':CHAN'+str(channel)+':DISP?')
#        
    def channel_display_on(self,channel):
        self.scope.write(':CHAN'+str(channel)+':DISP ON')  
        
    def channel_display_off(self,channel):
        self.scope.write(':CHAN'+str(channel)+':DISP OFF') 

    #set the channel scale
    def chan_scale_set(self,channel):
        self.scope.write(':CHAN1:SCAL '+str(channel))

    #get the channel scale
    def chan_scale_get(self, channel):
        return self.scope.query(':CHAN'+channel+':SCAL?')
        
    
    '''DISPLAY COMMANDS'''
    #get the channel scale
    def display_data_get(self):
        return self.scope.query(':DISP:DATA?')
        
    def wave_mode_set(self,chan):
        self.scope.write(':WAV:MODE '+str(chan))
        
    def wave_mode_get(self):
        return self.scope.query('WAV:MODE?')

    def wave_format_set(self, frmt):
        self.scope.write(':WAV:FORM '+str(frmt))
        
    def wave_format_get(self):
        return self.scope.query('WAV:FORM?')

        

    def wave_source_set(self,chan):
        self.scope.write(':WAV:SOUR CHAN'+str(chan))
        
    def wave_source_get(self):
        return self.scope.query('WAV:SOUR?')     
        
    def wave_start_point(self,num):
        self.scope.write(':WAV:STAR '+str(num))
        
    def wave_stop_point(self,num):
        self.scope.write(':WAV:STOP '+str(num))
        
    def wave_data_get(self, start=1, stop= 125000, decimals=2):
        #set the start point
        self.wave_start_point(start)
        #set the stop point
        self.wave_stop_point(stop)
        #get the raw data
        raw = np.array(self.scope.query_ascii_values(':WAV:DATA?', converter='s'))
        values = raw[1:].astype(float)
        values = np.around(values, decimals = decimals)
        return values
   
    def channel_data_return(self, channel):
        self.stop()
        self.wave_source_set(channel)
        print("Getting data from " + str(self.wave_source_get()))
        memDepth = self.acquire_depth_get()
        #we can only querry for an amount of data depending on the format of the transmission
        #So we need to query for that format, then query for data accordingly
        querryFormat = self.wave_format_get()
        print("The querry format is "+str(querryFormat))
        if querryFormat == 'BYTE':
            maxReadPerQuerry = 250000
        elif querryFormat == 'WORD':
            maxReadPerQuerry = 125000
        elif querryFormat == 'ASC':
            maxReadPerQuerry = 15625
        else:
            maxReadPerQuerry = 15625
        maxReadPerQuerry = 15625
        numQueriesNeeded = int(int(memDepth) /int( maxReadPerQuerry)) + 1
        channelData = np.empty([1])
        for i in range(numQueriesNeeded):
            start = (i * maxReadPerQuerry) + 1
            stop = start + maxReadPerQuerry
            if stop > int(self.acquire_depth_get()):
                stop = int(self.acquire_depth_get())
            channelData = np.concatenate((channelData,self.wave_data_get(start = start, stop = stop)), axis = 0)
        print("Data retrieved from " + str(self.wave_source_get()))
        return channelData
