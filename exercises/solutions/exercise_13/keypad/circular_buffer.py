#!/opt/bin/lv_micropython

class CircularBuffer():
    def __init__(self, size):
        """Initialization"""
        self.buf = [None]*size
        self.wr_index = 0
        self.rd_index = 0
        self.size = size
        self.full = False
        self.overrun = False
    
    def write(self, value):
        """write an element element"""
        if self.full:
            print("buffer is full")
            self.overrun = True
            return
        else:
            # enter the data
            # print("write index: ",self.wr_index)
            # print("read index: ",self.rd_index)
            self.buf[self.wr_index] = value
            # increase the write index
            self.wr_index = (self.wr_index +1) % self.size
            # check if the buffer is full
            if self.wr_index == self.rd_index:
                self.full = True

    def read(self):
        ''' read an element '''
        if self.rd_index == self.wr_index and not self.full:
            print("buffer is empty")
            return None
        else:
            val = self.buf[self.rd_index]
            self.rd_index = (self.rd_index +1) % self.size
            self.full=False
            return val

    def available(self):
        ''' check if new data are available in the buffer '''
        if self.rd_index != self.wr_index:
            return True
        else:
            return False
        
    def is_full(self):
        ''' check if the buffer is full '''
        return self.full
        
    def overrun(self):
        ''' check for overrun errors '''
        return self.overrun
    
    def clr_overrun(self):
        ''' clear overrun flag '''
        self.overrun = False

    def flush(self):
        ''' clear the circular buffer '''
        self.wr_index = 0
        self.rd_index = 0
        self.full = False
        self.overrun = False
