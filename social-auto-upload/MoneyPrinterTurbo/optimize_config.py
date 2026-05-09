import toml; c=toml.load('config.toml'); c['app']['whisper_model'] = 'base'; f=open('config.toml','w',encoding='utf-8'); toml.dump(c,f); f.close(); print('Model set to base!')
