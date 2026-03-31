import nidaqmx
from nidaqmx.constants import AcquisitionType

class LoggerNI:
    def __init__(self, port_name, daq_frequency):
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(
            port_name,               
            min_val=-0.08, #set accordingly
            max_val=0.08
        )
        self.task.timing.cfg_samp_clk_timing(
            rate=daq_frequency,       
            sample_mode=AcquisitionType.CONTINUOUS
        )

    def read_voltage(self):
        return self.task.read()  

    def close(self):
        self.task.close()


# multiple daqs
