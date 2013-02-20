# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BlogProxy'
        db.create_table('mezzanine_recipes_blogproxy', (
            ('blogpost_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['blog.BlogPost'], unique=True, primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('mezzanine_recipes', ['BlogProxy'])

        # Adding model 'BlogPost'
        db.create_table('mezzanine_recipes_blogpost', (
            ('blogproxy_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mezzanine_recipes.BlogProxy'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('mezzanine_recipes', ['BlogPost'])

        # Adding model 'Recipe'
        db.create_table('mezzanine_recipes_recipe', (
            ('blogproxy_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mezzanine_recipes.BlogProxy'], unique=True, primary_key=True)),
            ('summary', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('portions', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('difficulty', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('mezzanine_recipes', ['Recipe'])

        # Adding model 'Ingredient'
        db.create_table('mezzanine_recipes_ingredient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('recipe', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ingredients', to=orm['mezzanine_recipes.Recipe'])),
            ('quantity', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('unit', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ingredient', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('mezzanine_recipes', ['Ingredient'])

        # Adding model 'WorkingHours'
        db.create_table('mezzanine_recipes_workinghours', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hours', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('minutes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('recipe', self.gf('django.db.models.fields.related.OneToOneField')(related_name='working_hours', unique=True, to=orm['mezzanine_recipes.Recipe'])),
        ))
        db.send_create_signal('mezzanine_recipes', ['WorkingHours'])

        # Adding model 'CookingTime'
        db.create_table('mezzanine_recipes_cookingtime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hours', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('minutes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('recipe', self.gf('django.db.models.fields.related.OneToOneField')(related_name='cooking_time', unique=True, to=orm['mezzanine_recipes.Recipe'])),
        ))
        db.send_create_signal('mezzanine_recipes', ['CookingTime'])

        # Adding model 'RestPeriod'
        db.create_table('mezzanine_recipes_restperiod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hours', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('minutes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('recipe', self.gf('django.db.models.fields.related.OneToOneField')(related_name='rest_period', unique=True, to=orm['mezzanine_recipes.Recipe'])),
            ('days', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mezzanine_recipes', ['RestPeriod'])


    def backwards(self, orm):
        # Deleting model 'BlogProxy'
        db.delete_table('mezzanine_recipes_blogproxy')

        # Deleting model 'BlogPost'
        db.delete_table('mezzanine_recipes_blogpost')

        # Deleting model 'Recipe'
        db.delete_table('mezzanine_recipes_recipe')

        # Deleting model 'Ingredient'
        db.delete_table('mezzanine_recipes_ingredient')

        # Deleting model 'WorkingHours'
        db.delete_table('mezzanine_recipes_workinghours')

        # Deleting model 'CookingTime'
        db.delete_table('mezzanine_recipes_cookingtime')

        # Deleting model 'RestPeriod'
        db.delete_table('mezzanine_recipes_restperiod')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'blog.blogcategory': {
            'Meta': {'ordering': "('title',)", 'object_name': 'BlogCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'blog.blogpost': {
            'Meta': {'ordering': "('-publish_date',)", 'object_name': 'BlogPost'},
            '_meta_title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'blogposts'", 'blank': 'True', 'to': "orm['blog.BlogCategory']"}),
            'comments': ('mezzanine.generic.fields.CommentsField', [], {'object_id_field': "'object_pk'", 'to': "orm['generic.ThreadedComment']", 'frozen_by_south': 'True'}),
            'comments_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'featured_image': ('mezzanine.core.fields.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gen_description': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_sitemap': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keywords': ('mezzanine.generic.fields.KeywordsField', [], {'object_id_field': "'object_pk'", 'to': "orm['generic.AssignedKeyword']", 'frozen_by_south': 'True'}),
            'keywords_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rating': ('mezzanine.generic.fields.RatingField', [], {'object_id_field': "'object_pk'", 'to': "orm['generic.Rating']", 'frozen_by_south': 'True'}),
            'rating_average': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rating_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'related_posts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_posts_rel_+'", 'blank': 'True', 'to': "orm['blog.BlogPost']"}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'blogposts'", 'to': "orm['auth.User']"})
        },
        'comments.comment': {
            'Meta': {'ordering': "('submit_date',)", 'object_name': 'Comment', 'db_table': "'django_comments'"},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_comment'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comment_comments'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'user_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'generic.assignedkeyword': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'AssignedKeyword'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': "orm['generic.Keyword']"}),
            'object_pk': ('django.db.models.fields.IntegerField', [], {})
        },
        'generic.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'generic.rating': {
            'Meta': {'object_name': 'Rating'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'generic.threadedcomment': {
            'Meta': {'ordering': "('submit_date',)", 'object_name': 'ThreadedComment', '_ormbases': ['comments.Comment']},
            'by_author': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['comments.Comment']", 'unique': 'True', 'primary_key': 'True'}),
            'replied_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'null': 'True', 'to': "orm['generic.ThreadedComment']"})
        },
        'mezzanine_recipes.blogpost': {
            'Meta': {'ordering': "('-publish_date',)", 'object_name': 'BlogPost', '_ormbases': ['mezzanine_recipes.BlogProxy']},
            'blogproxy_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['mezzanine_recipes.BlogProxy']", 'unique': 'True', 'primary_key': 'True'})
        },
        'mezzanine_recipes.blogproxy': {
            'Meta': {'ordering': "('-publish_date',)", 'object_name': 'BlogProxy', '_ormbases': ['blog.BlogPost']},
            'blogpost_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['blog.BlogPost']", 'unique': 'True', 'primary_key': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'mezzanine_recipes.cookingtime': {
            'Meta': {'object_name': 'CookingTime'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minutes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recipe': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'cooking_time'", 'unique': 'True', 'to': "orm['mezzanine_recipes.Recipe']"})
        },
        'mezzanine_recipes.ingredient': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Ingredient'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredient': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ingredients'", 'to': "orm['mezzanine_recipes.Recipe']"}),
            'unit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'mezzanine_recipes.recipe': {
            'Meta': {'ordering': "('-publish_date',)", 'object_name': 'Recipe', '_ormbases': ['mezzanine_recipes.BlogProxy']},
            'blogproxy_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['mezzanine_recipes.BlogProxy']", 'unique': 'True', 'primary_key': 'True'}),
            'difficulty': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'portions': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'mezzanine_recipes.restperiod': {
            'Meta': {'object_name': 'RestPeriod'},
            'days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minutes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recipe': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'rest_period'", 'unique': 'True', 'to': "orm['mezzanine_recipes.Recipe']"})
        },
        'mezzanine_recipes.workinghours': {
            'Meta': {'object_name': 'WorkingHours'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minutes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recipe': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'working_hours'", 'unique': 'True', 'to': "orm['mezzanine_recipes.Recipe']"})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['mezzanine_recipes']