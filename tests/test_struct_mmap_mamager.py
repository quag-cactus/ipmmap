from re import A
import pytest
import pathlib
import ctypes
import time
import multiprocessing

from ipmmap import DataStructMmapManager, DataStructMmapEditor, DataStructMmapReader
from ipmmap.exception import ipmmap_error as Err  
from ipmmap.struct import base_struct as bs

class SampleMmapStructure(bs.BaseMmapStructure):
    _fields_ = (
        ('header', bs.MmapStructureHeader),
        ('test_data_int_32', ctypes.c_int32),
        ('test_data_float', ctypes.c_float),
        ('tset_data_string_256', ctypes.c_char * 256),
    )

def run_check_reader_acquirement_proc(conn, structName):
    reader = DataStructMmapReader(structName, mmapDir=pathlib.Path('\\.mmap'))
    # acquire read lock
    status = reader._acquireMmapResource(lock=True, blocking=False)
    if status:
        reader._releaseMmapResource(lock=True)
    conn.send(status)

    return

def run_check_writer_acquirement_proc(conn, structName):
    reader = DataStructMmapEditor(structName, mmapDir=pathlib.Path('\\.mmap'))
    # acquire write lock
    status = reader._acquireMmapResource(lock=True, blocking=False)
    if status:
        reader._releaseMmapResource(lock=True)
    conn.send(status)

    return

def run_reader_proc(conn, structName, key):
    while True:
        if conn.recv() is None:
            print("DONE")
            break
        else:
            with DataStructMmapReader(structName, mmapDir=pathlib.Path('\\.mmap')) as reader:
                conn.send(reader.readData(key))

    return


class TestStructMmapManager:

    @pytest.fixture
    def init_struct_mmap_manager(self):
        self.manager = DataStructMmapManager('SampleMmapStructure', mmapDir=pathlib.Path('\\.mmap'), create=True, force=True)

    @pytest.mark.parametrize('structName, tag, assert_fileName', [
        ('SampleMmapStructure', '', 'SampleMmapStructure_.mmap'),
        ('SampleMmapStructure', 'TAG', 'SampleMmapStructure_TAG.mmap'),
    ])
    def test_mmap_file_name(self, structName, tag, assert_fileName):
        manager = DataStructMmapManager(structName, tag, mmapDir=pathlib.Path('\\.mmap'), create=True, force=True)
        assert manager.mmapFilePath.name == assert_fileName

    def test_read_in_read_lock(self, init_struct_mmap_manager):
        # read lock with main proccess
        reader = DataStructMmapReader('SampleMmapStructure', mmapDir=pathlib.Path('\\.mmap'))
        reader._acquireMmapResource(lock=True, blocking=False)

        # read lock with child process
        parent_conn, child_conn = multiprocessing.Pipe()
        proc = multiprocessing.Process(target=run_check_reader_acquirement_proc, args=(child_conn, 'SampleMmapStructure'))
        proc.start()
        recvVal = parent_conn.recv()
        proc.join()

        # release
        reader._releaseMmapResource(lock=True)

        assert recvVal

    def test_write_in_read_lock(self):
        # read lock with main proccess
        reader = DataStructMmapReader('SampleMmapStructure', mmapDir=pathlib.Path('\\.mmap'))
        reader._acquireMmapResource(lock=True, blocking=False)

        # read lock with child process
        parent_conn, child_conn = multiprocessing.Pipe()
        proc = multiprocessing.Process(target=run_check_writer_acquirement_proc, args=(child_conn, 'SampleMmapStructure'))
        proc.start()
        recvVal = parent_conn.recv()
        proc.join()

        # release
        reader._releaseMmapResource(lock=True)

        assert (not recvVal)
        
    def test_read_in_write_lock(self):
        # write lock with main proccess
        reader = DataStructMmapEditor('SampleMmapStructure', mmapDir=pathlib.Path('\\.mmap'))
        reader._acquireMmapResource(lock=True, blocking=False)

        # read lock with child process
        parent_conn, child_conn = multiprocessing.Pipe()
        proc = multiprocessing.Process(target=run_check_reader_acquirement_proc, args=(child_conn, 'SampleMmapStructure'))
        proc.start()
        recvVal = parent_conn.recv()
        proc.join()

        # release
        reader._releaseMmapResource(lock=True)

        assert (not recvVal)

    def test_write_in_write_lock(self):
        # write lock with main proccess
        reader = DataStructMmapEditor('SampleMmapStructure', mmapDir=pathlib.Path('\\.mmap'))
        reader._acquireMmapResource(lock=True, blocking=False)

        # read lock with child process
        parent_conn, child_conn = multiprocessing.Pipe()
        proc = multiprocessing.Process(target=run_check_writer_acquirement_proc, args=(child_conn, 'SampleMmapStructure'))
        proc.start()
        recvVal = parent_conn.recv()
        proc.join()

        # release
        reader._releaseMmapResource(lock=True)

        assert (not recvVal)

    def test_sync_data_inter_process(self, init_struct_mmap_manager):

        key = 'test_data_int_32'

        parent_conn, child_conn = multiprocessing.Pipe()
        proc = multiprocessing.Process(target=run_reader_proc, args=(child_conn, 'SampleMmapStructure', key))
        proc.start()

        for i in range(10):

            with DataStructMmapEditor('SampleMmapStructure', mmapDir=pathlib.Path('\\.mmap')) as editor:
                editor.writeData(key, i)

            parent_conn.send(i)
            recvVal = parent_conn.recv()
            if not (i == recvVal):
                pytest.fail("data sync error! parent process: {},  child process: {}".format(i, recvVal))

        parent_conn.send(None)

        proc.join()

        assert True

    def test_struct_not_found_error(self):
        dummyStructName = 'NoExistMmapStructure'
        with pytest.raises(Err.StructNotFoundIpMmapError):
            DataStructMmapManager(dummyStructName, mmapDir=pathlib.Path('\\.mmap'), create=True, force=True)

