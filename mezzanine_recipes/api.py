import re
import math

from django.conf.urls.defaults import url
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q
from django.http import Http404
from django.utils import simplejson

from mezzanine.conf import settings
from mezzanine.generic.models import ThreadedComment, AssignedKeyword, Keyword, Rating
from mezzanine.blog.models import BlogCategory
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.utils.timezone import now

from tastypie import fields
from tastypie.paginator import Paginator as TastyPaginator
from tastypie.resources import ModelResource
from tastypie.throttle import CacheDBThrottle
from tastypie.utils import trailing_slash
from tastypie.serializers import Serializer
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization, ReadOnlyAuthorization
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField

import html2text

from .models import BlogProxy, Recipe, BlogPost, Ingredient, WorkingHours, CookingTime, RestPeriod
from .fields import DIFFICULTIES, UNITS


class CamelCaseJSONSerializer(Serializer):
    formats = ['json']
    content_types = {
        'json': 'application/json',
    }

    def to_json(self, data, options=None):
        # Changes underscore_separated names to camelCase names to go from python convention to javacsript convention
        data = self.to_simple(data, options)

        def underscoreToCamel(match):
            return match.group()[0] + match.group()[2].upper()

        def camelize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(r"[a-z]_[a-z]", underscoreToCamel, key)
                    new_dict[new_key] = camelize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = camelize(data[i])
                return data
            return data

        camelized_data = camelize(data)

        return simplejson.dumps(camelized_data, sort_keys=True)

    def from_json(self, content):
        # Changes camelCase names to underscore_separated names to go from javascript convention to python convention
        data = simplejson.loads(content)

        def camelToUnderscore(match):
            return match.group()[0] + "_" + match.group()[1].lower()

        def underscorize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(r"[a-z][A-Z]", camelToUnderscore, key)
                    new_dict[new_key] = underscorize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = underscorize(data[i])
                return data
            return data

        underscored_data = underscorize(data)

        return underscored_data



class RestKitPaginator(TastyPaginator):
    def page(self):
        output = super(RestKitPaginator, self).page()
        output['meta']['pageNumber'] = int(output['meta']['offset'] / output['meta']['limit']) + 1 if self.limit > 0 else 1
        output['meta']['totalPages'] = math.ceil(float(output['meta']['total_count']) / output['meta']['limit']) if self.limit > 0 else 1
        return output



class CategoryResource(ModelResource):
    posts = fields.ToManyField('mezzanine_recipes.api.PostResource', 'blogposts')

    class Meta:
        queryset = BlogCategory.objects.all()
        resource_name = "categories"
        fields = ['id', 'title',]
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        limit = 0
        throttle = CacheDBThrottle()
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()

    def get_object_list(self, request, *args, **kwargs):
        return BlogCategory.objects.filter(Q(blogposts__publish_date__lte=now()) | Q(blogposts__publish_date__isnull=True),
                                           Q(blogposts__expiry_date__gte=now()) | Q(blogposts__expiry_date__isnull=True),
                                           Q(blogposts__status=CONTENT_STATUS_PUBLISHED)).distinct()

    def alter_list_data_to_serialize(self, request, data):
        data['categories'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['categories']
        del data['categories']
        return data



class BlogPostResource(ModelResource):
    categories = fields.ToManyField('mezzanine_recipes.api.CategoryResource', 'categories', full=True)

    class Meta:
        queryset = BlogPost.secondary.published().order_by('-publish_date')
        resource_name = "blog"
        fields = ['id', 'title', 'featured_image', 'description', 'publish_date', 'allow_comments', 'comments_count', 'rating_average', 'rating_count', 'modified_date',]
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        throttle = CacheDBThrottle()
        filtering = {
            "publish_date": ('gt',),
        }
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        limit = 5
        paginator_class = RestKitPaginator

    def dehydrate_featured_image(self, bundle):
        if bundle.data['featured_image']:
            return settings.MEDIA_URL+bundle.data['featured_image']
        else:
            return None

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
        ]

    def alter_list_data_to_serialize(self, request, data):
        data['blogs'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['blogs']
        del data['blogs']
        return data

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        sqs = BlogPost.objects.search(request.GET.get('q', ''))
        paginator = Paginator(sqs, 20)

        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404(_("Sorry, no results on that page."))

        objects = []

        for result in page.object_list:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
            }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)



