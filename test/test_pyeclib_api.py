# Copyright (c) 2013, Kevin Greenan (kmgreen2@gmail.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.  THIS SOFTWARE IS
# PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
# NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import random
from string import ascii_letters, ascii_uppercase, digits
import sys
import tempfile
import unittest
from pyeclib.ec_iface import ECBackendNotSupported
from pyeclib.ec_iface import ECDriverError
from pyeclib.ec_iface import ECInsufficientFragments

from pyeclib.ec_iface import ECDriver, PyECLib_EC_Types
if sys.version < '3':
    from test_pyeclib_c import _available_backends
else:
    from .test_pyeclib_c import _available_backends

if sys.version < '3':
    def b2i(b):
        return ord(b)
else:
    def b2i(b):
        return b


class TestNullDriver(unittest.TestCase):

    def setUp(self):
        self.null_driver = ECDriver(
            library_import_str="pyeclib.core.ECNullDriver", k=8, m=2)

    def tearDown(self):
        pass

    def test_null_driver(self):
        self.null_driver.encode('')
        self.null_driver.decode([])


class TestStripeDriver(unittest.TestCase):

    def setUp(self):
        self.stripe_driver = ECDriver(
            library_import_str="pyeclib.core.ECStripingDriver", k=8, m=0)

    def tearDown(self):
        pass


class TestPyECLibDriver(unittest.TestCase):

    def __init__(self, *args):
        # Create the temp files needed for testing
        self.file_sizes = ["100-K"]
        self.files = {}
        self.num_iterations = 100
        self._create_tmp_files()

        unittest.TestCase.__init__(self, *args)

    def _create_tmp_files(self):
        """
        Create the temporary files needed for testing.  Use the tempfile
        package so that the files will be automatically removed during
        garbage collection.
        """
        for size_str in self.file_sizes:
            # Determine the size of the file to create
            size_desc = size_str.split("-")
            size = int(size_desc[0])
            if size_desc[1] == 'M':
                size *= 1000000
            elif size_desc[1] == 'K':
                size *= 1000

            # Create the dictionary of files to test with
            buf = ''.join(random.choice(ascii_letters) for i in range(size))
            if sys.version_info >= (3,):
                buf = buf.encode('ascii')
            tmp_file = tempfile.NamedTemporaryFile()
            tmp_file.write(buf)
            self.files[size_str] = tmp_file

    def setUp(self):
        # Ensure that the file offset is set to the head of the file
        for _, tmp_file in self.files.items():
            tmp_file.seek(0, 0)

    def tearDown(self):
        pass

    def test_valid_algo(self):
        print("")
        for _type in PyECLib_EC_Types.names():
            # Check if this algo works
            if _type not in _available_backends:
                print("Skipping test for %s backend" % _type)
                continue
            try:
                if _type is 'shss':
                    _instance = ECDriver(k=10, m=4, ec_type=_type)
                else:
                    _instance = ECDriver(k=10, m=5, ec_type=_type)
            except ECDriverError:
                self.fail("%p: %s algorithm not supported" % _instance, _type)

        self.assertRaises(ECBackendNotSupported, ECDriver, k=10, m=5,
                          ec_type="invalid_algo")

    def get_pyeclib_testspec(self, csum="none"):
        pyeclib_drivers = []
        _type1 = 'jerasure_rs_vand'
        if _type1 in _available_backends:
            pyeclib_drivers.append(ECDriver(k=12, m=2, ec_type=_type1,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=11, m=2, ec_type=_type1,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=10, m=2, ec_type=_type1,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=8, m=4, ec_type=_type1,
                                   chksum_type=csum))
        _type2 = 'liberasurecode_rs_vand'
        if _type2 in _available_backends:
            pyeclib_drivers.append(ECDriver(k=12, m=2, ec_type=_type2,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=11, m=2, ec_type=_type2,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=10, m=2, ec_type=_type2,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=8, m=4, ec_type=_type2,
                                   chksum_type=csum))
        _type3_1 = 'flat_xor_hd'
        if _type3_1 in _available_backends:
            pyeclib_drivers.append(ECDriver(k=12, m=6, ec_type=_type3_1,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=10, m=5, ec_type=_type3_1,
                                   chksum_type=csum))
        _type3_2 = 'flat_xor_hd_4'
        if _type3_2 in _available_backends:
            pyeclib_drivers.append(ECDriver(k=12, m=6, ec_type=_type3_2,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=10, m=5, ec_type=_type3_2,
                                   chksum_type=csum))
        _type4 = 'shss'
        if _type4 in _available_backends:
            pyeclib_drivers.append(ECDriver(k=10, m=4, ec_type=_type4,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=20, m=4, ec_type=_type4,
                                   chksum_type=csum))
            pyeclib_drivers.append(ECDriver(k=11, m=7, ec_type=_type4,
                                   chksum_type=csum))
        return pyeclib_drivers

    def test_small_encode(self):
        pyeclib_drivers = self.get_pyeclib_testspec()
        encode_strs = [b"a", b"hello", b"hellohyhi", b"yo"]

        for pyeclib_driver in pyeclib_drivers:
            for encode_str in encode_strs:
                encoded_fragments = pyeclib_driver.encode(encode_str)
                decoded_str = pyeclib_driver.decode(encoded_fragments)

                self.assertTrue(decoded_str == encode_str)

