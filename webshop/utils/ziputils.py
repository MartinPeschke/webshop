import zipfile
import os, shutil

class RecursiveFileIterator:
    # Great script from Daniel Dittmar,
    # http://www.faqts.com/knowledge-base/view.phtml/aid/6000
    def __init__ (self, *rootDirs):
        self.dirQueue = list (rootDirs)
        self.includeDirs = None
        self.fileQueue = []

    def __getitem__ (self, index):
        while len (self.fileQueue) == 0:
            self.nextDir ()
        result = self.fileQueue [0]
        del self.fileQueue [0]
        return result

    def nextDir (self):
        dir = self.dirQueue [0]   # fails with IndexError, which is fine
                                  # for iterator interface
        del self.dirQueue [0]
        list = os.listdir (dir)
        join = os.path.join
        isdir = os.path.isdir
        for basename in list:
            fullPath = join (dir, basename)
            if isdir (fullPath):
                self.dirQueue.append (fullPath)
                if self.includeDirs:
                    self.fileQueue.append (fullPath)
            else:
                self.fileQueue.append (fullPath)



def zipFolder(folder, toZipfilename):
    file = zipfile.ZipFile(toZipfilename, "w")
    for name in RecursiveFileIterator(folder):
        if os.path.isfile(name):
            file.write(name, name[len(folder):], zipfile.ZIP_DEFLATED)
    file.close()
    return toZipfilename
    
    
    
def unzipToFolder(folder, tmpfile):
    try:
        shutil.rmtree(folder)
        print 'emptied',folder
    except: pass

    file = zipfile.ZipFile(tmpfile, "r")
    print 'Number of files', len(file.infolist())
    for zfile in file.infolist():

        dirname = os.path.join(folder,os.path.dirname(zfile.filename)[1:])
        try: os.makedirs( dirname )
        except: pass

        if zfile.file_size > 0:
            temp = file.read(zfile.filename)
            fname =  os.path.join( dirname, os.path.split(zfile.filename)[1] )
            f = open(fname, "wb").write(temp)
        else:
            print dirname