class RecipeResource(ModelResource):
    categories = fields.ToManyField('mezzanine_recipes.api.CategoryResource', 'categories', full=True)
    ingredients = fields.ToManyField('mezzanine_recipes.api.IngredientResource', 'ingredients', full=True)
    working_hours = fields.ToOneField('mezzanine_recipes.api.WorkingHoursResource', 'working_hours', full=True, null=True)
    cooking_time = fields.ToOneField('mezzanine_recipes.api.CookingTimeResource', 'cooking_time', full=True, null=True)
    rest_period = fields.ToOneField('mezzanine_recipes.api.RestPeriodResource', 'rest_period', full=True, null=True)

    class Meta:
        queryset = Recipe.secondary.published().order_by('-publish_date')
        resource_name = "recipe"
        fields = ['id', 'title', 'featured_image', 'summary', 'content', 'portions', 'difficulty', 'publish_date', 'allow_comments', 'comments_count', 'rating_average', 'rating_count', 'modified_date',]
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        throttle = CacheDBThrottle()
        filtering = {
            "publish_date": ('gt',),
        }
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        limit = 5
        paginator_class = RestKitPaginator

    def dehydrate_featured_image(self, bundle):
        if bundle.data['featured_image']:
            return settings.MEDIA_URL+bundle.data['featured_image']
        else:
            return None

    def dehydrate_difficulty(self, bundle):
        if bundle.data['difficulty']:
            return dict(DIFFICULTIES)[bundle.data['difficulty']]
        else:
            return ""

    def dehydrate(self, bundle):
        content = bundle.data['content']
        bundle.data['description'] = re.sub("\n+$", "", re.sub(" +\* ", "- ", html2text.html2text(content)))
        del bundle.data['content']
        return bundle

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
        ]

    def alter_list_data_to_serialize(self, request, data):
        data['recipes'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['recipes']
        del data['recipes']
        return data

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        sqs = Recipe.objects.search(request.GET.get('q', ''))
        paginator = Paginator(sqs, 20)

        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404(_("Sorry, no results on that page."))

        objects = []

        for result in page.object_list:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
            }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)



class PostResource(ModelResource):
    categories = fields.ToManyField('mezzanine_recipes.api.CategoryResource', 'categories', full=True)

    class Meta:
        queryset = BlogProxy.secondary.published().order_by('-publish_date')
        resource_name = "post"
        fields = ['id', 'title', 'featured_image', 'description', 'publish_date', 'allow_comments', 'comments_count', 'rating_average', 'rating_count', 'modified_date',]
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        throttle = CacheDBThrottle()
        filtering = {
            "publish_date": ('gt',),
        }
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        limit = 5
        paginator_class = RestKitPaginator

    def dehydrate_featured_image(self, bundle):
        if bundle.data['featured_image']:
            return settings.MEDIA_URL+bundle.data['featured_image']
        else:
            return None

    def dehydrate(self, bundle):
        if isinstance(bundle.obj, BlogPost):
            blog_res = BlogPostResource()
            rr_bundle = blog_res.build_bundle(obj=bundle.obj, request=bundle.request)
            bundle.data = blog_res.full_dehydrate(rr_bundle).data
        elif isinstance(bundle.obj, Recipe):
            recipe_res = RecipeResource()
            br_bundle = recipe_res.build_bundle(obj=bundle.obj, request=bundle.request)
            bundle.data = recipe_res.full_dehydrate(br_bundle).data
        return bundle

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
        ]

    def alter_list_data_to_serialize(self, request, data):
        data['posts'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['posts']
        del data['posts']
        return data

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        sqs = BlogProxy.secondary.search(request.GET.get('q', ''))
        paginator = Paginator(sqs, 20)

        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404(_("Sorry, no results on that page."))

        objects = []

        for result in page.object_list:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
            }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)



