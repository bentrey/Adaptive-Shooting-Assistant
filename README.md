# Adaptive Basketball Coach

Utilizing motion sensing wearable technology, our application will train a 
model on a basketball players specific motion characteristics and provide 
feedback on a shot by shot basis.

## Installation requirements

The are several technologies being employed:
* Bluetooth for capturing motion data
* Speech recognition for accepting voice commands
* Text to speech for providing feedback
* pipenv for python virtual environment 
 
### Windows
* Use the included pipfile:
    * pipenv shell
    * pipenv install
     
* For bluetooth connectivity bleak is used to wrap around blueZ

  * On Windows install the bleak package
  
    `pipenv install bleak`

* pyaudio is required for the SpeechRecognition package. 
It was easiest to install from the wheel PyAudio-0.2.11-cp38-cp38-win_amd64.whl, included in the project or 
found [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)



### Linux
* For bluetooth connectivity bluez is used
    * Manually install using: 
    
      pipenv install bluez


## Running the app
Run the app from the bball_coach_app folder:
    
    python main_ui.py

## Demo files
Try speech recognition running:

    python speech/guess_game.py

Try the text to speech by running:
   
    python speech/test_speak.py "hello world" "nice to meet you"
    
    
