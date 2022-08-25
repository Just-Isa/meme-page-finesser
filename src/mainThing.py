import tweepy, sys, re, videoDownloader, os
from unicodedata import name
from cv2 import split
from pyparsing import dictOf, null_debug_action
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

auth = tweepy.OAuth1UserHandler(
    os.getenv('api'), os.getenv('apikeysecret'),
    os.getenv('access'), os.getenv('accesssecret')
)

if len(sys.argv) < 4 or len(sys.argv) > 5:
    print("Need User-ID or @ First use either:")
    print("python .\origin.py -i user-id")
    print("python .\origin.py -s screen-name-without-@")
    print("add -f for finessing memes (videos) -p for person")
    print("add -d to download them instantly aswell")
    sys.exit(1)

api = tweepy.API(auth)

def recursiveTextTruncater(tweet, index=1):
    if tweet.in_reply_to_status_id is None:
        return tweet.text + "    |" + tweet.user.name , index, 1
    if index == 0:
        return re.sub('@\w*\w',"",tweet.text) + '\n-----------------------------------------------------------------------------------------'
    if index >= 5:
        return tweet.text, 0, 0
    try:
        tweetAbove, index, totallyBackwards = recursiveTextTruncater(api.get_status(tweet.in_reply_to_status_id), index+1)        
        tweetAbove = tweetAbove + '\n'
        for _ in range(totallyBackwards):
            tweetAbove = tweetAbove + '| '
        tweetAbove = tweetAbove + tweet.text + "    |" + tweet.user.name

        if totallyBackwards+1 == index:
            return re.sub('@\w*\w',"",tweetAbove) + '\n-----------------------------------------------------------------------------------------'
        
        return tweetAbove, index, totallyBackwards+1    
    except tweepy.NotFound:
        return "", 0, 0
    except tweepy.Forbidden:
        return "", 0, 0            


if sys.argv[1] == '-i':
    user = api.get_user(user_id=sys.argv[2])
elif sys.argv[1] == '-s':
    user = api.get_user(screen_name=sys.argv[2])

try:
    print("Getting every Tweet of user: " + user.name + " | @" + user.screen_name)
    if sys.argv[1] == '-i':
        timeline = api.user_timeline(user_id=sys.argv[2],count=200,include_rts=False)
    elif sys.argv[1] == '-s':
        timeline = api.user_timeline(screen_name=sys.argv[2],count=20,include_rts=False)

    test = open('csvs/'+user.name+'.csv', 'w', encoding='utf-8')
    if sys.argv[3] != None and sys.argv[3] == '-f':
        for i in tqdm(range(len(timeline))):
            if 'media' not in timeline[i].entities.keys():
                continue
            if 'video' in timeline[i].entities['media'][0]['expanded_url']:
                test.write(timeline[i].entities['media'][0]['expanded_url'])
                test.write('\n')
    elif sys.argv[3] != None and sys.argv[3] == '-p':
        for i in tqdm(range(len(timeline))):
            if timeline[i].in_reply_to_status_id is not None:
                try:
                    test.write(recursiveTextTruncater(timeline[i]))
                    test.write('\n')
                    test.write('\n')
                except TypeError:
                    test.write("Deleted Tweet")
                    test.write('\n')
                    test.write('\n')
    else:
        test.close()
        print("Unknown option: " + sys.argv[3])
        exit()
    test.close()

    if len(sys.argv) == 5:
        if (sys.argv[4] == '-d'):
            for line in open('csvs/'+user.name+'.csv', 'r'):
                videoDownloader.submitall(line, user.name)

finally:
    print("Done")

