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
dataset1 <-
  read_csv("Dati/Kaggle/archive/Environment_Temperature_change_E_All_Data_NOFLAG.csv")
# Leggi il file CSV escludendo le prime quattro righe
#Forest Area
dataset2 <-
  read_csv("Dati/WorldBank/API_AG/API_AG.LND.FRST.K2_DS2_en_csv_v2_47369.csv",
           skip = 4)
#Terreno irrigato
dataset3 <-
  read_csv("Dati/WorldBank/API_AG-2/API_AG.LND.IRIG.AG.ZS_DS2_en_csv_v2_48449.csv",
           skip = 4)
#Terreno arabile
dataset4 <-
  read_csv("Dati/WorldBank/API_AG-3/API_AG.LND.ARBL.ZS_DS2_en_csv_v2_43395.csv",
           skip = 4)
#Agricultural land (% of land area)
dataset5 <-
  read_csv("Dati/WorldBank/API_AG-4/API_AG.LND.AGRI.ZS_DS2_en_csv_v2_44906.csv",
           skip = 4)
#Average precipitation in depth (mm per year)
dataset6 <-
  read_csv("Dati/WorldBank/API_AG-5/API_AG.LND.PRCP.MM_DS2_en_csv_v2_356.csv",
           skip = 4)
#Renewable energy consumption (% of total final energy consumption)
dataset7 <-
  read_csv("Dati/WorldBank/API_EG/API_EG.FEC.RNEW.ZS_DS2_en_csv_v2_45401.csv",
           skip = 4)
#Alternative and nuclear energy (% of total energy use)
dataset8 <-
  read_csv("Dati/WorldBank/API_EG-3/API_EG.USE.COMM.CL.ZS_DS2_en_csv_v2_61892.csv",
           skip = 4)
#Electricity production from hydroelectric sources (% of total)
dataset9 <-
  read_csv("Dati/WorldBank/API_EG-4/API_EG.ELC.HYRO.ZS_DS2_en_csv_v2_51204.csv",
           skip = 4)
#Electricity production from nuclear sources (% of total)
dataset10 <-
  read_csv("Dati/WorldBank/API_EG-5/API_EG.ELC.NUCL.ZS_DS2_en_csv_v2_76135.csv",
           skip = 4)
#CO2 emissions (kt)
dataset11 <-
  read_csv("Dati/WorldBank/API_EN/API_EN.ATM.CO2E.KT_DS2_en_csv_v2_213077.csv",
           skip = 4)
#CO2 emissions (metric tons per capita)
dataset12 <-
  read_csv("Dati/WorldBank/API_EN-2/API_EN.ATM.CO2E.PC_DS2_en_csv_v2_47017.csv",
           skip = 4)
#Population living in areas where elevation is below 5 meters (% of total population)
dataset13 <-
  read_csv("Dati/WorldBank/API_EN-3/API_EN.POP.EL5M.ZS_DS2_en_csv_v2_44902.csv",
           skip = 4)
#Population in urban agglomerations of more than 1 million (% of total population
dataset14 <-
  read_csv("Dati/WorldBank/API_EN-4/API_EN.URB.MCTY.TL.ZS_DS2_en_csv_v2_450.csv",
           skip = 4)
#Total greenhouse gas emissions (kt of CO2 equivalent)
dataset15 <-
  read_csv("Dati/WorldBank/API_EN-5/API_EN.ATM.GHGT.KT.CE_DS2_en_csv_v2_45354.csv",
           skip = 4)
#Plant species (higher), threatened
dataset16 <-
  read_csv("Dati/WorldBank/API_EN-6/API_EN.HPT.THRD.NO_DS2_en_csv_v2_52000.csv",
           skip = 4)
#Fish species, threatened
dataset17 <-
  read_csv("Dati/WorldBank/API_EN-7/API_EN.FSH.THRD.NO_DS2_en_csv_v2_46041.csv",
           skip = 4)
#Bird species, threatened
dataset18 <-
  read_csv("Dati/WorldBank/API_EN-8/API_EN.BIR.THRD.NO_DS2_en_csv_v2_52306.csv",
           skip = 4)
#PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)
dataset19 <-
  read_csv("Dati/WorldBank/API_EN-9/API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_42623.csv",
           skip = 4)
#Methane emissions (kt of CO2 equivalent)
dataset20 <-
  read_csv("Dati/WorldBank/API_EN-10/API_EN.ATM.METH.KT.CE_DS2_en_csv_v2_49214.csv",
           skip = 4)
