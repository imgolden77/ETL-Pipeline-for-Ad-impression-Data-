import json
import sqlite3
import argparse
from pathlib import Path

def load_json_from_js(p):
    return json.loads(p.read_text(encoding='utf-8')[33:])

def populate_db(adsjson, db):
    """Takes a blob of Twitter ad impression data and pushes it into our database.
    """ 
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        json2db(adsjson, cur)
    except:
        print("There was a problem with the loader. This shouldn't happen")
    conn.commit()
    conn.close()

def json2db(adsjson, cur):

    id=0 #impressionid
    tid=0 #TargetingCriteriaId
    
    for database in adsjson:
        datachunk= database['ad']['adsUserData']['adImpressions']['impressions']
        for data in datachunk:    
            id +=1
            deviceInfo=data['deviceInfo']
            osType=deviceInfo.get('osType')     
            deviceId=deviceInfo.get('deviceId') 
            deviceType=deviceInfo.get('deviceType')
            if deviceId is None and deviceType is None:
                deviceInfoData=[osType, deviceId, deviceType]
            else:
                deviceInfoData=[osType, deviceId+deviceType, deviceType]

            result = cur.execute("SELECT * FROM deviceInfo WHERE deviceId = ?", [deviceInfoData[1]]).fetchall() 
            if result:
                pass   
            else:
                cur.execute("INSERT INTO deviceInfo(osType, deviceId, deviceType) VALUES(?, ?, ?)", deviceInfoData)
                
            #promotedTweetInfo
            if 'promotedTweetInfo' in data:
                promotedTweetInfo=data['promotedTweetInfo']
                tweetId=promotedTweetInfo['tweetId']
                tweetText=promotedTweetInfo['tweetText']
                urls=promotedTweetInfo['urls']
                mediaUrls=promotedTweetInfo['mediaUrls']
                promotedTweetInfoData=[tweetId, tweetText, str(urls), str(mediaUrls)]
                result = cur.execute("SELECT * FROM promotedTweetInfo WHERE tweetId= ?", [promotedTweetInfoData[0]]).fetchall()
                if result:
                    pass   
                else:
                    cur.execute("INSERT INTO promotedTweetInfo(tweetId, tweetText, urls, mediaUrls) VALUES(?, ?, ?, ?)", promotedTweetInfoData)
            else:
                cur.execute("INSERT INTO promotedTweetInfo(tweetId, tweetText, urls, mediaUrls) VALUES(Null, Null, Null, Null)")
            
            #advertiserInfo
            if 'advertiserInfo' in data:
                advertiserInfo=data['advertiserInfo']
                advertiserName=advertiserInfo.get('advertiserName')
                screenName=advertiserInfo.get('screenName')
                advertiserInfoData=[advertiserName, screenName]
                result = cur.execute("SELECT * FROM advertiserInfo WHERE advertiserName= ?", [advertiserInfoData[0]]).fetchall()
                if result:
                    pass   
                else:
                    cur.execute("INSERT INTO advertiserInfo(advertiserName, screenName) VALUES(?, ?)", advertiserInfoData)
            else:
                cur.execute("INSERT INTO advertiserInfo(advertiserName, screenName) VALUES(Null, Null)")

            TargetingCriteria=data['matchedTargetingCriteria']

            for tar in TargetingCriteria:
                tid +=1
                targetingType=tar.get('targetingType')
                targetingValue=tar.get('targetingValue')
                tcd=[tid, targetingType, targetingValue] 
                cur.execute("INSERT INTO TargetingCriteria(id, targetingType, targetingValue) VALUES(?, ?, ?)", tcd)
                mtcd=[id, tid]
                cur.execute("INSERT INTO matchedTargetingCriteria(impression, criteria) VALUES(?, ?)", mtcd)
            
            impressionTime=data.get('impressionTime')

            displayLocation=data.get('displayLocation')
            impressionsData=[id, deviceId, displayLocation, tweetId, impressionTime, advertiserName]
            cur.execute("INSERT INTO impressions(id, device, displayLocation, promotedTweet, impressionTime, advertiser)\
                        VALUES(?, ?, ?, ?, ?, ?)", impressionsData)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load JSON from Twitter's ad-impressions.js into our database.")
    parser.add_argument('--source',  
                        type=Path,
                        default=Path('./ad-impressions.js'),
                        help='path to source file')    
    parser.add_argument('--output', 
                        type=Path,
                        default=Path('./twitterads.db'),
                        help='path to output DB')    
    args = parser.parse_args()
    
    print('Loading JSON.')
    ads_json = load_json_from_js(args.source)
    print('Populating database.')    
    populate_db(ads_json, args.output)
    print('Done')
