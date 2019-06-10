# Install

1) Create virtual environment 
2) Activate
3) pip3 install -r requirements.txt

# Run
This repo holds a collection of scripts for computing parameters to be used
with the PX4 style motor models.

The main script is motor_modeling/capture_motor_data.py

```
usage: Capture motor data [-h] [--port-send PORT_SEND]
                          [--port-receive PORT_RECEIVE] [--motor MOTOR]
                          [--duration DURATION] [--filepath FILEPATH]
                          [--mode MODE]

optional arguments:
  -h, --help            show this help message and exit
  --port-send PORT_SEND
                        The port connected to the aircraft FC.
  --port-receive PORT_RECEIVE
                        The port connected to the Arduino
  --motor MOTOR         The motor ID, starts at 0
  --duration DURATION   The total duration to perform the experiment. NOTE
                        there is a minimum delay of 0.01 seconds between motor
                        commands which must be taken into accourt when
                        computing duration.
  --filepath FILEPATH   The absolute path to the file to log the data
  --mode MODE           One of 'step' or 'ramp'. Ramp will ramp the given
                        motor from zero to full throttle for duration/2 and
                        then full throttle to zero for duration/2. Step will
                        immediately apply motor input to full throttle (2000)
                        and then ramp drown to zero for duration/2
```

Example use,

```
python capture_motor_data.py --port-send COM5 --port-receive COM1 --motor 2 --duration 20 --filepath nf1_ramp_1100.csv --mode ramp
```

Once you have collected your data run the analyzer to plot the results and
generate the neccessary parameters,

```
python3 data_analyzer.py  --ramp-filepath --step-filepath
```



# Circuit Diagram

NOTE! On Ubuntu (All systems?) you must disconnect the RESET pin in order to
upload the sketch.