#Nitrous oxide emissions (thousand metric tons of CO2 equivalent)
dataset21 <-
  read_csv("Dati/WorldBank/API_EN-11/API_EN.ATM.NOXE.KT.CE_DS2_en_csv_v2_49217.csv",
           skip = 4)
#Droughts, floods, extreme temperatures (% of population, average 1990-2009)
dataset22 <-
  read_csv("Dati/WorldBank/API_EN-12/API_EN.CLC.MDAT.ZS_DS2_en_csv_v2_45415.csv",
           skip = 4)
#Disaster risk reduction progress score (1-5 scale; 5=best)
dataset23 <-
  read_csv("Dati/WorldBank/API_EN-13/API_EN.CLC.DRSK.XQ_DS2_en_csv_v2_50987.csv",
           skip = 4)
#GHG net emissions/removals by LUCF (Mt of CO2 equivalent)
dataset24 <-
  read_csv("Dati/WorldBank/API_EN-14/API_EN.CLC.GHGR.MT.CE_DS2_en_csv_v2_44848.csv",
           skip = 4)
#Terrestrial and marine protected areas (% of total territorial area)
dataset25 <-
  read_csv("Dati/WorldBank/API_ER/API_ER.PTD.TOTL.ZS_DS2_en_csv_v2_53310.csv",
           skip = 4)
#Renewable internal freshwater resources, total (billion cubic meters)
dataset26 <-
  read_csv("Dati/WorldBank/API_ER-2/API_ER.H2O.INTR.K3_DS2_en_csv_v2_44524.csv",
           skip = 4)
#Population growth (annual %)
dataset27 <-
  read_csv("Dati/WorldBank/API_SP/API_SP.POP.GROW_DS2_en_csv_v2_323.csv",
           skip = 4)


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
paesi_unici_dataset8 <- unique(dataset8$`Country Name`)
paesi_unici_dataset9 <- unique(dataset9$`Country Name`)
paesi_unici_dataset10 <- unique(dataset10$`Country Name`)
paesi_unici_dataset11 <- unique(dataset11$`Country Name`)
paesi_unici_dataset12 <- unique(dataset12$`Country Name`)
paesi_unici_dataset13 <- unique(dataset13$`Country Name`)
paesi_unici_dataset14 <- unique(dataset2$`Country Name`)
paesi_unici_dataset15 <- unique(dataset3$`Country Name`)
paesi_unici_dataset16 <- unique(dataset4$`Country Name`)
paesi_unici_dataset17 <- unique(dataset5$`Country Name`)
paesi_unici_dataset18 <- unique(dataset6$`Country Name`)
paesi_unici_dataset19 <- unique(dataset7$`Country Name`)
paesi_unici_dataset20 <- unique(dataset8$`Country Name`)
paesi_unici_dataset21 <- unique(dataset9$`Country Name`)
paesi_unici_dataset22 <- unique(dataset10$`Country Name`)
paesi_unici_dataset23 <- unique(dataset11$`Country Name`)
paesi_unici_dataset24 <- unique(dataset12$`Country Name`)
paesi_unici_dataset25 <- unique(dataset13$`Country Name`)
paesi_unici_dataset26 <- unique(dataset12$`Country Name`)
paesi_unici_dataset27 <- unique(dataset13$`Country Name`)
# Trova i paesi comuni nei tre dataset
paesi_comuni <-
  Reduce(
    intersect,
    list(
      paesi_unici_dataset,
      paesi_unici_dataset1,
      paesi_unici_dataset2,
      paesi_unici_dataset3,
      paesi_unici_dataset4,
      paesi_unici_dataset5,
      paesi_unici_dataset6,
      paesi_unici_dataset7,
      paesi_unici_dataset8,
      paesi_unici_dataset9,
      paesi_unici_dataset10,
      paesi_unici_dataset11,
      paesi_unici_dataset12,
      paesi_unici_dataset13,
      paesi_unici_dataset14,
      paesi_unici_dataset15,
      paesi_unici_dataset16,
      paesi_unici_dataset17,
      paesi_unici_dataset18,
      paesi_unici_dataset19,
      paesi_unici_dataset20,
      paesi_unici_dataset21,
      paesi_unici_dataset22,
      paesi_unici_dataset23,
      paesi_unici_dataset24,
      paesi_unici_dataset25,
      paesi_unici_dataset26,
      paesi_unici_dataset27
    )
  )

# Visualizza i paesi comuni
print(paesi_comuni)
