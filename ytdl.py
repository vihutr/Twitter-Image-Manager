import youtube_dl
import os
from pathlib import Path

script_dir = os.path.dirname(__file__)

class VideoDownloader:
    def __init__(self, output_dir='./downloads/', sort=False):
        output_dir = Path(output_dir)
        print(output_dir)
        Path.mkdir(output_dir, parents = True, exist_ok = True)
        self.output_dir = str(output_dir)
        self.sort = sort

    def download_video(self, url):
        ydl = youtube_dl.YoutubeDL({'outtmpl': f'./{self.output_dir}/%(id)s.%(ext)s'})
        url = url.split('?', 1)[0]
        with ydl:
            result = ydl.extract_info(url, download=True)
        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            # Just a video
            video = result
        return(video['url'],video['id'])


    def get_media_url(self, url):
        ydl = youtube_dl.YoutubeDL({'outtmpl': f'./{self.output_dir}/%(id)s.%(ext)s'})
        url = url.split('?', 1)[0]
        with ydl:
            result = ydl.extract_info(url, download=False)
        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            # Just a video
            video = result
        return(video['url'])

    def extract_info(self, url):
        ydl = youtube_dl.YoutubeDL({'outtmpl': f'./{self.output_dir}/%(id)s.%(ext)s'})
        url = url.split('?', 1)[0]
        with ydl:
            result = ydl.extract_info(url, download=False)
        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            # Just a video
            video = result
        return(video['url'],video['id'])
urlvideo = 'https://twitter.com/enarane/status/1599339493940932609'
urlanimg = 'https://twitter.com/testest18683495/status/1599187903821021184'
urlmultivideo = 'https://twitter.com/enarane/status/1590735639808331777?s=46&t=tJPt8eep7HHzZWsoZ-6yqA'
#dl = VideoDownloader()
#dl.extract_info(urlvideo)
#dl.extract_info(urlanimg)
#dl.extract_info(urlmultivideo)
#dl.download_video(urlmultivideo)
