import os
from telegraph import Telegraph
from pyzbar.pyzbar import decode
from PIL import Image


# setting
currentFile = __file__
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
telegraph = Telegraph()
telegraph.create_account(short_name='file-converter')


# pyinstaller compile
def pyinstallcommand(message,inputt):
    ofold = f"{str(message.id)}/"
    tfold = f"{str(message.id)}t/"
    basename = inputt.split("/")[-1].split(".")[0]
    out = ofold + basename
    temp = f"{basename}.spec"
    cmd = f'pyinstaller --onefile --distpath {ofold} --workpath {tfold} {inputt}'
    return cmd, out, ofold, tfold, temp


# g++ compile command
def gppcommand(inputt):
    filename = inputt.split("/")[-1].split(".")[0]
    cmd = f'g++ -o {filename} {inputt}'
    return cmd, filename


# scan qr and barcode
def scanner(file):
    data = decode(Image.open(file))
    info = ""
    for ele in data:
        info = info + str(ele[0],encoding="utf-8") + "\n\n"
    return info


# compiling jar command
def warpcommand(inputt,message,optimize=False):
    if not optimize:
        cmd = f'warp4j {inputt} -o warp{message.id}'
    else:
        cmd = f'warp4j {inputt} --no-optimize -o warp{message.id}'

    filename = inputt.split("/")[-1].replace(".jar","")
    filelist = [f'warp{message.id}/{filename}-linux-x64', f'warp{message.id}/{filename}-macos-x64', f'warp{message.id}/{filename}-windows-x64.exe']
    return cmd,f'warp{message.id}/',filelist


# ctmconv 3d file cmd
def ctm3dcommand(inputt,output):
    return f'ctmconv {inputt} {output}'


# ttconv subtiles cmd
def subtitlescommand(inputt,output):
    return f'tt convert -i {inputt} -o {output}'


# calibre cmd
def calibrecommand(inputt,output):
    return f'ebook-convert "{inputt}" "{output}" --enable-heuristics'


# fontforge cmd
def fontforgecommand(inputt,output,message):
    des = f"{dirPath}/{output}"
    cdes = f"{dirPath}/{message.id}-convert.pe"
    text = f'Open(\'{inputt}\')\nGenerate(\'{des}\')'
    with open(f"{message.id}-convert.pe","w") as file:
        file.write(text)
    os.system(f"chmod 777 {message.id}-convert.pe")
    return f'fontforge -script "{cdes}"'


# libreoffice cmd
def libreofficecommand(inputt,new):
    return (
        f'libreoffice --infilter=="writer_pdf_import" --headless --convert-to "{new}":"writer_pdf_Export" "{inputt}" --outdir "{dirPath}"'
        if inputt.split(".")[-1] == 'pdf'
        else f'libreoffice --headless --convert-to "{new}" "{inputt}" --outdir "{dirPath}"'
    )


# tesseract cmd
def tesrctcommand(inputt,out):
    return f'tesseract "{inputt}" {out}'


# ffmpeg cmd
def ffmpegcommand(inputt,output,new):
    return (
        f'ffmpeg -i "{inputt}" -c copy "{output}"'
        if new in ["mp4", "mkv", "mov"]
        and (new != "mov" or ".webm" not in inputt)
        else f'ffmpeg -i "{inputt}" "{output}"'
    )


# magic cmd (imagemagic)
def magickcommand(inputt,output,new):
    #cmd = f'{magick} --appimage-extract-and-run "{inputt}" "{output}"'
    if new == "ico":
        cmd = "convert"
        slist = ["256", "128", "96", "64", "48", "32", "16"]
        for ele in slist:
           toutput = updtname(inputt,f"{ele}.png")
           tcmd = f'convert "{inputt}" -resize {ele}x{ele}\! "{toutput}"'
           os.system(tcmd)
           cmd = f'{cmd} "{toutput}"'
        cmd = f'{cmd} "{output}"'
    else:
        cmd = f'convert "{inputt}" "{output}"'
    return cmd  


# 7zip cmd
def zipcommand(file,message):
    cmd = f'7z x "{file}" -o{message.id}z > {message.id}zl'
    return cmd, f'{message.id}z', f'{message.id}zl'


# get files
def absoluteFilePaths(directory):
    listt = []
    for dirpath,_,filenames in os.walk(directory):
        listt.extend(os.path.abspath(os.path.join(dirpath, f)) for f in filenames)
    return listt


# new file name
def updtname(inputt,new):
    inputt = inputt.split(".")
    inputt[-1] = new
    output = ""
    for ele in inputt:
        output = f"{output}.{ele}"
    output = output[1:]
    print('New Filename will be')
    print(output)
    return output

# image info
def imageinfo(file):
    cmd = f'identify -verbose {file} > "{file}.txt"'
    os.system(cmd)

    with open(f'{file}.txt', "rb") as infile:
        info = str(infile.read())
    os.remove(f'{file}.txt')
   
    info = info.replace(":", ": ")
    info = info.replace("b'","")
    info = info.replace("'","")
    info = info.replace("\\n","<br>")
    
    file = file.split("downloads")[-1]
    if file[0] == '/':
       file = file[1:]
    try:
        response = telegraph.create_page(f'{file.replace("./", "")}', html_content=f"<p>{info}</p>")
    except:
        return "Error in getting Info"
    return response['url']


# video info
def videoinfo(file):
    cmd = f'ffprobe -v quiet -show_format -show_streams "{file}" > "{file}.txt"'
    os.system(cmd)
    with open(f'{file}.txt', "rb") as infile:
        info = str(infile.read())

    os.remove(f'{file}.txt')

    stream = info[10:].split("[/STREAM]")
    try:
        formats = str(stream[1])[10:-12]
    except:
        formats = ""
    stream = stream[0]

    info = formats + stream[2:]
    info = info.replace("=", "     =        ")
    info = info.replace("\\n", "<br>")
    info = info.replace(":", "   ")
    info = info.replace("./", "")

    file = file.split("downloads")[-1]
    if file[0] == "/":
        file = file[1:]
    
    try:
        response = telegraph.create_page(f'{file.replace("./", "")}', html_content=f"<p>{info}</p>")
    except:
        return "Error in getting Info"
    return response["url"]   


# list beautifier
def give_name(data):
    name = "".join(f", {str(i)}" for i in data)
    return name[2:]
