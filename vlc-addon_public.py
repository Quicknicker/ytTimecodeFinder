#NB
#V0.6

from ast import Break
import sys, re, os, time, argparse as arg
import requests as r

parser = arg.ArgumentParser(description='Add timestamps')
parser.add_argument('-id', '--id', metavar='\'str\'', type=str, help='The ID of an Video.\nIf ID starts with a "-", type a space infront', required=True)
parser.add_argument('-c', '--comments', metavar='\'bool\'', type=bool, help='Search for timecodes in comments')
parser.parse_args()

apiKey = ""                                           # INSERT YOUR YTDL KEY
dir = ''                                              # INSERT THE LOCATION YOUR VIDEOS ARE AT    (also mind line 36)


def run(videoName, timecodes, timecodeNames):
    # Delete special characters from timecodeNames
    for i in range(len(timecodeNames)):
        timecodeNames[i] = re.sub(r'[^A-Z|a-z|\s|\d|#]', '', timecodeNames[i])
        timecodeNames[i] = timecodeNames[i].strip()
        timecodeNames[i] = re.sub(r'(?<=\s)\s', '', timecodeNames[i])

    # Convert timecode to seconds
    for i in range(len(timecodes)):
        if ":" in timecodes[i]:
            min, sek = timecodes[i].split(":")
            timecodes[i] = str(int(min)*60 + int(sek))

    # Create and write the playlist file for vlc
    location = f'			<location>file:///#{videoName}.mp4</location>'  # REPLACE THE '#' WITH THE LOCATION YOUR VIDEOS ARE AT (use '/')

    with open(f'{dir}{videoName}.xspf', 'w') as file:
        string = '<?xml version="1.0" encoding="UTF-8"?>\n'+'<playlist xmlns="http://xspf.org/ns/0/" xmlns:vlc="http://www.videolan.org/vlc/playlist/ns/0/" version="1">\n'+f'	<title>Playlist-{videoName}</title>\n'+'	<trackList>\n'+'		<track>\n'+f'{location}'+'			<extension application="http://www.videolan.org/vlc/playlist/0">\n'+'				<vlc:id>0</vlc:id>\n'+'				<vlc:option>bookmarks=???</vlc:option>\n'+'			</extension>\n'+'		</track>\n'+'	</trackList>\n'+'	<extension application="http://www.videolan.org/vlc/playlist/0">\n'+'		<vlc:item tid="0"/>\n'+'	</extension>\n'+'</playlist>'

        file.write(string)

    integer = 0
    bookmarks = ''
    for code in timecodes:
        bookmarks += '{name=' + timecodeNames[integer] + ',time=' + code + '}'
        integer += 1


    replacement = ''
    changes = ''
    with open(f"{dir}{videoName}.xspf", "r") as f:
        for line in f:
            changes = line.replace('???', bookmarks)
            replacement += changes + '\n'

    with open(f"{dir}{videoName}.xspf", "w") as f:
        f.write(replacement)


def runDecription(videoID, videoName):
    description = response.json()['items'][0]['snippet']['description']
    timecodes = re.findall('\d+:\d+', description)
    timecodeNames = re.findall('(?:(?<=\d{1}:\d{2}\s)|(?<=\d{2}:\d{2}\s)).+', description)

    # Check if timecodes in video description
    if not timecodes:
        print("no timecodes in decription")
        time.sleep(3)
        runComments(videoID, videoName)
        return

    # save the file
    for i in range(2):
        try:
            if timecodes and timecodeNames:
                run(videoName, timecodes, timecodeNames)
            else:
                print('no valid timecodes in description')
                time.sleep(3)
                runComments(videoID, videoName)
                return
        except IndexError:
            print('no valid timecodes in decription')
            time.sleep(3)
            runComments(videoID, videoName)
            #return
        except OSError as e:
            print('name of video consists of unsupportet characters')
            print(e)
            time.sleep(3)
            continue
            #return
        except:
            print("something went wrong")
        break


