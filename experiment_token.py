import torch
import logging
import os

from transformers import GPT2LMHeadModel
from transformers import pipeline

# Path del modelo pre-entrenado.
model_path = "./runs/gpt2-modelset_token-256/best_model"

# Carga del modelo pre-entrenado.
model = GPT2LMHeadModel.from_pretrained(model_path)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Usamos la GPU si esta disponible.
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# Creamos un pipeline con el tipo de tarea que vamos a resolver
# y el path al modelo cargado.
# max_new_tokens para generar siempre 1 token mas.
# handle_long_generation = "hole" para que no haya problemas con lineas mayores de 1024 tokens, truncado automatico
generator = pipeline("text-generation", model=model_path, max_new_tokens=1, handle_long_generation="hole")

# Fichero donde guardamos las predicciones.
output_file = "predictions.txt"

# Fichero con el conjunto de test.
test_path = "./modelset_token/test.txt"

# Contador para saber por que frase vamos.
cnt = 0

# Abrimos el conjunto de test y el fichero para las predicciones.
with open(test_path, "r") as file, open(output_file, "w") as out_file:
    for line in file:
        cnt += 1
        tokens = line.split()
        out_tokens = "<s>"
        # Creamos todos los prefijos posibles (salvo la linea entera)
        words = line.split()
        #print("Empiezan predicciones:" + str(len(words)))
        # Creamos todos los prefijos posibles (salvo la linea entera)
        prefixes = [' '.join(words[:i + 1]) for i in range(len(words)-1)]
        # Predecimos un token por cada línea nueva.
        predictions = [generator(prefix)[0]['generated_text'].strip() for prefix in prefixes]

        # A veces se predicen 0 tokens. En ese caso, añado yo el token "NO PRED".
        for prefix, prediction in zip(prefixes, predictions):
            if len(prefix.split()) == len(prediction.split()):
                out_tokens += ' ' + 'NO_PRED'
            else:
                assert( len(prefix.split()) + 1 == len(prediction.split()) )
                out_tokens += ' ' + prediction.split()[-1]

        # Escribo en el fichero la predicción
        out_file.write(out_tokens + '\n')
        print("terminada frase: " + str(cnt))


