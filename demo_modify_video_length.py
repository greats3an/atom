from atom import ATOM
blocksize = 32768
path = input('Media file path >>>').replace("\"", '')
video = open(path, 'r+b')
try:
    msb = video.read(blocksize)
    # msb : Most significant block
    offset = ATOM.locate(msb)
except Exception:
    # Probably no MVHD header was found...from the head
    # Read from the tail,then let's talk
    print("[-] Looking from the tail...")
    video.seek(-blocksize,2)
    msb = video.read(blocksize)
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
video.seek(offset-blocksize,1)
video.write(header())
video.close()
input('[!] Operation complete') 