"""
LIMBA 2.0 — Hugging Face Spaces application

Gradio interface for a fine-tuned Llama 3.1 model supporting Italian and
Limba Sarda Comuna (LSC), with lightweight Wikipedia retrieval.

Model weights are downloaded from:
    FPll/limba-mentor-llama3-gguf

Environment variables:
    HF_TOKEN: Hugging Face access token used by InferenceClient and
              hf_hub_download when authentication is required.
"""

import os
import sys

# Workaround for the musl runtime used by the Hugging Face Space
musl_path = "/home/user/app/libc.musl-x86_64.so.1"
if not os.path.exists(musl_path):
    print("Configurazione libreria musl in corso...")
    os.system(f"ln -s /usr/lib/x86_64-linux-musl/libc.so {musl_path}")
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = "/home/user/app:" + env.get("LD_LIBRARY_PATH", "")
    os.execve(sys.executable, [sys.executable] + sys.argv, env)


import gradio as gr
from huggingface_hub import hf_hub_download, InferenceClient
from llama_cpp import Llama
import wikipedia

# Default Wikipedia language; the retrieval function switches between Sardinian and Italian.
wikipedia.set_lang("it")
hf_client = InferenceClient(token=os.environ.get("HF_TOKEN"))

REPO_ID = "FPll/limba-mentor-llama3-gguf"
FILENAME = "Meta-Llama-3.1-8B.Q4_K_M.gguf"

# Scarica il file GGUF nella cache della Space
model_path = hf_hub_download(
    repo_id=REPO_ID, 
    filename=FILENAME, 
    token=os.environ.get("HF_TOKEN")
)

# Inizializza Llama (su CPU Free Tier)
llm = Llama(
    model_path=model_path,
    n_ctx=4096,      
    n_threads=2,
    verbose=True
)

def cerca_su_wikipedia(query):
    """Estrazione entità via API remota e ricerca (Sardo -> Italiano)"""
    try:
        print(f"\n--- RAG START --- Query utente: '{query}'")
        prompt_estrazione = f"Estrai solo l'argomento principale da cercare su Wikipedia da questa domanda. Rispondi SOLO con l'argomento, senza punteggiatura. Domanda: '{query}'"
        
        risposta = hf_client.chat_completion(
            messages=[{"role": "user", "content": prompt_estrazione}], 
            model="Qwen/Qwen2.5-7B-Instruct", 
            max_tokens=15
        )
        query_pulita = risposta.choices[0].message.content.strip()
        print(f"--- RAG ESTRAZIONE --- Modello remoto ha estratto: '{query_pulita}'")
        
        if not query_pulita:
            return ""

        wikipedia.set_lang("sc")
        risultati = wikipedia.search(query_pulita, results=1)
        print(f"--- RAG SEARCH SC --- Risultati in sardo: {risultati}")
        
        if not risultati:
            wikipedia.set_lang("it")
            risultati = wikipedia.search(query_pulita, results=1)
            print(f"--- RAG SEARCH IT --- Risultati in italiano: {risultati}")
            
        if risultati:
            titolo = risultati[0]
            try:
                # Scarica la pagina completa
                pagina = wikipedia.page(titolo)
                
                # Partiamo da ZERO (per salvare le biografie/definizioni) 
                # e arriviamo fino a 6000 caratteri (per catturare le liste più in basso)
                testo_utile = pagina.content[:6000]
                
                print(f"--- RAG SUCCESSO UNIVERSALE --- Testo estratto da: {titolo}")
                return testo_utile
                
            except wikipedia.exceptions.DisambiguationError as e:
                # Se è una pagina ambigua, prende la prima opzione
                pagina = wikipedia.page(e.options[0])
                return pagina.content[:6000]
            
        print("--- RAG FALLITO --- Nessun risultato trovato.")
        return ""
    except Exception as e:
        print(f"--- RAG ERRORE --- {str(e)}")
        return ""

