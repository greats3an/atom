'''
# atom Module

    Unpacks a video's QuickTime ATOM (`moov`) info via its ATOM header / footer

    reference:https://developer.apple.com/library/archive/documentation/QuickTime/QTFF/QTFFChap2/qtff2.html (fig.2-3)
'''
import struct
import io

class _ATOM:
    whences = {
        'ATOM_SIZE': ('I', 4),
        'ATOM_TYPE': ('', 4),
        'ATOM_VERSION': ('B', 1),
        'ATOM_FLAGS': ('', 3),
        'ATOM_CREATION_TIME': ('I', 4),
        'ATOM_MODIFICATION_TIME': ('I', 4),
        'ATOM_TIMESCALE': ('I', 4),
        'ATOM_DURATION': ('I', 4),
        'ATOM_PREFERED_RATE': ('f', 4),
        'ATOM_PREFERED_VOLUME': ('h', 2),
        'ATOM_RESERVED': ('', 10),
        'ATOM_MATRIX_STRUCT':('',36),
        'ATOM_PREVIEW_TIME': ('I', 4),
        'ATOM_PREVIEW_DURATION': ('I', 4),
        'ATOM_POSTER_TIME': ('I', 4),
        'ATOM_SELECTION_TIME': ('I', 4),
        'ATOM_SELECTION_DURATION': ('I', 4),
        'ATOM_CURRENT_TIME': ('I', 4),
        'ATOM_NEXT': ('I', 4),
    }
    
    @staticmethod
    def _locate_whence(key):
        if not key in _ATOM.whences.keys():
            raise KeyError('"%s" is not a valiad ATOM key!' % key)
        offset, whence = 0, ('',0)
        for k, v in _ATOM.whences.items():
            if k == key:
                whence = v
                break
            offset += v[1]
        return offset,whence

    @staticmethod
    def prop(func):
        @property
        def wrapper(self):
            return self._read(func.__name__)

        @wrapper.setter
        def wrapper(self,value):
            # here we go bois
            return self._write(func.__name__, value)
        return wrapper

