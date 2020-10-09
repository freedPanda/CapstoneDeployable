class ResponseMention():
    def __init__(self, thejson):
        self.text = ''
        self.date = ''
        self.tweet_id = ''
        self.user = ''
        self.screen_name = ''
        self.hashtags = ''

        self.extract_data(thejson)

    def extract_data(self, info):
        
        self.text = info['text']
        self.date = self.make_date(info['created_at'])
        self.tweet_id = info['id_str']
        user = info['user']
        self.screen_name = user['screen_name']
        self.hashtags = self.extract_hashtags(info['entities'])

    def extract_hashtags(self,entities):
        hashtags = ''
        hashtags_list = entities['hashtags']
        for obj in hashtags_list:
            hashtags = hashtags + f'{obj["text"]} '
        if len(hashtags) < 2:
            hashtags = None
        return hashtags

    def make_date(self,date):
        m_d = date[4:10]
        y = date[25:30]
        return m_d + y

