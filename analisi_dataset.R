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



# Carica le librerie necessarie
library(dplyr)
library(readr)
library(tidyr)

# Funzione per rinominare le colonne chiave
rinomina_colonne <- function(df, country_col, year_col) {
  df %>%
    rename(Country = !!sym(country_col),
           Year = !!sym(year_col))
}

# Funzione per filtrare i dati per i paesi comuni
filtra_paesi_comuni <- function(df, paesi_comuni) {
  df %>%
    filter(Country %in% paesi_comuni)
}

# Rinomina le colonne chiave nei vari dataset
dataset <- rinomina_colonne(dataset, "Area", "Year")
dataset1 <- rinomina_colonne(dataset1, "Area", "Year")
dataset2 <- rinomina_colonne(dataset2, "Country Name", "Year")
dataset3 <- rinomina_colonne(dataset3, "Country Name", "Year")
dataset4 <- rinomina_colonne(dataset4, "Country Name", "Year")
dataset5 <- rinomina_colonne(dataset5, "Country Name", "Year")
dataset6 <- rinomina_colonne(dataset6, "Country Name", "Year")
dataset7 <- rinomina_colonne(dataset7, "Country Name", "Year")
dataset8 <- rinomina_colonne(dataset8, "Country Name", "Year")
dataset9 <- rinomina_colonne(dataset9, "Country Name", "Year")
dataset10 <- rinomina_colonne(dataset10, "Country Name", "Year")
dataset11 <- rinomina_colonne(dataset11, "Country Name", "Year")
dataset12 <- rinomina_colonne(dataset12, "Country Name", "Year")
dataset13 <- rinomina_colonne(dataset13, "Country Name", "Year")
dataset14 <- rinomina_colonne(dataset14, "Country Name", "Year")
dataset15 <- rinomina_colonne(dataset15, "Country Name", "Year")
dataset16 <- rinomina_colonne(dataset16, "Country Name", "Year")
dataset17 <- rinomina_colonne(dataset17, "Country Name", "Year")
dataset18 <- rinomina_colonne(dataset18, "Country Name", "Year")
dataset19 <- rinomina_colonne(dataset19, "Country Name", "Year")
dataset20 <- rinomina_colonne(dataset20, "Country Name", "Year")
dataset21 <- rinomina_colonne(dataset21, "Country Name", "Year")
dataset22 <- rinomina_colonne(dataset22, "Country Name", "Year")
dataset23 <- rinomina_colonne(dataset23, "Country Name", "Year")
dataset24 <- rinomina_colonne(dataset24, "Country Name", "Year")
dataset25 <- rinomina_colonne(dataset25, "Country Name", "Year")
dataset26 <- rinomina_colonne(dataset26, "Country Name", "Year")
dataset27 <- rinomina_colonne(dataset27, "Country Name", "Year")

# Trova i paesi comuni a tutti i dataset
paesi_comuni <- Reduce(intersect, list(
  unique(dataset$Country),
  unique(dataset1$Country),
  unique(dataset2$Country),
  unique(dataset3$Country),
  unique(dataset4$Country),
  unique(dataset5$Country),
  unique(dataset6$Country),
  unique(dataset7$Country),
  unique(dataset8$Country),
  unique(dataset9$Country),
  unique(dataset10$Country),
  unique(dataset11$Country),
  unique(dataset12$Country),
  unique(dataset13$Country),
  unique(dataset14$Country),
  unique(dataset15$Country),
  unique(dataset16$Country),
  unique(dataset17$Country),
  unique(dataset18$Country),
  unique(dataset19$Country),
  unique(dataset20$Country),
  unique(dataset21$Country),
  unique(dataset22$Country),
  unique(dataset23$Country),
  unique(dataset24$Country),
  unique(dataset25$Country),
  unique(dataset26$Country),
  unique(dataset27$Country)
))