class ATOM:
    '''
        # ATOM Movie header object
        Parses a standard `mvhd` ATOM header

        Usage:

        - Reading

            `mvhdbytes = ATOM.extract(videoblock)`

            `mvhdheader = ATOM(mvhdbytes)`

        - Writing
        
            `header_offset = ATOM.locate(videoblock)`

            `mvhdheader = ATOM(mvhdbytes)`

            `...(do sth to the header)`

            `new_header = mvhdheader()`

            `videoblock[header_offset:header_offset + len(new_header)] = new_header`

        see:https://developer.apple.com/library/archive/documentation/QuickTime/QTFF/QTFFChap2/qtff2.html
    '''

    def _read(self, key):
        offset,whence = _ATOM._locate_whence(key)    
        # Parses current offset
        mode,length = whence
        block = self.mvhd[offset:offset+length]
        if mode:
            # every atom is small-endian
            return struct.unpack('>'+mode,block)[0]
        else:return block

    def _write(self,key,value):
        offset,whence = _ATOM._locate_whence(key)    
        # Parses current offset
        mode,length = whence
        new_block = value
        if mode:
            # every atom is small-endian
            new_block = struct.pack('>'+mode,new_block)
        else:new_block = bytearray(new_block)
        # Writes new block to local buffer
        self.mvhd[offset:offset+length] = new_block
        
    def __init__(self, mvhd: bytearray):
        '''Store raw mvhd header'''
        self.mvhd = mvhd

    def __call__(self):
        '''Once called,return the current mvhd buffer'''
        return self.mvhd

    # region Staticmethods
    @staticmethod
    def _index(subiter, mainiter) -> int:
        '''
            Indexing a iterable from another iterable
        '''
        for i in range(0, len(mainiter) - len(subiter)):
            if mainiter[i:i+len(subiter)] == subiter:
                return i
        return -1

    @staticmethod
    def locate(pack, header='mvhd') -> int:
        '''
            Locates ATOM Header offset
        '''
        header_index = ATOM._index(header.encode(), pack) - len(header)
        # Locating header
        if header_index < 0:
            raise Exception(f"{header} Header not found")
        return header_index

    @staticmethod
    def extract(pack) -> bytearray:
        '''
            Extracts bytesarray to get mvhd header
        '''
        header_index = ATOM.locate(pack)
        ATOM_SIZE = bytearray(pack[header_index:header_index + 4])
        ATOM_SIZE = struct.unpack('>I', ATOM_SIZE)[0]
        # ATOM size,should be 108 bytes in most cases
        pack = bytearray(pack[header_index:header_index + ATOM_SIZE])
        return pack

    # endregion

    # region Properties

    @_ATOM.prop
    def ATOM_SIZE(self):
        """A 32-bit integer that specifies the number of bytes in this movie header atom"""
        pass

    @_ATOM.prop
    def ATOM_TYPE(self):
        """A 32-bit integer that identifies the atom type; must be set to 'mvhd'."""
        pass

    @_ATOM.prop
    def ATOM_VERSION(self):
        """A 1-byte specification of the version of this movie header atom."""
        pass

    @_ATOM.prop
    def ATOM_FLAGS(self):
        """Three bytes of space for future movie header flags."""
        pass

    @_ATOM.prop
    def ATOM_CREATION_TIME(self):
        """
        A 32-bit integer that specifies the calendar date and time (in seconds since midnight, January 1, 1904) 
        when the movie atom was created. It is strongly recommended that this value should be specified using coordinated universal time (UTC).
        """
        pass

    @_ATOM.prop
    def ATOM_MODIFICATION_TIME(self):
        """
        A 32-bit integer that specifies the calendar date and time (in seconds since midnight, January 1, 1904) 
        when the movie atom was changed. BooleanIt is strongly recommended that this value should be specified using coordinated universal time (UTC).
        """
        pass

    @_ATOM.prop
    def ATOM_TIMESCALE(self):
        """
        A time value that indicates the time scale for this movie—that is, 
        the number of time units that pass per second in its time coordinate system. 
        A time coordinate system that measures time in sixtieths of a second, for example, has a time scale of 60.
        """
        pass

    @_ATOM.prop
    def ATOM_DURATION(self):
        """
        A time value that indicates the duration of the movie in time scale units. 
        Note that this property is derived from the movie’s tracks. The value of this field corresponds to the duration of the longest track in the movie.
        """
        pass

    @_ATOM.prop
    def ATOM_PREFERED_RATE(self):
        """A 32-bit fixed-point number that specifies the rate at which to play this movie. A value of 1.0 indicates normal rate."""
        pass

    @_ATOM.prop
    def ATOM_PREFERED_VOLUME(self):
        """A 16-bit fixed-point number that specifies how loud to play this movie’s sound. A value of 1.0 indicates full volume."""
        pass

    @_ATOM.prop
    def ATOM_RESERVED(self):
        """Ten bytes reserved for use by Apple. Set to 0."""
        pass

    @_ATOM.prop
    def ATOM_MATRIX_STRUCT(self):
        """
        The matrix structure associated with this movie. A matrix shows how to map points from one coordinate space into another. 
        """
        pass

    @_ATOM.prop
    def ATOM_PREVIEW_TIME(self):
        """The time value in the movie at which the preview begins."""
        pass

    @_ATOM.prop
    def ATOM_PREVIEW_DURATION(self):
        """The duration of the movie preview in movie time scale units."""
        pass

    @_ATOM.prop
    def ATOM_POSTER_TIME(self):
        """The time value of the time of the movie poster."""
        pass

    @_ATOM.prop
    def ATOM_SELECTION_TIME(self):
        """The time value for the start time of the current selection."""
        pass

    @_ATOM.prop
    def ATOM_SELECTION_DURATION(self):
        """The duration of the current selection in movie time scale units."""
        pass

    @_ATOM.prop
    def ATOM_CURRENT_TIME(self):
        """The time value for current time position within the movie."""
        pass

    @_ATOM.prop
    def ATOM_NEXT(self):
        """A 32-bit integer that indicates a value to use for the track ID number of the next track added to this movie. Note that 0 is not a valid track ID value."""
        pass
    
    @property
    def ATOM_DURATION_SENCONDS(self):
        return self.ATOM_DURATION / self.ATOM_TIMESCALE
    # endregion


def unpack(block: bytearray) -> ATOM:
    '''Unpacks the ATOM header from a bytearray block'''
    return ATOM(ATOM.extract(block))


if __name__ == "__main__":
    path = input('Media file path >>>').replace("\"", '')
    header = open(path, 'rb').read(256)
    atom = unpack(header)
    def printout():
        print('#'*50)
        for key in dir(atom):
            if key[:4] == 'ATOM':
                print(key.ljust(24), getattr(atom, key))
        print('#'*50)
    input(printout())