from leads.data_persistence import DataPersistence

fh = open("./test_data.csv", "a")
dp = DataPersistence(fh, max_size=4)

for i in range(1000):
    dp.append(i)
print(dp._chunk_size)
print(dp)