def respond(message, history):
    # 1. IL SALVAVITA: Emette un segnale vuoto per impedire a Gradio di andare in crash (StopAsyncIteration)
    partial_message = ""
    yield partial_message 
    
    try:
        # Estrazione sicura del testo nel caso Gradio invii un dizionario
        msg_text = message.get("text", "") if isinstance(message, dict) else str(message)
        # Richiama Wikipedia
        wiki_context = cerca_su_wikipedia(msg_text)
        extra_ctx = f"\n\nCONTESTO WIKIPEDIA (usalo per rispondere e traduci in sardo): {wiki_context}" if wiki_context else ""
        
        system_instruction = (
            "Sei Limba 2.0, creato da Francesco Palladino. Sei un modello di linguaggio che parla sardo (LSC) e italiano.\n"
            "REGOLE DA RISPETTARE:\n"
            "1. Se l'utente chiede una traduzione in sardo o in italiano, esegui la traduzione senza aggiungere altro.\n"
            "2. Se l'utente chiede una formula o se nella risposta scrivi formule, usa il formato LaTeX racchiuso tra doppi simboli di dollaro ($$) su una riga separata, esempio: $$E=mc^2$$.\n"
            "3. Se l'utente ti saluta (es. 'Ciao', 'Buongiorno'), rispondi esclusivamente con: 'Salude! So Limba 2.0, comente ti potzo agiudare?' e fermati.\n"
            "4. Se l'utente fa una richiesta su un argomento specifico, rispondi alla richiesta in modo completo e accurato.\n"
        )

        few_shot = (
            "<|start_header_id|>user<|end_header_id|>\n\nDimmi tre colori in sardo.<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\nEcco sos colores:\n\n"
            "- Ruju\n"
            "- Birde\n"
            "- Blu<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\nConfronta oro e argento.<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\nEcco sa tabella:\n\n"
            "| Metallu | Simbolu | n. Atòmicu |\n"
            "| :--- | :--- | :--- |\n"
            "| Oro | Au | 79 |\n"
            "| Prata | Ag | 47 |<|eot_id|>"
        )

        # 2. GESTIONE UNIVERSALE HISTORY (Funziona con tutte le versioni di Gradio)
        history_text = ""
        for item in history:
            if isinstance(item, dict):
                # Formato nuovo di Gradio
                role = item.get("role", "user")
                content = item.get("content", "")
                history_text += f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>"
            else:
                # Formato classico a tuple
                user_msg, bot_msg = item
                history_text += f"<|start_header_id|>user<|end_header_id|>\n\n{user_msg}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{bot_msg}<|eot_id|>"

       # Assemblaggio del Prompt
        prompt = f"<|start_header_id|>system<|end_header_id|>\n\n{system_instruction}{extra_ctx}<|eot_id|>{few_shot}{history_text}<|start_header_id|>user<|end_header_id|>\n\n{msg_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

        # 3. GENERAZIONE CON PARAMETRI OTTIMIZZATI PER GLI ELENCHI
        response = llm(
            prompt,
            max_tokens=768,
            stop=["<|eot_id|>", "<|start_header_id|>", "<|end_header_id|>"],
            stream=True,
            temperature=0.1,
            top_p=0.9,
            repeat_penalty=1.15  
        )
        
        for chunk in response:
            if "choices" in chunk and len(chunk["choices"]) > 0:
                text = chunk["choices"][0].get("text", "")
                if text:
                    partial_message += text
                    yield partial_message
                    
    # Scudo Anti-Crash: se c'è un errore te lo stampa in chat invece di far crollare la pagina
    except Exception as e:
        yield f"🚨 Errore Python interno: {str(e)}"

# 4. INTERFACCIA VISIVA E STILE

# CSS "Mano Pesante" per eliminare ogni traccia di bordo e sfondo dall'avatar della chat
custom_css = """
/* Rimuove lo sfondo bianco, il bordo, l'ombra e il margine dal contenitore esterno */
.message-avatar, .avatar-container, .avatar-image {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    width: 60px !important;
    height: 60px !important;
}
/* Forza l'immagine a riempire tutto lo spazio senza limitazioni */
.message-avatar img, .avatar-container img, .avatar-image img {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}
"""

# Header HTML personalizzato con il link corretto (FPll)
header_html = """
<div style="display: flex; align-items: center; margin-bottom: 10px;">
    <img src="https://huggingface.co/spaces/FPll/Limba_2.0/resolve/main/logo.png" style="width: 55px; height: 55px; border-radius: 50%; margin-right: 15px;">
    <h1 style="margin: 0; font-size: 24px;">Limba 2.0 - S'assistente IA tuo chi faeddat sardu</h1>
</div>
"""

with gr.Blocks() as demo:
    # Inseriamo il titolo grafico in cima
    gr.HTML(header_html)
    
    # Rimuoviamo il parametro 'title' da qui perché ora usiamo l'intestazione sopra
    gr.ChatInterface(
        fn=respond,
        description="Ajò! So Limba 2.0, s'assistente tuo pro s'informatica, sa matematica e s'iscentzia. Faeddo sardu e italianu.",
        examples=["Iscrie unu script in Python pro lèghere unu file CSV.", "Ispiegami su teorema de Pitagora.", "Traduci in sardo: L'algoritmo di machine learning sta analizzando i dati."],
        cache_examples=False,
        chatbot=gr.Chatbot(
            avatar_images=[None, "https://huggingface.co/spaces/FPll/Limba_2.0/resolve/main/logo.png"], 
            height=500
        )
    )

if __name__ == "__main__":
    demo.launch(css=custom_css, ssr_mode=False)