class CommentResource(ModelResource):
    replied_to = fields.ToOneField('mezzanine_recipes.api.CommentResource', 'replied_to', null=True)
    content_object = GenericForeignKeyField({
        BlogProxy: PostResource,
        BlogPost: BlogPostResource,
        Recipe: RecipeResource
    }, 'content_object')

    class Meta:
        queryset = ThreadedComment.objects.visible()
        resource_name = "comments"
        fields = ['id', 'object_pk', 'comment', 'submit_date', 'user_name', 'user_email', 'user_url', 'replied_to',]
        list_allowed_methods = ['get', 'post',]
        detail_allowed_methods = ['get',]
        throttle = CacheDBThrottle()
        filtering = {
            'object_pk': ('exact',),
            }
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        limit = 0

    def dehydrate_user_email(self, bundle):
        return None

    def dehydrate_user_url(self, bundle):
        return None

    def alter_list_data_to_serialize(self, request, data):
        data['comments'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['comments']
        del data['comments']
        return data



class RatingResource(ModelResource):
    post = GenericForeignKeyField({
        BlogProxy: PostResource,
        BlogPost: BlogPostResource,
        Recipe: RecipeResource
    }, 'content_object')

    class Meta:
        queryset = Rating.objects.all()
        resource_name = "rating"
        fields = ['id', 'object_pk', 'value',]
        list_allowed_methods = ['get', 'post',]
        detail_allowed_methods = ['get',]
        throttle = CacheDBThrottle()
        filtering = {
            'object_pk': ('exact',),
            }
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        limit = 0

    def alter_list_data_to_serialize(self, request, data):
        data['ratings'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['ratings']
        del data['ratings']
        return data



class KeywordResource(ModelResource):
    keyword = fields.ToManyField('mezzanine_recipes.api.AssignedKeywordResource', 'assignments')

    class Meta:
        queryset = Keyword.objects.all()
        resource_name = "keywords"
        fields = ['id', 'title']
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        limit = 0
        throttle = CacheDBThrottle()
        filtering = {
            'title': ('exact',),
            }
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()

    def alter_list_data_to_serialize(self, request, data):
        data['keywords'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['keywords']
        del data['keywords']
        return data



class AssignedKeywordResource(ModelResource):
    assignments = fields.ToOneField('mezzanine_recipes.api.KeywordResource', 'keyword', full=True)
    post = GenericForeignKeyField({
        BlogProxy: PostResource,
        BlogPost: BlogPostResource,
        Recipe: RecipeResource
    }, 'content_object')

    class Meta:
        queryset = AssignedKeyword.objects.all()
        resource_name = "assigned_keywords"
        fields = ['id', 'object_pk', '_order',]
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        throttle = CacheDBThrottle()
        filtering = {
            'object_pk': ('exact',),
            }
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        limit = 0

    def alter_list_data_to_serialize(self, request, data):
        data['assignedKeywords'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['assignedKeywords']
        del data['assignedKeywords']
        return data



class IngredientResource(ModelResource):
    recipe = fields.ToOneField('mezzanine_recipes.api.RecipeResource', 'recipe')

    class Meta:
        queryset = Ingredient.objects.all()
        resource_name = "ingredient"
        fields = ['id', 'quantity', 'unit', 'ingredient', 'note',]
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        limit = 0
        throttle = CacheDBThrottle()
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()

    def get_object_list(self, request, *args, **kwargs):
        return Ingredient.objects.filter(Q(recipe__publish_date__lte=now()) | Q(recipe__publish_date__isnull=True),
                                         Q(recipe__expiry_date__gte=now()) | Q(recipe__expiry_date__isnull=True),
                                         Q(recipe__status=CONTENT_STATUS_PUBLISHED))

    def dehydrate_unit(self, bundle):
        if bundle.data['unit']:
            return dict(UNITS)[bundle.data['unit']]
        else:
            return ""

    def alter_list_data_to_serialize(self, request, data):
        data['ingredients'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['ingredients']
        del data['ingredients']
        return data



class WorkingHoursResource(ModelResource):
    recipe = fields.ToOneField('mezzanine_recipes.api.RecipeResource', 'recipe')

    class Meta:
        queryset = WorkingHours.objects.all()
        resource_name = "working_hours"
        fields = ['id', 'hours', 'minutes',]
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        throttle = CacheDBThrottle()
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()

    def get_object_list(self, request, *args, **kwargs):
        return WorkingHours.objects.filter(Q(recipe__publish_date__lte=now()) | Q(recipe__publish_date__isnull=True),
                                           Q(recipe__expiry_date__gte=now()) | Q(recipe__expiry_date__isnull=True),
                                           Q(recipe__status=CONTENT_STATUS_PUBLISHED))

    def alter_list_data_to_serialize(self, request, data):
        data['workingHours'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['workingHours']
        del data['workingHours']
        return data



class CookingTimeResource(ModelResource):
    recipe = fields.ToOneField('mezzanine_recipes.api.RecipeResource', 'recipe')

    class Meta:
        queryset = CookingTime.objects.all()
        resource_name = "cooking_time"
        fields = ['id', 'hours', 'minutes',]
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        throttle = CacheDBThrottle()
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()

    def get_object_list(self, request, *args, **kwargs):
        return CookingTime.objects.filter(Q(recipe__publish_date__lte=now()) | Q(recipe__publish_date__isnull=True),
                                          Q(recipe__expiry_date__gte=now()) | Q(recipe__expiry_date__isnull=True),
                                          Q(recipe__status=CONTENT_STATUS_PUBLISHED))

    def alter_list_data_to_serialize(self, request, data):
        data['cookingTimes'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['cookingTimes']
        del data['cookingTimes']
        return data



class RestPeriodResource(ModelResource):
    recipe = fields.ToOneField('mezzanine_recipes.api.RecipeResource', 'recipe')

    class Meta:
        queryset = RestPeriod.objects.all()
        resource_name = "rest_period"
        fields = ['id', 'days', 'hours', 'minutes',]
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        throttle = CacheDBThrottle()
        serializer = CamelCaseJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()

    def get_object_list(self, request, *args, **kwargs):
        return RestPeriod.objects.filter(Q(recipe__publish_date__lte=now()) | Q(recipe__publish_date__isnull=True),
                                         Q(recipe__expiry_date__gte=now()) | Q(recipe__expiry_date__isnull=True),
                                         Q(recipe__status=CONTENT_STATUS_PUBLISHED))

    def alter_list_data_to_serialize(self, request, data):
        data['restPeriods'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['restPeriods']
        del data['restPeriods']
        return data
