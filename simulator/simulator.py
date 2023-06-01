#!/usr/bin/python3

# DISCLAIMER
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import argparse
from encrypt import EncryptDir, DecryptDir
from temp import CreateTempData
from configparser import ConfigParser
import cryptography

print(cryptography.hazmat.backends.openssl.backend.openssl_version_text())

CONFIG="simulator.ini"

parser = argparse.ArgumentParser()
parser.add_argument('--dir', help='Root directory to encrypt')
parser.add_argument('--mode', default='encrypt', choices=['encrypt', 'decrypt'], help='either encrypt or decrypt')
parser.add_argument('--password', required=True, help='Password for encryption/decryption')
args = parser.parse_args()

config = ConfigParser()
config.read(CONFIG)

if args.mode == "encrypt":
    if args.dir:
        directory = args.dir
    else:
        directory = CreateTempData()

    # save the last directory & password
    if not config.has_section('data'):
        config.add_section('data')
    config.set('data', 'temp_dir', directory)
    config.set('data', 'password', args.password)
    with open(CONFIG, "w") as configfile:
        config.write(configfile)

    print(f'Encrypting dir {directory}...')
    count = EncryptDir(directory, args.password)
    print(f'{count} files encrypted under {directory}')
    
elif args.mode == "decrypt":
    if args.dir:
        directory = args.dir
    else:
        # retrieve the last dir used
        directory = config.get('data', 'temp_dir')
    
    print(f'Decrypting dir {directory}...')
    count = DecryptDir(directory, args.password)
    print(f'{count} files decrypted under {directory}')