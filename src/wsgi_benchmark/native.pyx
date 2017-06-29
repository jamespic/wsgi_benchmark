from posix.time cimport clock_gettime, clock_nanosleep, CLOCK_MONOTONIC, CLOCK_THREAD_CPUTIME_ID, timespec
from libc.errno cimport EINTR

cpdef int triangular_nogil(float seconds):
    cdef int i = 1
    cdef int x
    cdef int result
    cdef timespec start_time
    cdef timespec last_time
    with nogil:
        result = clock_gettime(CLOCK_THREAD_CPUTIME_ID, &start_time)
        if result:
            return 0
        while True:
            for x in range(10000):
                i += x
            result = clock_gettime(CLOCK_THREAD_CPUTIME_ID, &last_time)
            if result:
                return 0
            if (last_time.tv_sec - start_time.tv_sec) + (last_time.tv_nsec - start_time.tv_nsec) / 1000000000.0 > seconds:
                return i

cpdef int native_wait(float seconds):
    cdef timespec wait_time
    cdef timespec remain
    cdef long long nsec = <long long>(seconds * 1000000000)
    with nogil:
        wait_time.tv_sec = nsec / 1000000000
        wait_time.tv_nsec = nsec % 1000000000
        while clock_nanosleep(CLOCK_MONOTONIC, 0, &wait_time, &remain) == EINTR:
            wait_time = remain
        return 1
