# DISCLAIMER
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import os, tempfile, shutil, errno

# DIRS = ['/usr/share/perl', '/usr/share/zoneinfo'] (? files)
DIRS = ['/usr/share/zoneinfo'] # (1793 files)

def CreateTempData() -> str:
    # create temp directory
    temp_dir = tempfile.mkdtemp() # return file descriptor

    # copy these directory trees
    for src in DIRS:
        if os.path.exists(src):
            try:
                print(f'Copying {src} into {temp_dir}...')
                shutil.copytree(src, temp_dir, dirs_exist_ok=True)
            except OSError as exc:
                if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                    shutil.copy(src, temp_dir)
                else: raise
    return temp_dir

def DeleteTempData(temp_dir):
    os.remove(temp_dir)