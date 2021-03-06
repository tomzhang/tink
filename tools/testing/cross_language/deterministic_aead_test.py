# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for tink.tools.testing.python.cli."""

from absl.testing import absltest
from absl.testing import parameterized

import tink
from tink import daead
from tools.testing.cross_language.util import cli_daead
from tools.testing.cross_language.util import cli_tinkey


def setUpModule():
  daead.register()


class DeterministicAeadTest(parameterized.TestCase):

  @parameterized.parameters(('AES256_SIV', ('cc', 'go', 'java', 'python')),)
  def test_encrypt_decrypt(self, key_template, supported_langs):
    keyset_handle = cli_tinkey.generate_keyset_handle(key_template)
    supported_daeads = [
        cli_daead.CliDeterministicAead(lang, keyset_handle)
        for lang in supported_langs
    ]
    unsupported_daeads = [
        cli_daead.CliDeterministicAead(lang, keyset_handle)
        for lang in cli_daead.LANGUAGES
        if lang not in supported_langs
    ]
    for p in supported_daeads:
      plaintext = (
          b'This is some plaintext message to be encrypted using key_template '
          b'%s using %s for encryption.'
          % (key_template.encode('utf8'), p.lang.encode('utf8')))
      associated_data = (
          b'Some associated data for %s using %s for encryption.' %
          (key_template.encode('utf8'), p.lang.encode('utf8')))
      ciphertext = p.encrypt_deterministically(plaintext, associated_data)
      for p2 in supported_daeads:
        output = p2.decrypt_deterministically(ciphertext, associated_data)
        self.assertEqual(output, plaintext)
      for p2 in unsupported_daeads:
        with self.assertRaises(tink.TinkError):
          p2.decrypt_deterministically(ciphertext, associated_data)
    for p in unsupported_daeads:
      with self.assertRaises(tink.TinkError):
        p.encrypt_deterministically(b'plaintext', b'associated_data')

if __name__ == '__main__':
  absltest.main()
