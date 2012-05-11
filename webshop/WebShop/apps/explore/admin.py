from django.contrib import admin
from WebShop.apps.explore.models import Shop, Line, ArticleType, ArticleFamily, Promotion, Article, \
    ArticleOption, Pricing, LanguagePack

class ShopAdmin(admin.ModelAdmin):
    list_display = ('ref', 'logopath')
admin.site.register(Shop, ShopAdmin)


class LineAdmin(admin.ModelAdmin):
    list_display = ('id', 'ref', 'shop', 'sort', 'logopath', 'template_path')
admin.site.register(Line, LineAdmin)

class ArticleTypeAdmin(admin.ModelAdmin):
    list_display = ('en', 'de')
    search_fields = ('en',)
admin.site.register(ArticleType, ArticleTypeAdmin)

class ArticleFamilyAdmin(admin.ModelAdmin):
    list_display = ('ref', 'logopath', 'desc', 'line')
    search_fields = ('ref',)
admin.site.register(ArticleFamily, ArticleFamilyAdmin)

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('family', 'shop')
    search_fields = ('family__ref',)    
admin.site.register(Promotion, PromotionAdmin)

class PricingAdmin(admin.ModelAdmin):
    list_display = ('article', 'forRole', '_price', 'discountQty')
    search_fields = ('article__ref',)
admin.site.register(Pricing, PricingAdmin)

class PricingInline(admin.TabularInline):
    model = Pricing
    extra = 1

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('ref', 'article_family')
    search_fields = ('ref',)
    inlines = [
        PricingInline,
    ]
admin.site.register(Article, ArticleAdmin)

class ArticleOptionAdmin(admin.ModelAdmin):
    list_display = ('article', 'ref', 'sub_image_code')
    search_fields = ('article__ref',)
admin.site.register(ArticleOption, ArticleOptionAdmin)

class LanguagePackAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'en', 'de', 'fr', 'it', 'es', 'pl')
    search_fields = ('en','message_id')
admin.site.register(LanguagePack, LanguagePackAdmin)