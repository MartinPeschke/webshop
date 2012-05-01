from django.conf import settings
import os

for af in ArticleFamily.objects.all():
	for subdir in ['high', 'medium', 'low']:
		f = os.path.join(settings.MEDIA_ROOT, 'files', af.get_shop_ref(), 'families', subdir, af.logopath + '.jpg')
		if not os.path.exists(f):
			print af.get_shop_ref(), subdir, af.ref



for shop in [s.ref for s in Shop.objects.all()]:
	for (dirpath, dirnames, filenames) in os.walk(os.path.join(settings.MEDIA_ROOT, 'files', shop, 'families')):
		res = dirpath.split(os.sep)[-1]
		names = map(lambda x: (x.rsplit('.', 1)[0], x), filenames)
		for name, fname in names:
			if not ArticleFamily.objects.filter(line__shop__ref = shop).filter(logopath = name).all():
				print 'removing', os.path.join(dirpath, fname)
				os.remove(os.path.join(dirpath, fname))
				