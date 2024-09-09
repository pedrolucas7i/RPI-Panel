import subprocess

def obter_memoria_gpu():
    try:
        # Executa o comando vcgencmd para obter a memória da GPU
        resultado = subprocess.run(['vcgencmd', 'get_mem', 'gpu'], capture_output=True, text=True)
        memoria_gpu = resultado.stdout.strip()  # Remove espaços em branco adicionais
        # Remove a parte "gpu=" da string
        memoria_gpu = memoria_gpu.split('=')[1]
        return memoria_gpu
    except FileNotFoundError:
        return "vcgencmd não está instalado ou não é suportado"

memoria_gpu = obter_memoria_gpu()
print(f"{memoria_gpu}")
