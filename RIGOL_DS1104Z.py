import visa as vs
import sys
from time import sleep
import numpy as np
import dashboard_functions as dbf
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
        #we need to initialize the channels before setting the memory depth
        #otherwise if someone has on all 4 channels, but we want to sample 1 channel
        #very high, the scope will limit our memory depth because it thinks we're using 
        # more than 1 channel
        self.initialize_channel(channel)
       #to adjust the # of points recorded (depth) we need to have the scope in
        #   Run mode and then change the depth
        self.run()
       #set the memory depth
        self.acquire_depth_set(memDepth)
        self.stop()
       #set the termination
        self.scope.read_termination='\n'


    def initialize_channel(self,channel = [1]):
        analog_channels = [1,2,3,4] #make a list of all the analog channels
        for i in channel:
            self.channel_display_on(i)
            if int(i) in analog_channels:
                analog_channels.remove(int(i)) #remove the active analog channel form the list
        for i in analog_channels:
            self.channel_display_off(i)
    
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
    
    
    

    '''ACQUIRE COMMANDS '''
    def acquire_averages_get(self):
        return self.scope.query(':ACQ:AVER?')
    
    def acquire_depth_get(self):
        return self.scope.query(':ACQ:MDEP?')
        
    def acquire_depth_set(self,num):
        self.scope.write(':ACQ:MDEP '+ str(int(num)))
        
    def acquire_type_get(self):
        return self.scope.query(':ACQ:TYPE?')
    #NORMal, AVERages, PEAK, HRESolution
    def acquire_type_set(self,mode):
        self.scope.write(':ACQ:TYPE '+str(mode))
        
    def acquire_srate_get(self):
        return float(self.scope.query(':ACQ:SRATe?'))


        
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
        
    def trigger_status(self):
        return self.scope.query(':TRIG:STAT?')
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
        
    def single_channel_data(self, start=1, stop= 125000, decimals=2):
        #set the start point
        self.wave_start_point(start)
        #set the stop point
        self.wave_stop_point(stop)
        #get the raw data
        raw = np.array(self.scope.query_ascii_values(':WAV:DATA?', converter='s'))
        #check for data type
        print(type(raw))
        values = raw[1:].astype(float)
        values = np.around(values, decimals = decimals)
        return values
   
    def channel_data_return(self, channel):
        self.stop()
        self.wave_source_set(channel)
        print("Getting data from " + str(self.wave_source_get()))
        memDepth = self.acquire_depth_get()
        queryFormat = self.wave_format_get()
        numQueriesNeeded, maxReadsPerQuery = dbf.calc_query_req(str(queryFormat), memDepth)
        channelData = np.empty([1])
        for i in range(numQueriesNeeded):
            start = (i * maxReadsPerQuery) + 1
            stop = start + maxReadsPerQuery
            if stop > int(self.acquire_depth_get()):
                stop = int(self.acquire_depth_get())
            newData = self.single_channel_data(start = start, stop = stop)
            channelData = np.concatenate((channelData,newData), axis = 0)
        print("Data retrieved from " + str(self.wave_source_get()))
        return channelData
