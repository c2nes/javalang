
from __future__ import with_statement

class LookAheadIterator(object):
    def __init__(self, iterable):
        self.iterable = iter(iterable)
        self.look_ahead = list()
        self.markers = list()
        self.default = None
        self.value = None

    def __iter__(self):
        return self

    def set_default(self, value):
        self.default = value

    def next(self):
        if self.look_ahead:
            self.value = self.look_ahead.pop(0)
        else:
            self.value = self.iterable.next()

        if self.markers:
            self.markers[-1].append(self.value)

        return self.value

    def look(self, i=0):
        """ Look ahead of the iterable by some number of values with advancing
        past them.

        If the requested look ahead is past the end of the iterable then None is
        returned.

        """

        length = len(self.look_ahead)

        if length <= i:
            try:
                self.look_ahead.extend([self.iterable.next() for _ in range(length, i + 1)])
            except StopIteration:
                return self.default

        self.value = self.look_ahead[i]
        return self.value

    def last(self):
        return self.value

    def __enter__(self):
        self.push_marker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Reset the iterator if there was an error
        if exc_type or exc_val or exc_tb:
            self.pop_marker(True)
        else:
            self.pop_marker(False)

    def push_marker(self):
        """ Push a marker on to the marker stack """
        self.markers.append(list())

    def pop_marker(self, reset):
        """ Pop a marker off of the marker stack. If reset is True then the
        iterator will be returned to the state it was in before the
        corresponding call to push_marker().

        """

        marker = self.markers.pop()

        if reset:
            # Make the values available to be read again
            marker.extend(self.look_ahead)
            self.look_ahead = marker
        elif self.markers:
            # Otherwise, reassign the values to the top marker
            self.markers[-1].extend(marker)
        else:
            # If there are not more markers in the stack then discard the values
            pass

class LookAheadListIterator(object):
    def __init__(self, iterable):
        self.list = list(iterable)

        self.marker = 0
        self.saved_markers = []

        self.default = None
        self.value = None

    def __iter__(self):
        return self

    def set_default(self, value):
        self.default = value

    def next(self):
        try:
            self.value = self.list[self.marker]
            self.marker += 1
        except IndexError:
            raise StopIteration()

        return self.value

    def look(self, i=0):
        """ Look ahead of the iterable by some number of values with advancing
        past them.

        If the requested look ahead is past the end of the iterable then None is
        returned.

        """

        try:
            self.value = self.list[self.marker + i]
        except IndexError:
            return self.default

        return self.value

    def last(self):
        return self.value

    def __enter__(self):
        self.push_marker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Reset the iterator if there was an error
        if exc_type or exc_val or exc_tb:
            self.pop_marker(True)
        else:
            self.pop_marker(False)

    def push_marker(self):
        """ Push a marker on to the marker stack """
        self.saved_markers.append(self.marker)

    def pop_marker(self, reset):
        """ Pop a marker off of the marker stack. If reset is True then the
        iterator will be returned to the state it was in before the
        corresponding call to push_marker().

        """

        saved = self.saved_markers.pop()

        if reset:
            self.marker = saved
        elif self.saved_markers:
            self.saved_markers[-1] = saved

if __name__ == "__main__":
    i = LookAheadIterator(xrange(0, 10000))

    assert i.next() == 0
    assert i.next() == 1
    assert i.next() == 2

    assert i.last() == 2

    assert i.look() == 3
    assert i.last() == 3

    assert i.look(1) == 4
    assert i.look(2) == 5
    assert i.look(3) == 6
    assert i.look(4) == 7

    assert i.last() == 7

    i.push_marker()
    i.next() == 3
    i.next() == 4
    i.next() == 5
    i.pop_marker(True) # reset

    assert i.look() == 3
    assert i.next() == 3

    i.push_marker() #1
    assert i.next() == 4
    assert i.next() == 5
    i.push_marker() #2
    assert i.next() == 6
    assert i.next() == 7
    i.push_marker() #3
    assert i.next() == 8
    assert i.next() == 9
    i.pop_marker(False) #3
    assert i.next() == 10
    i.pop_marker(True) #2
    assert i.next() == 6
    assert i.next() == 7
    assert i.next() == 8
    i.pop_marker(False) #1
    assert i.next() == 9

    try:
        with i:
            assert i.next() == 10
            assert i.next() == 11
            raise Exception()
    except:
        assert i.next() == 10
        assert i.next() == 11

    with i:
        assert i.next() == 12
        assert i.next() == 13
    assert i.next() == 14

    print 'All tests passed'
