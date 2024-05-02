# Carica le librerie necessarie
library(dplyr)
library(readr)
library(mice)
library(zoo)
library(tidyr)

# Pulisci l'ambiente di lavoro
rm(list = ls())

# Imposta la directory di lavoro e leggi il file
dataset <- read_csv("Dati/Kaggle/Agrofood_co2_emission.csv")
dataset1 <- read_csv("Dati/Kaggle/archive/Environment_Temperature_change_E_All_Data_NOFLAG.csv")
# Leggi il file CSV escludendo le prime quattro righe
#Forest Area
dataset2 <- read_csv("Dati/WorldBank/API_AG/API_AG.LND.FRST.K2_DS2_en_csv_v2_47369.csv", skip = 4)
#Terreno irrigato
dataset3 <- read_csv("Dati/WorldBank/API_AG-2/API_AG.LND.IRIG.AG.ZS_DS2_en_csv_v2_48449.csv", skip = 4)
#Terreno arabile
dataset4 <- read_csv("Dati/WorldBank/API_AG-3/API_AG.LND.ARBL.ZS_DS2_en_csv_v2_43395.csv", skip = 4)
#Agricultural land (% of land area)
dataset5 <- read_csv("Dati/WorldBank/API_AG-4/API_AG.LND.AGRI.ZS_DS2_en_csv_v2_44906.csv", skip = 4)
#Average precipitation in depth (mm per year)
dataset6 <- read_csv("Dati/WorldBank/API_AG-5/API_AG.LND.PRCP.MM_DS2_en_csv_v2_356.csv", skip = 4)
#Renewable energy consumption (% of total final energy consumption)
dataset7 <- read_csv("Dati/WorldBank/API_EG/API_EG.FEC.RNEW.ZS_DS2_en_csv_v2_45401.csv", skip = 4)


print(unique(dataset2$`Country Name`))
print(unique(dataset3$`Country Name`))
print(unique(dataset$Area))
print(unique(dataset$Year))

# Controlla i valori nulli per ogni colonna
valori_nulli_per_colonna <- colSums(is.na(dataset))
print(valori_nulli_per_colonna)
print(dim(dataset))

print(unique(dataset1$Area))
print(unique(dataset1$Year))

# Controlla i valori nulli per ogni colonna
valori_nulli_per_colonna <- colSums(is.na(dataset1))
print(valori_nulli_per_colonna)
print(dim(dataset1))

# Trova i paesi unici nei tre dataset
paesi_unici_dataset <- unique(dataset$Area)
paesi_unici_dataset1 <- unique(dataset1$Area)
paesi_unici_dataset2 <- unique(dataset2$`Country Name`)
paesi_unici_dataset3 <- unique(dataset3$`Country Name`)
paesi_unici_dataset4 <- unique(dataset4$`Country Name`)
paesi_unici_dataset5 <- unique(dataset5$`Country Name`)
paesi_unici_dataset6 <- unique(dataset6$`Country Name`)
paesi_unici_dataset7 <- unique(dataset7$`Country Name`)
# Trova i paesi comuni nei tre dataset
paesi_comuni <- Reduce(intersect, list(paesi_unici_dataset, paesi_unici_dataset1,
                                       paesi_unici_dataset2, paesi_unici_dataset3,
                                       paesi_unici_dataset4, paesi_unici_dataset5,
                                       paesi_unici_dataset6))

# Visualizza i paesi comuni
print(paesi_comuni)