# Filtra i dati per i paesi comuni
dataset <- filtra_paesi_comuni(dataset, paesi_comuni)
dataset1 <- filtra_paesi_comuni(dataset1, paesi_comuni)
dataset2 <- filtra_paesi_comuni(dataset2, paesi_comuni)
dataset3 <- filtra_paesi_comuni(dataset3, paesi_comuni)
dataset4 <- filtra_paesi_comuni(dataset4, paesi_comuni)
dataset5 <- filtra_paesi_comuni(dataset5, paesi_comuni)
dataset6 <- filtra_paesi_comuni(dataset6, paesi_comuni)
dataset7 <- filtra_paesi_comuni(dataset7, paesi_comuni)
dataset8 <- filtra_paesi_comuni(dataset8, paesi_comuni)
dataset9 <- filtra_paesi_comuni(dataset9, paesi_comuni)
dataset10 <- filtra_paesi_comuni(dataset10, paesi_comuni)
dataset11 <- filtra_paesi_comuni(dataset11, paesi_comuni)
dataset12 <- filtra_paesi_comuni(dataset12, paesi_comuni)
dataset13 <- filtra_paesi_comuni(dataset13, paesi_comuni)
dataset14 <- filtra_paesi_comuni(dataset14, paesi_comuni)
dataset15 <- filtra_paesi_comuni(dataset15, paesi_comuni)
dataset16 <- filtra_paesi_comuni(dataset16, paesi_comuni)
dataset17 <- filtra_paesi_comuni(dataset17, paesi_comuni)
dataset18 <- filtra_paesi_comuni(dataset18, paesi_comuni)
dataset19 <- filtra_paesi_comuni(dataset19, paesi_comuni)
dataset20 <- filtra_paesi_comuni(dataset20, paesi_comuni)
dataset21 <- filtra_paesi_comuni(dataset21, paesi_comuni)
dataset22 <- filtra_paesi_comuni(dataset22, paesi_comuni)
dataset23 <- filtra_paesi_comuni(dataset23, paesi_comuni)
dataset24 <- filtra_paesi_comuni(dataset24, paesi_comuni)
dataset25 <- filtra_paesi_comuni(dataset25, paesi_comuni)
dataset26 <- filtra_paesi_comuni(dataset26, paesi_comuni)
dataset27 <- filtra_paesi_comuni(dataset27, paesi_comuni)

# Unisci i dataset usando le colonne chiave "Country" e "Year"
dataset_unito <- dataset %>%
  full_join(dataset1, by = c("Country", "Year")) %>%
  full_join(dataset2, by = c("Country", "Year")) %>%
  full_join(dataset3, by = c("Country", "Year")) %>%
  full_join(dataset4, by = c("Country", "Year")) %>%
  full_join(dataset5, by = c("Country", "Year")) %>%
  full_join(dataset6, by = c("Country", "Year")) %>%
  full_join(dataset7, by = c("Country", "Year")) %>%
  full_join(dataset8, by = c("Country", "Year")) %>%
  full_join(dataset9, by = c("Country", "Year")) %>%
  full_join(dataset10, by = c("Country", "Year")) %>%
  full_join(dataset11, by = c("Country", "Year")) %>%
  full_join(dataset12, by = c("Country", "Year")) %>%
  full_join(dataset13, by = c("Country", "Year")) %>%
  full_join(dataset14, by = c("Country", "Year")) %>%
  full_join(dataset15, by = c("Country", "Year")) %>%
  full_join(dataset16, by = c("Country", "Year")) %>%
  full_join(dataset17, by = c("Country", "Year")) %>%
  full_join(dataset18, by = c("Country", "Year")) %>%
  full_join(dataset19, by = c("Country", "Year")) %>%
  full_join(dataset20, by = c("Country", "Year")) %>%
  full_join(dataset21, by = c("Country", "Year")) %>%
  full_join(dataset22, by = c("Country", "Year")) %>%
  full_join(dataset23, by = c("Country", "Year")) %>%
  full_join(dataset24, by = c("Country", "Year")) %>%
  full_join(dataset25, by = c("Country", "Year")) %>%
  full_join(dataset26, by = c("Country", "Year")) %>%
  full_join(dataset27, by = c("Country", "Year"))

# Esporta il dataset unito in un file CSV
write_csv(dataset_unito, "Dati/unione_dataset.csv")

print("Dataset unito e salvato con successo.")
