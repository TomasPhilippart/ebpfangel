# DISCLAIMER
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import os, time, pyAesCrypt

def EncryptFile(file, password):
    pyAesCrypt.encryptFile(file, file+".aes", password)
    os.remove(file)

def DecryptFile(file, password):
    try:
        pyAesCrypt.decryptFile(file, file.split(".aes")[0], password)
        os.remove(file)
    except ValueError:
        print(f'File {file} cant be decrypted!')

def EncryptDir(directory, password) -> int:
    count = 0
    for dirpath, _dirnames, filenames in os.walk(directory, topdown=False):
        for name in filenames:
            EncryptFile(os.path.join(dirpath, name), password)
            count = count + 1
        time.sleep(0.01) # sleep 10 milliseconds
    return count

def DecryptDir(directory, password) -> int:
    count = 0
    for dirpath, _dirnames, filenames in os.walk(directory, topdown=False):
        for name in filenames:
            DecryptFile(os.path.join(dirpath, name), password)
            count = count + 1
    return count

