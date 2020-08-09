import pyttsx3
import sys
import pygame
from gtts import gTTS
import io

def main():
     engine = pyttsx3.init()
     for arg in sys.argv[1:]:
         engine.say(arg)
     engine.runAndWait()

     for arg in sys.argv[1:]:
         with io.BytesIO() as f:
             gTTS(text=arg, lang='en').write_to_fp(f)
             f.seek(0)
             pygame.mixer.init()
             pygame.mixer.music.load(f)
             pygame.mixer.music.play()
             while pygame.mixer.music.get_busy():
                 continue

if __name__ == "__main__":
    main()

