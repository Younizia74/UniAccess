from kivy.app import App
from kivy.uix.button import Button

try:
    from jnius import autoclass
    HAVE_PYJNIUS = True
except ImportError:
    HAVE_PYJNIUS = False

class NVDAAndroidApp(App):
    def build(self):
        btn = Button(text='Dire Bonjour', font_size=40)
        btn.bind(on_press=self.say_hello)
        return btn

    def say_hello(self, instance):
        if HAVE_PYJNIUS:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
            Locale = autoclass('java.util.Locale')
            tts = TextToSpeech(activity, None)
            tts.speak('Bonjour depuis NVDA Android', TextToSpeech.QUEUE_FLUSH, None, None)
        else:
            print('[TTS] (Simulation) Bonjour depuis NVDA-Android !')

if __name__ == '__main__':
    NVDAAndroidApp().run() 