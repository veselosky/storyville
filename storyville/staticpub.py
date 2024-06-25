from genericsite.models import Article, HomePage, Page, Section
from staticpub.models import ModelProducer


class GenericProducer(ModelProducer):
    def get_queryset(self):
        return self.get_model()


class ArticleProducer(ModelProducer):
    def get_model(self):
        return Article
