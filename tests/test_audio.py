from gfunpack import audio


def test_sound_effects():
    audio.SoundEffects('output', 'audio')


def test_bgm():
    audio.BGM('output', 'audio')

if __name__ == '__main__':
    test_sound_effects()
    test_bgm()
