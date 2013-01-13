import sys
import xbmcaddon, random
import xbmcgui, xbmc, os

#Most of the screensaver code was taken from the screensaver.xbmc.slideshow addon, so thanks for that go to the authors at Team XBMC
if 'xbmcplugin' in sys.modules:
	oldxbmcplugin = sys.modules['xbmcplugin']
	del(sys.modules["xbmcplugin"])
import xbmcplugin
xbmcplugin.reset()
xbmcplugin.normxbmcplugin = oldxbmcplugin
	
__addon__	= xbmcaddon.Addon()
__addonid__  = __addon__.getAddonInfo('id')
__cwd__	  = __addon__.getAddonInfo('path').decode("utf-8")

def log(txt):
	if isinstance (txt,str):
		txt = txt.decode("utf-8")
	message = u'%s: %s' % (__addonid__, txt)
	xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

class Screensaver(xbmcgui.WindowXMLDialog):
	def __init__( self, *args, **kwargs ):
		pass

	def onInit(self):
		self.conts()
		items = self.items()
		if items:
			self.show(items)

	def conts(self):
		self.winid = xbmcgui.getCurrentWindowDialogId()
		self.stop = False
		self.Monitor = MyMonitor(action = self.exit)
		self.image1 = self.getControl(1)
		self.image2 = self.getControl(2)
		self.slideshow_type = __addon__.getSetting('type')
		self.slideshow_path = __addon__.getSetting('path')
		self.slideshow_effect = __addon__.getSetting('effect')
		self.slideshow_random = __addon__.getSetting('randomize') == 'true'
		self.slideshow_time = (int('%02d' % int(__addon__.getSetting('time'))) + 1) * 1000
		self.slideshow_dim = hex(int('%.0f' % (float(__addon__.getSetting('level')) * 2.55)))[2:] + 'ffffff' # convert float to hex value usable by the skin

	def items(self):
		#addonName = 'plugin.image.flickr'
		addonName = self.slideshow_path.split('://')[-1].split('/')[0]
		xbmcplugin.addonID = addonName
		localAddonsPath = os.path.join(xbmc.translatePath('special://home'),'addons')
		addonPath = os.path.join(localAddonsPath,addonName)
		defaultpyPath = os.path.join(addonPath,'default.py')
		if len(sys.argv) < 2:
			sys.argv.append(1)
		if len(sys.argv) < 3:
			sys.argv.append('test')
		#sys.argv[2] = '?mode=1&url=slideshow&name=photostream'
		sys.argv[2] = '?' + self.slideshow_path.split('?')[-1]
		print sys.argv[2]
		sys.path.insert(0,addonPath)
		execfile(defaultpyPath,globals())
		items = xbmcplugin.FINAL_ITEMS
		if self.slideshow_random: random.shuffle(items)
		return items

	def show(self, items):
		# set window properties for the skin
		xbmcgui.Window(self.winid).setProperty('SlideView.Dim', self.slideshow_dim)
		cur_img = self.image1
		while (not xbmc.abortRequested) and (not self.stop):
			for img in items:
				cur_img.setImage(img)
				if cur_img == self.image1:
					if self.slideshow_effect == "0":
						xbmcgui.Window(self.winid).setProperty('SlideView.Slide1', '0')
						xbmcgui.Window(self.winid).setProperty('SlideView.Slide2', '1')
					else:
						xbmcgui.Window(self.winid).setProperty('SlideView.Fade1', '0')
						xbmcgui.Window(self.winid).setProperty('SlideView.Fade2', '1')
						if self.slideshow_effect == "2":
							self.anim(self.winid, 1, 2, self.image1, self.image2, self.slideshow_time)
					cur_img = self.image2
				else:
					if self.slideshow_effect == "0":
						xbmcgui.Window(self.winid).setProperty('SlideView.Slide2', '0')
						xbmcgui.Window(self.winid).setProperty('SlideView.Slide1', '1')
					else:
						xbmcgui.Window(self.winid).setProperty('SlideView.Fade2', '0')
						xbmcgui.Window(self.winid).setProperty('SlideView.Fade1', '1')
						if self.slideshow_effect == "2":
							self.anim(self.winid, 2, 1, self.image2, self.image1, self.slideshow_time)
					cur_img = self.image1
				count = int(self.slideshow_time / 1000)
				if self.slideshow_effect == "2":
					count -= 1
				while (not xbmc.abortRequested) and (not self.stop) and count > 0:
					count -= 1
					xbmc.sleep(1000)
				if  self.stop or xbmc.abortRequested:
					break

	def anim(self, winid, next_prop, prev_prop, next_img, prev_img, showtime):
		number = random.randint(1,9)
		posx = 0
		posy = 0
		# calculate posx and posy offset depending on the selected time per image (add 0.5 sec fadeout time)
		if number == 2 or number == 6 or number == 8:
			posx = int(-128 + (12.8 * ((showtime + 0.5) / 1000)))
		elif number == 3 or number == 7 or number == 9:
			posx = int(128 - (12.8 * ((showtime + 0.5) / 1000)))
		if number == 4 or number == 6 or number == 7:
			posy = int(-72 + (7.2 * ((showtime + 0.5) / 1000)))
		elif number == 5 or number == 8 or number == 9:
			posy = int(72 - (7.2 * ((showtime + 0.5) / 1000)))
		next_img.setPosition(posx, posy)
		xbmcgui.Window(winid).setProperty('SlideView.Pan%i' % next_prop, str(number))
		xbmc.sleep(500)
		prev_img.setPosition(0, 0)
		xbmcgui.Window(winid).setProperty('SlideView.Pan%i' % prev_prop, '0')
		xbmc.sleep(500)

	def exit(self):
		self.stop = True
		self.close()

class MyMonitor(xbmc.Monitor): #@UndefinedVariable
	def __init__( self, *args, **kwargs ):
		self.action = kwargs['action']

	def onScreensaverDeactivated(self):
		self.action()
		
if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'resetpath':
		__addon__.setSetting('path','')
	else:
		screensaver_gui = Screensaver('script-python-slideshow.xml', __cwd__, 'default')
		screensaver_gui.doModal()
		del screensaver_gui
		sys.modules.clear()

