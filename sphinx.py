#!/usr/bin/env/python
#
# Original script by: Yu-Jie Lin
# http://sites.google.com/site/livibetter/


import os
import time
import audioop
import subprocess
import alsaaudio as alsa
import pocketsphinx as ps

import automaton.client.pyro as thrift_client
import automaton.lib.exceptions as exceptions


filename = 'audio'
volume_threshold = 500


# Records audio to a file until two seconds of 'silence' have passed
# Silence is defined as any audio below volume_threshold
def record_audio(pcm_in, data, vol):
  print 'Recording. Two seconds of silence will commit the command.'
  buf = open(filename, 'w+b')
  time_start = time.time()
  while ((time.time() - time_start) < 2) or (vol > volume_threshold):
    if vol > volume_threshold:
      time_start = time.time()
    buf.write(data)
    l, data = pcm_in.read()
    vol = audioop.max(data, 2)
    time.sleep(.001)
  buf.close()


# Uses Pocketsphinx to decode audio from the default file
def decode_audio():
  print 'Beginning to decode input...'
  buf = open(filename, 'rb')
  d.decode_raw(buf)
  block = d.get_hyp()
  buf.close()
  return block[0]


if __name__ == '__main__':

  client = thrift_client.ClientWrapper("localhost", appname="sphinx")
  client.open()

  client.allowAllServices()
  
  hmdir = "/usr/share/pocketsphinx/model/hmm/wsj1"
  lmd = "/usr/share/pocketsphinx/model/lm/wsj/wlist5o.3e-7.vp.tg.lm.DMP"
  dictd = "/usr/share/pocketsphinx/model/lm/wsj/wlist5o.dic"

  d = ps.Decoder(hmm=hmdir, lm=lmd, dict=dictd)

  # Prepare the CAPTURE device. It must use 16k Hz,
  # little endian, 16 bit signed integer
  pcm_in = alsa.PCM(alsa.PCM_CAPTURE, alsa.PCM_NONBLOCK, 'default')
  pcm_in.setchannels(1)
  pcm_in.setrate(16000)
  pcm_in.setformat(alsa.PCM_FORMAT_S16_LE)
  # Size of block of each read
  pcm_in.setperiodsize(512)

  print
  print 'Waiting for input...'

  while True:
    l, data = pcm_in.read()
    vol = audioop.max(data, 2)
    # enter recording state
    if vol > volume_threshold:
      record_audio(pcm_in, data, vol)
      block = decode_audio()
      print 'Result on decoding on a block:', block
      ret = "Sorry, I don't know how to interpret what you said."
      try:
        ret = client.interpret(block)
      except exceptions.ServiceNotRegisteredError:
        pass
      except exceptions.ClientError as err:
        ret = "Error in client."
      except exceptions.UnknownIntentError:
        ret = "Could not understand your query."
      print ret
      client.interpret('say ' + ret)
      print
      print 'Waiting for input...'