def runComments(videoID, videoName):
    responses = []
    commentText = []

    response = r.get(f"https://youtube.googleapis.com/youtube/v3/commentThreads?part=id&part=snippet&order=orderUnspecified&videoId={videoID}&key={apiKey}&maxResults=100")

    # if 'nextPageToken' not in response.json():
    responses.append(response.json())
    while 'nextPageToken' in response.json():
        pageToken = response.json()['nextPageToken']
        response = r.get(f"https://youtube.googleapis.com/youtube/v3/commentThreads?part=id&part=snippet&order=orderUnspecified&videoId={videoID}&key={apiKey}&maxResults=100&pageToken={pageToken}")
        responses.append(response.json())


    for res in responses:
        for item in res['items']:
            commentText.append(item['snippet']['topLevelComment']['snippet']['textOriginal'])
    
    matches = [x for x in commentText if re.search('(\d+:\d+:*\d+)+', x)]

    # Check if timecodes in video commends
    if not matches:
        print("no timecodes in commends")
        time.sleep(3)
        return

    timecodeNames = []
    timecodes = []
    for e in matches:
        timecodeNames.append(re.findall('(?:(?<=\d{1}:\d{2}(:\d{1,3})?\s)|(?<=\d{2}:\d{2}(:\d{1,3})?\s)).*', e))
        timecodes.append(re.findall('(\d{1}:\d{2}(:\d{1,3})?)|(\d{2}:\d{2}(:\d{1,3})?)', e))

    timecodeNames = [x for x in timecodeNames if len(x) > 2]
    timecodes = [x for x in timecodes if len(x) > 2]
    for i in range(len(timecodes)):
        timecodes[i] = [(tuple(int(x) if x.isdigit() else x for x in _ if x)) for _ in timecodes[i]]
        for _ in range(len(timecodes[i])):
            timecodes[i][_] = str(timecodes[i][_][0])

    # Get Comment with the most timecodes
    maxT = []
    for e in timecodes:
        if len(e) > len(maxT):
            maxT = e
    maxN = []
    for e in timecodeNames:
        if len(e) > len(maxN):
            maxN = e

    # save the file
    try:
        print(maxT)
        print('\n')
        print(maxN)
        if maxT and maxN:
            run(videoName, maxT, maxN)
        else:
            print('no valid timecodes in comments')
            return
    except IndexError:
        print('no valid timecodes in comments')
        time.sleep(3)
        if os.path.exists(f'{dir}{videoName}.xspf'):
            os.remove(f'{dir}{videoName}.xspf')
        return
    except OSError:
        print('name of video consists of unsupportet characters')
        time.sleep(3)
        return


def convBool(arg):
    ua = str(arg).upper()
    if 'TRUE'.startswith(ua):
       return True
    elif 'FALSE'.startswith(ua):
       return False

def apiRequest(videoID):
    # api request
    response = r.get(f"https://www.googleapis.com/youtube/v3/videos?id={videoID}&key={apiKey}&part=snippet&part=contentDetails")
    videoName = ""
    try:
        videoName = response.json()['items'][0]['snippet']['title']
    except IndexError:
        if re.match(r'^ \-.*', videoID):
            videoID = videoID.strip()
            return apiRequest(videoID)
        else:
            print("video doesn´t exist")
            time.sleep(3)
            exit()
    return videoName, response, videoID



if __name__ == "__main__":
    try:
        for i in range(len(sys.argv)):
            if (sys.argv[i] == '-id' or sys.argv[i] == '--id'):
                videoID = sys.argv[i+1]
                if sys.argv[i] is sys.argv[-1]:
                    raise ValueError('No videoID in arguments')

        videoName, response, videoID = apiRequest(videoID)

        # Delete special characters
        videoName = re.sub(r'[^!-\]a-z\s]', '', videoName)
        videoName = re.sub(r'/|:', '', videoName)
        videoName = videoName.strip()
        videoName = re.sub(r'(?<=\s)\s', '', videoName)
        videoName = re.sub(r'\"', '\'', videoName)

    

        c_arg = False
        for i in range(len(sys.argv)):
            if (sys.argv[i] == '-c' or sys.argv[i] == '--comments'):
                c_arg = True
                if convBool(sys.argv[i+1]) == True:
                    runComments(videoID, videoName)
                    break
                else:
                    runDecription(videoID, videoName)
                    break
        if not c_arg:        
            runDecription(videoID, videoName)

    except ValueError as err:
        print('something went wrong with the userinput\n' + str(err))