#    def disabled_test_verify_fragment_algsig_chksum_fail(self):
#        pyeclib_drivers = []
#        pyeclib_drivers.append(
#            ECDriver(k=12, m=2, ec_type="jerasure_rs_vand", chksum_type="algsig"))
#        pyeclib_drivers.append(
#            ECDriver(k=12, m=3, ec_type="jerasure_rs_vand", chksum_type="algsig"))
#        pyeclib_drivers.append(
#            ECDriver(k=12, m=6, ec_type="flat_xor_hd", chksum_type="algsig"))
#        pyeclib_drivers.append(
#            ECDriver(k=10, m=5, ec_type="flat_xor_hd", chksum_type="algsig"))
#
#        filesize = 1024 * 1024 * 3
#        file_str = ''.join(random.choice(ascii_letters) for i in range(filesize))
#        file_bytes = file_str.encode('utf-8')
#
#        fragment_to_corrupt = random.randint(0, 12)
#
#        for pyeclib_driver in pyeclib_drivers:
#            fragments = pyeclib_driver.encode(file_bytes)
#            fragment_metadata_list = []
#
#            i = 0
#            for fragment in fragments:
#                if i == fragment_to_corrupt:
#                    corrupted_fragment = fragment[:100] +\
#                        (str(chr((b2i(fragment[100]) + 0x1)
#                                 % 0xff))).encode('utf-8') + fragment[101:]
#                    fragment_metadata_list.append(pyeclib_driver.get_metadata(corrupted_fragment))
#                else:
#                    fragment_metadata_list.append(pyeclib_driver.get_metadata(fragment))
#                i += 1
#
#            self.assertTrue(pyeclib_driver.verify_stripe_metadata(fragment_metadata_list) != -1)
#
#    def disabled_test_verify_fragment_inline_succeed(self):
#        pyeclib_drivers = []
#        pyeclib_drivers.append(
#            ECDriver(k=12, m=2, ec_type="jerasure_rs_vand", chksum_type="algsig"))
#        pyeclib_drivers.append(
#            ECDriver(k=12, m=3, ec_type="jerasure_rs_vand", chksum_type="algsig"))
#        pyeclib_drivers.append(
#            ECDriver(k=12, m=6, ec_type="flat_xor_hd", chksum_type="algsig"))
#        pyeclib_drivers.append(
#            ECDriver(k=10, m=5, ec_type="flat_xor_hd", chksum_type="algsig"))
#
#        filesize = 1024 * 1024 * 3
#        file_str = ''.join(random.choice(ascii_letters) for i in range(filesize))
#        file_bytes = file_str.encode('utf-8')
#
#        for pyeclib_driver in pyeclib_drivers:
#            fragments = pyeclib_driver.encode(file_bytes)
#
#            fragment_metadata_list = []
#
#            for fragment in fragments:
#                fragment_metadata_list.append(
#                    pyeclib_driver.get_metadata(fragment))
#
#            self.assertTrue(
#                pyeclib_driver.verify_stripe_metadata(fragment_metadata_list) == -1)
#

    def check_metadata_formatted(self, k, m, ec_type, chksum_type):

        if ec_type not in _available_backends:
            return

        filesize = 1024 * 1024 * 3
        file_str = ''.join(random.choice(ascii_letters)
                           for i in range(filesize))
        file_bytes = file_str.encode('utf-8')

        pyeclib_driver = ECDriver(k=k, m=m, ec_type=ec_type,
                                  chksum_type=chksum_type)

        fragments = pyeclib_driver.encode(file_bytes)

        f = 0
        for fragment in fragments:
            metadata = pyeclib_driver.get_metadata(fragment, 1)
            if 'index' in metadata:
                self.assertEqual(metadata['index'], f)
            else:
                self.assertTrue(False)

            if 'chksum_mismatch' in metadata:
                self.assertEqual(metadata['chksum_mismatch'], 0)
            else:
                self.assertTrue(False)

            if 'backend_id' in metadata:
                self.assertEqual(metadata['backend_id'], ec_type)
            else:
                self.assertTrue(False)

            if 'orig_data_size' in metadata:
                self.assertEqual(metadata['orig_data_size'], 3145728)
            else:
                self.assertTrue(False)

            if 'chksum_type' in metadata:
                self.assertEqual(metadata['chksum_type'], 'crc32')
            else:
                self.assertTrue(False)

            if 'backend_version' not in metadata:
                self.assertTrue(False)

            if 'chksum' not in metadata:
                self.assertTrue(False)

            if 'size' not in metadata:
                self.assertTrue(False)

            f += 1

    def test_get_metadata_formatted(self):
        self.check_metadata_formatted(12, 2, "jerasure_rs_vand",
                                      "inline_crc32")
        self.check_metadata_formatted(12, 2, "liberasurecode_rs_vand",
                                      "inline_crc32")
        self.check_metadata_formatted(8, 4, "liberasurecode_rs_vand",
                                      "inline_crc32")

    def test_verify_fragment_inline_chksum_fail(self):
        pyeclib_drivers = self.get_pyeclib_testspec("inline_crc32")
        filesize = 1024 * 1024 * 3
        file_str = ''.join(random.choice(ascii_letters) for i in range(filesize))
        file_bytes = file_str.encode('utf-8')

        for pyeclib_driver in pyeclib_drivers:
            fragments = pyeclib_driver.encode(file_bytes)

            fragment_metadata_list = []

            first_fragment_to_corrupt = random.randint(0, len(fragments))
            num_to_corrupt = 2
            fragments_to_corrupt = [
              (first_fragment_to_corrupt + i) % len(fragments) for i in range(num_to_corrupt + 1)
            ]
            fragments_to_corrupt.sort()

            i = 0
            for fragment in fragments:
                if i in fragments_to_corrupt:
                    corrupted_fragment = fragment[:100] +\
                        (str(chr((b2i(fragment[100]) + 0x1)
                                 % 128))).encode('utf-8') + fragment[101:]
                    fragment_metadata_list.append(
                        pyeclib_driver.get_metadata(corrupted_fragment))
                else:
                    fragment_metadata_list.append(
                        pyeclib_driver.get_metadata(fragment))
                i += 1

            expected_ret_value = {"status": -206, 
                                  "reason": "Bad checksum", 
                                  "bad_fragments": fragments_to_corrupt}
            self.assertEqual(
                pyeclib_driver.verify_stripe_metadata(fragment_metadata_list),
                expected_ret_value)

    def test_verify_fragment_inline_chksum_succeed(self):
        pyeclib_drivers = self.get_pyeclib_testspec("inline_crc32")

        filesize = 1024 * 1024 * 3
        file_str = ''.join(random.choice(ascii_letters) for i in range(filesize))
        file_bytes = file_str.encode('utf-8')

        for pyeclib_driver in pyeclib_drivers:
            fragments = pyeclib_driver.encode(file_bytes)

            fragment_metadata_list = []

            for fragment in fragments:
                fragment_metadata_list.append(
                    pyeclib_driver.get_metadata(fragment))

            expected_ret_value = {"status": 0 }

            self.assertTrue(
                pyeclib_driver.verify_stripe_metadata(fragment_metadata_list) == expected_ret_value)

    def test_get_segment_byterange_info(self):
        pyeclib_drivers = self.get_pyeclib_testspec()

        file_size = 1024 * 1024
        segment_size = 3 * 1024

        ranges = [(0, 1), (1, 12), (10, 1000), (0, segment_size-1), (1, segment_size+1), (segment_size-1, 2*segment_size)]

        expected_results = {}

        expected_results[(0, 1)] = {0: (0, 1)}
        expected_results[(1, 12)] = {0: (1, 12)}
        expected_results[(10, 1000)] = {0: (10, 1000)}
        expected_results[(0, segment_size-1)] = {0: (0, segment_size-1)}
        expected_results[(1, segment_size+1)] = {0: (1, segment_size-1), 1: (0, 1)}
        expected_results[(segment_size-1, 2*segment_size)] = {0: (segment_size-1, segment_size-1), 1: (0, segment_size-1), 2: (0, 0)}

        results = pyeclib_drivers[0].get_segment_info_byterange(ranges, file_size, segment_size)

        for exp_result_key in expected_results:
            self.assertIn(exp_result_key, results)
            self.assertTrue(len(results[exp_result_key]) == len(expected_results[exp_result_key]))
            exp_result_map = expected_results[exp_result_key]
            for segment_key in exp_result_map:
                self.assertIn(segment_key, results[exp_result_key])
                self.assertTrue(results[exp_result_key][segment_key] == expected_results[exp_result_key][segment_key])

    def test_get_segment_info(self):
        pyeclib_drivers = self.get_pyeclib_testspec()

        file_sizes = [
            1024 * 1024,
            2 * 1024 * 1024,
            10 * 1024 * 1024,
            10 * 1024 * 1024 + 7]
        segment_sizes = [3 * 1024, 1024 * 1024]
        segment_strings = {}

        #
        # Generate some test segments for each segment size.
        # Use 2 * segment size, because last segment may be
        # greater than segment_size
        #
        char_set = ascii_uppercase + digits
        for segment_size in segment_sizes:
            segment_strings[segment_size] = \
                ''.join(random.choice(char_set) for i in range(segment_size * 2))

        for pyeclib_driver in pyeclib_drivers:
            for file_size in file_sizes:
                for segment_size in segment_sizes:
                    #
                    # Compute the segment info
                    #
                    segment_info = pyeclib_driver.get_segment_info(
                        file_size,
                        segment_size)

                    num_segments = segment_info['num_segments']
                    segment_size = segment_info['segment_size']
                    fragment_size = segment_info['fragment_size']
                    last_segment_size = segment_info['last_segment_size']
                    last_fragment_size = segment_info['last_fragment_size']

                    computed_file_size = (
                        (num_segments - 1) * segment_size) + last_segment_size

                    #
                    # Verify that the segment sizes add up
                    #
                    self.assertTrue(computed_file_size == file_size)

                    encoded_fragments = pyeclib_driver.encode(
                        (segment_strings[segment_size][
                            :segment_size]).encode('utf-8'))

                    #
                    # Verify the fragment size
                    #
                    self.assertTrue(fragment_size == len(encoded_fragments[0]))

                    if last_segment_size > 0:
                        encoded_fragments = pyeclib_driver.encode(
                            (segment_strings[segment_size][
                                :last_segment_size]).encode('utf-8'))

                        #
                        # Verify the last fragment size, if there is one
                        #
                        self.assertTrue(
                            last_fragment_size == len(
                                encoded_fragments[0]))

    def test_rs(self):
        pyeclib_drivers = self.get_pyeclib_testspec()

        for pyeclib_driver in pyeclib_drivers:
            for file_size in self.file_sizes:
                tmp_file = self.files[file_size]
                tmp_file.seek(0)
                whole_file_bytes = tmp_file.read()

                encode_input = whole_file_bytes
                orig_fragments = pyeclib_driver.encode(encode_input)

                for iter in range(self.num_iterations):
                    num_missing = 2
                    idxs_to_remove = []
                    fragments = orig_fragments[:]
                    for j in range(num_missing):
                        idx = random.randint(0, (pyeclib_driver.k +
                                                 pyeclib_driver.m - 1))
                        if idx not in idxs_to_remove:
                            idxs_to_remove.append(idx)

                    # Reverse sort the list, so we can always
                    # remove from the original index
                    idxs_to_remove.sort(key=int, reverse=True)
                    for idx in idxs_to_remove:
                        fragments.pop(idx)

                    #
                    # Test decoder (send copy, because we want to re-use
                    # fragments for reconstruction)
                    #
                    decoded_string = pyeclib_driver.decode(fragments[:])

                    self.assertTrue(encode_input == decoded_string)

                    #
                    # Test reconstructor
                    #
                    reconstructed_fragments = pyeclib_driver.reconstruct(
                        fragments,
                        idxs_to_remove)
                    self.assertTrue(
                        reconstructed_fragments[0] == orig_fragments[
                            idxs_to_remove[0]])

                    #
                    # Test decode with integrity checks
                    #
                    first_fragment_to_corrupt = random.randint(0, len(fragments))
                    num_to_corrupt = min(len(fragments), pyeclib_driver.m + 1)
                    fragments_to_corrupt = [
                      (first_fragment_to_corrupt + i) % len(fragments) for i in range(num_to_corrupt)
                    ]

                    i = 0
                    for fragment in fragments:
                      if i in fragments_to_corrupt:
                        corrupted_fragment = ("0" * len(fragment)).encode('utf-8')
                        fragments[i] = corrupted_fragment
                      i += 1

                    self.assertRaises(ECInsufficientFragments,
                                      pyeclib_driver.decode,
                                      fragments[:], force_metadata_checks=True)

    def get_available_backend(self, k, m, ec_type, chksum_type="inline_crc32"):
        if ec_type[:11] == "flat_xor_hd":
            return ECDriver(k=k, m=m, ec_type="flat_xor_hd",
                            chksum_type=chksum_type)
        elif ec_type in _available_backends:
            return ECDriver(k=k, m=m, ec_type=ec_type, chksum_type=chksum_type)
        else:
            return None

    def test_liberasurecode_insufficient_frags_error(self):
        file_size = self.file_sizes[0]
        tmp_file = self.files[file_size]
        tmp_file.seek(0)
        whole_file_bytes = tmp_file.read()
        for ec_type in ['flat_xor_hd_3', 'liberasurecode_rs_vand']:
            if ec_type in _available_backends:
                pyeclib_driver = self.get_available_backend(
                    k=10, m=5, ec_type=ec_type)
                fragments = pyeclib_driver.encode(whole_file_bytes)
                self.assertRaises(ECInsufficientFragments,
                                  pyeclib_driver.reconstruct,
                                  [fragments[0]], [1, 2, 3, 4, 5, 6])

    def test_min_parity_fragments_needed(self):
        pyeclib_drivers = []
        for ec_type in ['flat_xor_hd_3', 'liberasurecode_rs_vand']:
            if ec_type in _available_backends:
                pyeclib_drivers.append(ECDriver(k=10, m=5, ec_type=ec_type))
                self.assertTrue(
                    pyeclib_drivers[0].min_parity_fragments_needed() == 1)


if __name__ == '__main__':
    unittest.main()
