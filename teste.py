from functions import make_heatmap, dirs2data
import time

folder = 'Samples/64c1852d8ef087ee1c0f6912'
inicio = time.time()
#test_heatmap(folder, type='eye')
data = dirs2data(folder)
fim = time.time()
print(fim - inicio)

print(data)