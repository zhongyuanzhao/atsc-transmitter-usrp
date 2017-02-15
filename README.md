# atsc-transmitter-usrp
### ATSC Transmitter on USRP
> **Citation**
>- Davis Rempe, Mitchell Snyder, Andrew Pracht, Andrew Schwarz, Tri Nguyen, Mitchel Votrez, Zhongyuan Zhao, and Mehmet C. Vuran, "A Cognitive Radio TV Prototype for Effective TV Spectrum Sharing", in IEEE DySPAN 2017, Mar. 2017, to be appear. 

Step 1: Install GNURadio from source code

> http://gnuradio.org/redmine/projects/gnuradio/wiki/InstallingGRFromSource

Step 2: Change center frequency in line 42 of atsc_usrp.py to a local TV white space channel (channel 49 by default)

> self.center_freq = 683000000

Step 3: Run atsc_usrp.py from python
```
cd /path/to/the/project/
python atsc_usrp.py
```
