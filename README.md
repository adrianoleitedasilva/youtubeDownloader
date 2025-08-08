# Youtube Downloader

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white) ![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)

Este é um script em Python que permite baixar vídeos do YouTube na maior resolução disponível e escolher a faixa de áudio desejada — por exemplo, Português (Brasil), quando disponível.
O projeto utiliza pytubefix para acessar os streams e ffmpeg para mesclar vídeo e áudio de forma rápida, sem perda de qualidade.

✨ Recursos
📹 Resolução máxima disponível (inclui 4K, 8K, se presentes).

🎙 Escolha do idioma do áudio (lista todas as faixas de áudio adaptativas).

⚡ Mesclagem de vídeo e áudio sem re-encode sempre que possível.

🔄 Fallback automático para MP4 re-encodado quando necessário.

🛠 Suporte a linha de comando com filtros por idioma ou índice da faixa.

🚀 Como funciona
Busca o vídeo na resolução máxima.

Lista todas as faixas de áudio disponíveis.

Permite escolha manual por índice ou filtro por idioma.

Baixa vídeo e áudio separadamente.

Mescla com ffmpeg no formato final.

📌 Description (EN)
This is a Python script that allows you to download YouTube videos in the highest available resolution and select the audio track you want — for example, Portuguese (Brazil), when available.
It uses pytubefix to access streams and ffmpeg to merge video and audio quickly without quality loss.

✨ Features
📹 Maximum resolution available (includes 4K, 8K if present).

🎙 Choose audio language (lists all available adaptive audio tracks).

⚡ Merge video and audio without re-encoding whenever possible.

🔄 Automatic fallback to re-encoded MP4 when needed.

🛠 Command-line support with filters by language or track index.

🚀 How it works
Fetches the video in the maximum resolution.

Lists all available audio tracks.

Allows manual selection by index or language filter.

Downloads video and audio separately.

Merges them with ffmpeg into the final file.

pip install pytubefix

# Windows:

winget install Gyan.FFmpeg # ou: choco install ffmpeg
ffmpeg -version
