import nidaqmx
from nidaqmx.system import System

# Create a system object to access DAQmx system properties
system = System.local()

# Access the device object for DEV3
device = system.devices['Dev3']

# List all analog input channels on DEV3
print("Available Analog Input Channels on DEV3:")
for physical_channel in device.ai_physical_chans:
    print(f"Analog Input Channel: {physical_channel.name}")

