#!/usr/bin/python
import os
import sys
import libs.fingerprint as fingerprint
import argparse
import struct
from argparse import RawTextHelpFormatter
from itertools import zip_longest
from libs.reader_microphone import MicrophoneReader
from libs.db_sqlite import SqliteDatabase

if __name__ == '__main__':

  db = SqliteDatabase()

  seconds = 5#int(args.seconds)

  chunksize = 2**12  # 4096
  channels = 2 # 1=mono, 2=stereo

  record_forever = False

  reader = MicrophoneReader(None)

  reader.start_recording(seconds=seconds,
    chunksize=chunksize,
    channels=channels)

  msg = ' * started recording..'
  print(msg)

  while True:
    bufferSize = int(reader.rate / reader.chunksize * seconds)

    for i in range(0, bufferSize):
        nums = reader.process_recording()
        print('   processing %d of %d..' % (i, bufferSize))

    if not record_forever: break

  reader.stop_recording()

  print(' * recording has been stopped')


  def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return ([_f for _f in values if _f] for values
             in zip_longest(fillvalue=fillvalue, *args))

  data = reader.get_recorded_data()

  print( ' * recorded %d samples' % len(data[0]))


  Fs = fingerprint.DEFAULT_FS
  channel_amount = len(data)

  result = set()
  matches = []

  def find_matches(samples, Fs=fingerprint.DEFAULT_FS):
    hashes = fingerprint.fingerprint(samples, Fs=Fs)
    return return_matches(hashes)

  def return_matches(hashes):
    mapper = {}
    for hash, offset in hashes:
      mapper[hash.upper()] = offset
    values = list(mapper.keys())
    
    for split_values in grouper(values, 1000):
      query = """
        SELECT upper(hash), song_fk, offset
        FROM fingerprints
        WHERE upper(hash) IN (%s)
      """
      query = query % ', '.join('?' * len(split_values))

      x = db.executeAll(query, split_values)
      matches_found = len(x)

      if matches_found > 0:
        msg = '   ** found %d hash matches (step %d/%d)'
        print(msg % (matches_found,len(split_values),len(values)))
      else:
        msg = '   ** not matches found (step %d/%d)'
        print(msg % (len(split_values), len(values)))

      for hash, sid, offset in x:

        offset = struct.unpack('<Q', offset)[0]
        yield (sid,offset - mapper[hash])

  for channeln, channel in enumerate(data):
    msg = '   fingerprinting channel %d/%d'
    print(msg % (channeln+1, channel_amount))

    matches.extend(find_matches(channel))

    msg = '   finished channel %d/%d, got %d hashes'
    print(msg % (channeln+1, channel_amount, len(matches)))

  def align_matches(matches):
    diff_counter = {}
    largest = 0
    largest_count = 0
    song_id = -1

    for tup in matches:
      sid, diff = tup

      if diff not in diff_counter:
        diff_counter[diff] = {}

      if sid not in diff_counter[diff]:
        diff_counter[diff][sid] = 0

      diff_counter[diff][sid] += 1

      if diff_counter[diff][sid] > largest_count:
        largest = diff
        largest_count = diff_counter[diff][sid]
        song_id = sid

    songM = db.get_song_by_id(song_id)

    nseconds = round(float(largest) / fingerprint.DEFAULT_FS *
                     fingerprint.DEFAULT_WINDOW_SIZE *
                     fingerprint.DEFAULT_OVERLAP_RATIO, 5)

    return {
        "SONG_ID" : song_id,
        "SONG_NAME" : songM[1],
        "CONFIDENCE" : largest_count,
        "OFFSET" : int(largest),
        "OFFSET_SECS" : nseconds
    }

  total_matches_found = len(matches)

  print('')

  if total_matches_found > 0:
    msg = ' ** totally found %d hash matches'
    print(msg % total_matches_found)

    song = align_matches(matches)

    msg = ' => song: %s (id=%d)\n'
    msg += '    offset: %d (%d secs)\n'
    msg += '    confidence: %d'

    print(msg % (
      song['SONG_NAME'], song['SONG_ID'],
      song['OFFSET'], song['OFFSET_SECS'],
      song['CONFIDENCE']
    ))
  else:
    print( ' ** not matches found at all')
