import toml; c=toml.load('config.toml'); c['app']['tts_server'] = 'edge-tts'; f=open('config.toml','w',encoding='utf-8'); toml.dump(c,f); f.close(); print('TTS switched to edge-tts!')
