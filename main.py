import os, re, shutil, subprocess, json
from pytubefix import YouTube

def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "_", text.strip())
    return re.sub(r"_+", "_", text)

def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg não encontrado no PATH. Instale e tente novamente (ffmpeg -version).")

def achar_itag_audio_ptbr(yt: YouTube):
    """
    Varre o playerResponse e tenta achar uma faixa de áudio com idioma PT-BR.
    Retorna o itag escolhido (maior bitrate) ou None se não existir.
    """
    # Em pytubefix, yt.vid_info já contém o playerResponse
    info = yt.vid_info
    # Alguns formatos: às vezes vem como dict, às vezes json string
    if isinstance(info, str):
        info = json.loads(info)

    # playerResponse pode estar em chaves diferentes conforme a versão
    pr = info.get("playerResponse") or info.get("player_response") or info
    sd = (pr or {}).get("streamingData", {})
    adaptive = sd.get("adaptiveFormats", [])

    candidatos = []
    for f in adaptive:
        # Só formatos de áudio
        if "audio" in (f.get("mimeType") or ""):
            at = f.get("audioTrack", {}) or {}
            # Tentamos identificar PT/Portuguese
            label = " ".join([
                str(at.get("displayName","")),
                str(at.get("id","")),
                str(at.get("audioIsDefault",""))
            ]).lower()
            lang = (at.get("displayName") or "").lower()
            if ("portugu" in label) or ("pt" in at.get("id","").lower()) or ("pt-br" in label) or ("brasil" in label):
                br = f.get("averageBitrate") or f.get("bitrate") or 0
                itag = f.get("itag")
                if itag is not None:
                    candidatos.append((itag, int(br)))
    if not candidatos:
        return None
    # escolhe maior bitrate
    candidatos.sort(key=lambda x: x[1], reverse=True)
    return candidatos[0][0]

def baixar_ptbr_max(url: str, pasta_destino: str = "downloads"):
    check_ffmpeg()
    os.makedirs(pasta_destino, exist_ok=True)

    yt = YouTube(url)
    titulo = slugify(yt.title)
    print(f"Título: {yt.title}")
    print(f"Canal:  {yt.author}")

    # Melhor vídeo (adaptive)
    video_best = yt.streams.filter(adaptive=True, type="video").order_by("resolution").desc().first()

    # Fallback progressivo se não houver adaptive
    if not video_best:
        prog = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
        if not prog:
            raise RuntimeError("Não encontrei stream de vídeo.")
        print(f"Nada de adaptive. Baixando progressivo {prog.resolution}…")
        saida = os.path.join(pasta_destino, f"{titulo}.mp4")
        prog.download(output_path=pasta_destino, filename=os.path.basename(saida))
        print(f"✅ Concluído: {saida}")
        return

    # Tenta achar itag do áudio PT-BR
    itag_pt = achar_itag_audio_ptbr(yt)

    if itag_pt is None:
        print("⚠️ Não encontrei faixa de áudio PT-BR neste vídeo.")
        resp = input("Deseja continuar com o áudio padrão (geralmente inglês)? [s/N]: ").strip().lower()
        if resp != "s":
            print("Cancelado.")
            return
        # Sem PT-BR: pega melhor áudio disponível
        audio_best = yt.streams.filter(adaptive=True, type="audio").order_by("abr").desc().first()
    else:
        audio_best = yt.streams.get_by_itag(itag_pt)
        if not audio_best:
            # Raro, mas se não mapear, cai para melhor áudio
            audio_best = yt.streams.filter(adaptive=True, type="audio").order_by("abr").desc().first()

    if not audio_best:
        raise RuntimeError("Não encontrei faixa de áudio para baixar.")

    v_ext = os.path.splitext(video_best.default_filename)[1] or ".mp4"
    a_ext = os.path.splitext(audio_best.default_filename)[1] or ".m4a"
    video_tmp = os.path.join(pasta_destino, f"{titulo}.video{v_ext}")
    audio_tmp = os.path.join(pasta_destino, f"{titulo}.audio{a_ext}")

    print(f"Baixando VÍDEO em {video_best.resolution}…")
    video_best.download(output_path=pasta_destino, filename=os.path.basename(video_tmp))

    idioma_msg = "PT-BR" if itag_pt is not None else "padrão"
    print(f"Baixando ÁUDIO ({idioma_msg})…")
    audio_best.download(output_path=pasta_destino, filename=os.path.basename(audio_tmp))

    # Mescla com ffmpeg (tenta copy → MKV; se falhar, re-encode MP4)
    saida = os.path.join(pasta_destino, f"{titulo}.mkv")
    print("Mesclando com ffmpeg (sem re-encode)…")
    cmd_copy = ["ffmpeg","-y","-i",video_tmp,"-i",audio_tmp,"-c","copy","-movflags","+faststart",saida]
    try:
        subprocess.run(cmd_copy, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Cópia direta falhou. Re-encode para MP4…")
        saida = os.path.join(pasta_destino, f"{titulo}.mp4")
        cmd_enc = ["ffmpeg","-y","-i",video_tmp,"-i",audio_tmp,
                   "-c:v","libx264","-crf","18","-preset","medium",
                   "-c:a","aac","-b:a","192k","-movflags","+faststart",saida]
        subprocess.run(cmd_enc, check=True)

    # Limpeza
    for p in (video_tmp, audio_tmp):
        try: os.remove(p)
        except OSError: pass

    print(f"✅ Concluído: {saida}")

if __name__ == "__main__":
    url = input("Cole a URL do vídeo do YouTube: ").strip()
    baixar_ptbr_max(url)
