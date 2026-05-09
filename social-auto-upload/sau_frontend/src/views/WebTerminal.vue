<template>
  <div class="web-terminal-container">
    <div class="terminal-header">
      <div class="terminal-title">
        <span class="icon">💻</span>
        <span class="text">TERMINAL_CONSOLE</span>
      </div>
      <div class="terminal-controls">
        <span class="control minimize">_</span>
        <span class="control maximize">□</span>
        <span class="control close">×</span>
      </div>
    </div>
    <div class="terminal-body" ref="terminalRef"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'

const terminalRef = ref(null)
let terminal = null
let fitAddon = null
let currentLine = ''

onMounted(() => {
  initTerminal()
})

onBeforeUnmount(() => {
  if (terminal) {
    terminal.dispose()
  }
})

const initTerminal = () => {
  terminal = new Terminal({
    cursorBlink: true,
    cursorStyle: 'block',
    theme: {
      background: 'transparent',
      foreground: '#FFBF00',
      cursor: '#FFBF00',
      selection: 'rgba(255, 191, 0, 0.3)',
      black: '#3D2817',
      red: '#FF6B6B',
      green: '#90EE90',
      yellow: '#FFD700',
      blue: '#87CEEB',
      magenta: '#FFB380',
      cyan: '#00FFFF',
      white: '#FFF8DC',
      brightBlack: '#8B6F47',
      brightRed: '#FF8C42',
      brightGreen: '#39FF14',
      brightYellow: '#FFFF00',
      brightBlue: '#00D9FF',
      brightMagenta: '#FF00FF',
      brightCyan: '#00FFFF',
      brightWhite: '#FFFFFF'
    },
    fontFamily: '"JetBrains Mono", Consolas, monospace',
    fontSize: 14,
    lineHeight: 1.2,
    allowTransparency: true
  })

  fitAddon = new FitAddon()
  terminal.loadAddon(fitAddon)
  terminal.open(terminalRef.value)
  fitAddon.fit()

  terminal.writeln('\x1b[1;33mWelcome to Social Auto Upload Matrix [Nanxu Island Edition]\x1b[0m')
  terminal.writeln('Type "help" for a list of commands.')
  
  prompt()

  terminal.onData(async e => {
    const char = e
    if (char === '\r') { // Enter
      terminal.write('\r\n')
      const command = currentLine.trim()
      currentLine = ''
      
      if (command) {
        if (command === 'clear') {
            terminal.clear()
            prompt()
            return
        }
        await executeCommand(command)
      } else {
        prompt()
      }
    } else if (char === '\u007F') { // Backspace
      if (currentLine.length > 0) {
        terminal.write('\b \b')
        currentLine = currentLine.slice(0, -1)
      }
    } else {
      terminal.write(char)
      currentLine += char
    }
  })

  window.addEventListener('resize', () => {
    fitAddon.fit()
  })
}

const prompt = () => {
  terminal.write('\x1b[1;32mroot@sau-matrix:~$ \x1b[0m')
}

const executeCommand = async (cmd) => {
  try {
    const response = await fetch('http://localhost:5409/api/terminal/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command: cmd })
    })

    if (!response.ok) {
        throw new Error(`Server returned ${response.status} ${response.statusText}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n\n')
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6)
                terminal.writeln(data)
            }
        }
    }
  } catch (err) {
    terminal.writeln(`\x1b[31mError: ${err.message}\x1b[0m`)
  } finally {
    prompt()
  }
}
</script>

<style lang="scss" scoped>
.web-terminal-container {
  background: rgba(30, 20, 10, 0.6); // 深棕色透明背景
  backdrop-filter: blur(15px);
  border: 2px solid rgba(139, 111, 71, 0.6); // 木质边框
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  margin-top: 20px;
  height: 300px;
  display: flex;
  flex-direction: column;

  .terminal-header {
    background: rgba(74, 47, 31, 0.8);
    padding: 8px 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(139, 111, 71, 0.4);

    .terminal-title {
      color: #FFBF00; // 琥珀金
      font-family: 'Cinzel', serif;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }

    .terminal-controls {
      display: flex;
      gap: 10px;
      
      .control {
        color: #8B6F47;
        cursor: pointer;
        font-weight: bold;
        transition: color 0.3s;
        
        &:hover {
          color: #FFBF00;
        }
      }
    }
  }

  .terminal-body {
    flex: 1;
    padding: 10px;
    
    // 自定义滚动条
    &::-webkit-scrollbar {
      width: 8px;
    }
    
    &::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.1);
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba(139, 111, 71, 0.5);
      border-radius: 4px;
      
      &:hover {
        background: rgba(255, 191, 0, 0.5);
      }
    }
  }
}
</style>
