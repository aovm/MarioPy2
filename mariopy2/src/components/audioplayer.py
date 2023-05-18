import pygame

class AudioPlayer:

    def __init__(self, resourceLib: dict) -> None:
        self.audioDict: dict = resourceLib['audio']
   
    def playMusic(self, musicID: str, loops: int):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

        if musicID in self.audioDict.keys():
            pygame.mixer.music.load(self.audioDict[musicID])
            pygame.mixer.music.play(loops)

    def unloadCurrentMusic(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def pauseMusic(self):
        pygame.mixer.music.pause()

    def unpauseMusic(self):
        pygame.mixer.music.unpause()

    def playAudio(self, audioID: str):
        if audioID in self.audioDict.keys():
            self.audioDict[audioID].play()

    def finalize(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.stop()