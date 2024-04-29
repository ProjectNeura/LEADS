from atexit import register as _register

from sdl2 import AUDIO_S16 as _AUDIO_S16
from sdl2.sdlmixer import Mix_Init as _init, Mix_OpenAudioDevice as _open_audio_device, MIX_INIT_MP3 as _MIX_INIT_MP3, \
    Mix_LoadMUS as _load_music, Mix_PlayMusic as _play_music, Mix_Music as _Music, \
    Mix_GetError as _get_error, Mix_FreeMusic as _free_music, Mix_CloseAudio as _close_audio

from leads_audio.system import _ASSETS_PATH


def _ensure(flag: int) -> None:
    if flag < 0:
        raise RuntimeError(_get_error().decode())


_init(_MIX_INIT_MP3)
_ensure(_open_audio_device(44100, _AUDIO_S16, 2, 2048, None, 1))


@_register
def _release_resources() -> None:
    _close_audio()


class _SoundEffect(object):
    def __init__(self, name: str) -> None:
        self._name: str = name
        self._source: _Music | None = None

    def load_source(self) -> _Music:
        if self._source is None:
            self._source = _load_music(f"{_ASSETS_PATH}/{self._name}.mp3".encode())
        return self._source

    def play(self) -> None:
        _ensure(_play_music(self.load_source(), 0))

    def stop(self) -> None:
        _ensure(_free_music(self.load_source()))


CONFIRM: _SoundEffect = _SoundEffect("confirm")
DIRECTION_INDICATOR_ON: _SoundEffect = _SoundEffect("direction-indicator-on")
DIRECTION_INDICATOR_OFF: _SoundEffect = _SoundEffect("direction-indicator-off")
WARNING: _SoundEffect = _SoundEffect("warning")
