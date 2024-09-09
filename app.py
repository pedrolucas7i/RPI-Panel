from flask import Flask, render_template, jsonify
import subprocess
import plotly.graph_objs as go
import time
import psutil

app = Flask(__name__)

# Lista para armazenar o histórico de temperaturas
temperature_history = []

def get_cpu_temperature():
    """Função para obter a temperatura do processador"""
    try:
        temp_output = subprocess.check_output(['vcgencmd', 'measure_temp']).decode('utf-8')
        temperature = float(temp_output.split('=')[1].split("'")[0])
        if temperature is not None:
               timestamp = time.strftime('%H:%M:%S')
               temperature_history.append((timestamp, temperature))
               if len(temperature_history) > 20:  # Limitar o histórico a 20 entradas
                     temperature_history.pop(0)
        return temperature
    except Exception as e:
        print(f"Erro ao obter a temperatura: {e}")
        return None

def get_cpu_name_lscpu():
    resultado = subprocess.run(['lscpu'], capture_output=True, text=True)
    for linha in resultado.stdout.splitlines():
        if 'Model name' in linha:
            return linha.split(': ')[1].strip()

def get_cpu_freq_psutil():
    return psutil.cpu_freq().current

def get_ram_psutil():
    mem_info = psutil.virtual_memory()
    return round(mem_info.total / (1024 ** 3), 2)

def get_used_ram_perc():
    resultado = subprocess.run(['free'], capture_output=True, text=True)
    linhas = resultado.stdout.splitlines()
    for linha in linhas:
        if 'Mem:' in linha:
            valores = linha.split()
            mem_total = int(valores[1])
            mem_usada = int(valores[2])
            return round((mem_usada / mem_total) * 100, 2)

def get_ram_process_psutil():
    processos = psutil.process_iter(['pid', 'memory_info'])
    num_processos = 0

    for processo in processos:
        try:
            if processo.info['memory_info'].rss > 0:  # Verifica se o processo está usando memória
                num_processos += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Ignora processos que foram terminados ou inacessíveis

    return num_processos

def get_gpu_mem():
    try:
        # Executa o comando vcgencmd para obter a memória da GPU
        resultado = subprocess.run(['vcgencmd', 'get_mem', 'gpu'], capture_output=True, text=True)
        memoria_gpu = resultado.stdout.strip()  # Remove espaços em branco adicionais
        # Remove a parte "gpu=" da string
        memoria_gpu = memoria_gpu.split('=')[1]
        return memoria_gpu
    except FileNotFoundError:
        return "vcgencmd não está instalado ou não é suportado"

def choose_gif(temperature):
    """Escolher o GIF com base na temperatura"""
    if temperature < 65:
        return "fan.gif"
    else:
        return "fan-high.gif"

@app.route('/')
def index():
    # Obter a temperatura atual
    temperature = get_cpu_temperature()
    cpu_name = get_cpu_name_lscpu()
    cpu_freq = str(str(get_cpu_freq_psutil()) + "MHz")
    ram = str(str(get_ram_psutil()) + "GB")
    used_ram = str(str(get_used_ram_perc()) + "%")
    ram_process = get_ram_process_psutil()
    gpu_mem = get_gpu_mem()

    # Escolher o GIF com base na temperatura
    gif_file = choose_gif(temperature) if temperature is not None else "fan.gif"

    return render_template('index.html', cpu_name=cpu_name, temperature=temperature, cpu_freq=cpu_freq, ram_quant=ram, ram_usage=used_ram, process=ram_process, gpu_mem=gpu_mem, gif_file=gif_file)

@app.route('/temperature-data')
def temperature_data():
    """Endpoint para retornar dados do gráfico"""
    # Separar o histórico em timestamps e temperaturas
    timestamps, temperatures = zip(*temperature_history) if temperature_history else ([], [])

    return jsonify({
        'timestamps': timestamps,
        'temperatures': temperatures
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
