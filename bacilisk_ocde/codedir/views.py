
from users.models import MyUser
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from pathlib import Path
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import os
import subprocess
from django.urls.base import reverse
import shutil
from django.urls.conf import path
# Create your views here.
def index(request):
    """Processes the GET request on pressing the 'MyFolder" link on the left nav bar on the webpage

    If the user is unsubscribed to the code directory(i.e., user is in Basic plan), then we render codedir/unsubscribed.html
    Else if user is subscribed to the premium plan, then we open the special directory of the user that is created when the registration of user happens.
    Using os.listdir(path) we obtain the list of contents of the current path. Then we separate all dirs from files. Finally we render codedir/index.html along 
    with passing the lists that we just obtained.

    Args:
        GET request requesting the Folder structure of the user.
    Returns:
        The method returns rendering a html page- codedir/index.html with two lists passed to it by the method. These are nothing but the separate lists of
        directories and files. We also pass a variable path, which denotes the present path.
    """
    myuser=MyUser.objects.get(relatedUser=request.user)
    if myuser.Paid_User=='N':
        return render(request, "codedir/unsubscribed.html")
    else:
        string=str(request.path)
        path='.'+string+request.user.username
        listofDirs=os.listdir(path)
        dirs=list()
        files=list()
        for f in listofDirs:
            s=path+'/'+f
            if os.path.isfile(s):
                files.append(f)
            if os.path.isdir(s) and f!='templates':
                if  f!="validation":
                    dirs.append(f)
        return render(request, 'codedir/index.html', {
            "path":path, "dirs":dirs, "files":files
        })

def parsepath(request):
    """Process the GET request from pressing the links of folders/files from codedir/index.html

    There is form actually instead of just a button, in the codedir/index.html. There exists a hidden component in the form which is not visible to the user.
    this stores a string which denotes the path that we will be led to, when we press the link of that particular directory, or file. So, when user presses the button
    corresponding to the directory/file, we POST the path to which we should go also. So, the method first retrieves that path.
    THen uses os.listdir on this path to find the contents of that path. Similar to index function, we create lists and render the codedir/index.html but with this 
    updated data instead. But all this is when we press on a link which is a directory. If it is a file, we render coding/index.html that displays the code, and options to
    run etc...

    Args:
        A GET request that is obtained on pressing links on codedir/index.html
    Returns:
        Reutrns appropriate html pages, based on whether we press the links of direcoried or files.
    """
    givenpath=request.POST['path']
    if os.path.isfile(givenpath):
        code_text=""
        fhand=open(givenpath)
        for line in fhand:
            code_text+=line
        return render(request, "coding/index.html",{
            "path":givenpath, "code":code_text
        })
    else:
        listofDirs=os.listdir(givenpath)
        dirs=list()
        files=list()
        for f in listofDirs:
            s=givenpath+'/'+f
            if os.path.isfile(s):
                files.append(f)
            if os.path.isdir(s):
                dirs.append(f)
        return render(request, 'codedir/index.html', {
            "path":givenpath, "dirs":dirs, "files":files
        })

def newfolder(request):
    """Processes the GPOST request when new Folder button is pressed on codedir/index.html

    It obtains the present path which is a part of the form in codedir/index.html. the new folder is created using os.mkdir(). After that, user is redirected to the
    directory in which the new folder is created..the user will directly be able to see the new folder just created.

    Args:
        The POST request for new folder.
    Returns:
        Returns HttpResponseRedirect to the path initially started from.
    """
    path=request.POST["presentpath"]
    newstr=path[2:]
    folder_name=request.POST['newfoldername']
    f_name=folder_name.replace(" ", "_")
    string=newstr+'/'+f_name
    os.mkdir(string)
    return HttpResponseRedirect(reverse('codedir:index'))

def newfile(request):
    """Processes the POST request when new File button is pressed on codedir/index.html

    It obtains the present path which is a part of the form in codedir/index.html. The new file is created using open() functionality of python. After that,
    user is redirected to the directory in which the new file is created. The user will directly be able to see the new file just created.

    Args:
        The POST request for new file
    Returns:
        Returns HttpResponseRedirect to the path initially started from.
    """
    path=request.POST["presentpath"]
    newstr=path[2:]
    file_name=request.POST['newfilename']
    f_name=file_name.replace(" ", "_")
    string=newstr+'/'+f_name
    open(string, "w+")
    return HttpResponseRedirect(reverse("codedir:index"))

def deletefolder(request):
    """Processes the POST request when delete folder button is pressed on codedir/index.html

    It obtains the present path which is a part of the form in codedir/index.html. Since we need to remove all the inner subfolders also, we use the shutil.rmtree(path)
    functionality of the python. This removes the directory along with all the subfolders. Then user is directed to index of the codedir app.

    Args:
        A POST request from codedir/index.html
    Returns:
        Returns HttpResponseRedirect to the path initially started from.
    """
    path=request.POST["path"]
    shutil.rmtree(path)
    return HttpResponseRedirect(reverse("codedir:index"))

def deletefile(request):
    """Processes the POST request when delete file button is pressed on codedir/index.html

    It obtains the present path which is a part of the form in codedir/index.html. Unlike deleting folders, it is sufficient to 
    delete the file(No subfolders or anything like that). Then user is directed to index of the codedir app.

    Args:
        A POST request from codedir/index.html
    Returns:
        Returns HttpResponseRedirect to the path initially started from.
    """
    path=request.POST["path"]
    os.remove(path)
    return HttpResponseRedirect(reverse("codedir:index"))
