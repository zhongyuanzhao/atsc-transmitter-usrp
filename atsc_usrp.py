# Copyright 2013 Clayton Smith (argilo@gmail.com)
# Copyright 2014 Ryan Tucker (rtucker@gmail.com)
#   (Add UDP streaming support, tweak RRC filter)
# Copyright 2016 Andrew Pracht (prachtaine33@gmail.com), Andrew Schwarz (schwarzyz@gmail.com)
#   (Add USRP sink, use fixed ts file as vedio source)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gnuradio import gr, atsc, blocks, analog, filter
from gnuradio import uhd
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
import sys, os
# import osmosdr

UDP_HOST = "0.0.0.0"
UDP_PORT = 1234

TAPS = 100
streamfile = "./BroadcastStream.ts"

class top_block(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.symbol_rate = 4500000.0 / 286 * 684
        self.pilot_freq = 309441
        self.center_freq = 683000000
        # increase these to get proper transmission
        self.tx_gain = 75
        self.bandwidth = 6000000

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                channels=range(1),
            ),
        )
        self.uhd_usrp_sink_0.set_samp_rate(self.symbol_rate)
        self.uhd_usrp_sink_0.set_center_freq(self.center_freq, 0)
        self.uhd_usrp_sink_0.set_gain(self.tx_gain, 0)
        self.uhd_usrp_sink_0.set_bandwidth(self.bandwidth, 0)

        pad = atsc.pad()
        rand = atsc.randomizer()
        rs_enc = atsc.rs_encoder()
        inter = atsc.interleaver()
        trell = atsc.trellis_encoder()
        fsm = atsc.field_sync_mux()

        v2s = blocks.vector_to_stream(gr.sizeof_char, 1024)
        minn = blocks.keep_m_in_n(gr.sizeof_char, 832, 1024, 4)
        b2f = blocks.uchar_to_float()
        mul = blocks.multiply_const_vff((2,))
        add = blocks.add_const_vff((-7 + 1.25,))
        zero = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)
        # rrc = filter.fir_filter_ccf(1, firdes.root_raised_cosine(0.1, symbol_rate, symbol_rate/2, 0.1152, TAPS))
        rrc = filter.fft_filter_ccc(1, firdes.root_raised_cosine(0.1, self.symbol_rate, self.symbol_rate / 2, 0.1152, TAPS))
        offset = analog.sig_source_c(self.symbol_rate, analog.GR_COS_WAVE, -3000000 + self.pilot_freq, 0.9, 0)
        mix = blocks.multiply_vcc(1)
        f2c = blocks.float_to_complex(1)

        src = blocks.file_source(gr.sizeof_char, streamfile, True)

        ##################################################
        # Connections
        ##################################################
        self.connect(src, pad, rand, rs_enc, inter, trell, fsm, v2s, minn, b2f, mul, add)
        self.connect((add, 0), (f2c, 0))
        self.connect((zero, 0), (f2c, 1))
        self.connect((f2c, 0), (mix, 0))
        self.connect((offset, 0), (mix, 1))
        self.connect(mix, rrc, self.uhd_usrp_sink_0)

    def get_gain(self):
        return self.tx_gain

    def set_gain(self, gain):
        self.tx_gain = gain
        self.uhd_usrp_sink_0.set_gain(self.tx_gain, 0)

    def get_fc(self):
        return self.center_freq

    def set_fc(self, fc):
        self.center_freq = fc
        self.uhd_usrp_sink_0.set_center_freq(self.center_freq, 0)


# --------------------------------------------------------
def set_streamfile(tsfile):
    global streamfile
    streamfile = tsfile


# --------------------------------------------------------
if __name__ == '__main__':
    tb = top_block()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()
