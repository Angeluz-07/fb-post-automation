from services.news_service import get_news
from services.post_service import post_with_url, post_with_img

news = get_news()
i = 3
post_with_url(message=news[i].as_post(), url=news[i].link)

# use post with img
#import pdb; pdb.set_trace()

