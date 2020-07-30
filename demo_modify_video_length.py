from atom import ATOM

video = open('bruh.mp4', 'r+b')

msb = video.read(2048)
# msb : Most significant block
offset = ATOM.locate(msb)
# where the ATOM header would be
block = ATOM.extract(msb)
# the block (read from the offset)
header = ATOM(block)
# the parsed block
print('[-] Original duration (in seconds): %ss' %
      header.ATOM_DURATION_SENCONDS)
new_duration = float(input('[+] Input new duration (in seconds):'))
new_duration = int(new_duration * header.ATOM_TIMESCALE)
print('[-] Converted to ATOM time stamp "%s"' % new_duration)
header.ATOM_DURATION = new_duration
print('[-] Writing back ATOM header')
# Overwriting the old header
video.seek(offset)
video.write(header())
video.close()
